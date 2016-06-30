#!/usr/bin/python

# system-wide requirements
from flask import Flask, jsonify, render_template, request, redirect, url_for, make_response, flash
from flask.ext.httpauth import HTTPBasicAuth
from smart_m3.m3_kp_api import *
from smart_m3.m3_kp_api import Literal as LLiteral
from arrowheadlibs import *
from uuid import uuid4
import ConfigParser
import requests
import json

# importing models, controllers and views
from models.user import *
from models.vehicle import *
from models.reservation import *
from models.groundstation import *
from controllers.GroundStationsController import *
from controllers.ReservationsController import *
from controllers.VehiclesController import *
from controllers.UsersController import *
from controllers.AuthController import *

# importing other local libraries
from libs.traditional_bs_queries import *
from libs.n3loader import *
from libs.alfrest import *

# reading configuration
settings = {}
settingsParser = ConfigParser.ConfigParser()
settingsParser.readfp(open("otmbs.conf"))
settings["sib_host"] = settingsParser.get("sib", "host")
settings["sib_port"] = settingsParser.getint("sib", "port")
settings["flask_port"] = settingsParser.getint("flask", "port")
settings["flask_host"] = settingsParser.get("flask", "host")
settings["ah_enabled"] = settingsParser.getboolean("arrowhead", "enabled")
settings["ah_host"] = settingsParser.get("arrowhead", "host")
settings["ah_port"] = settingsParser.getint("arrowhead", "port")
settings["ah_service_domain"] = settingsParser.get("arrowhead", "service_domain")
settings["ah_service_host"] = settingsParser.get("arrowhead", "service_host")
settings["ah_service_name"] = settingsParser.get("arrowhead", "service_name")
settings["ah_service_port"] = settingsParser.getint("arrowhead", "service_port")
settings["ah_service_path"] = settingsParser.get("arrowhead", "service_path")
settings["ah_service_type"] = settingsParser.get("arrowhead", "service_type")
settings["block_size"] = settingsParser.getint("kb", "block_size")
settings["kb_files"] = []
for filename in settingsParser.get("kb", "kb_file").split("%"):
    settings["kb_files"].append(filename)

# loading the KB
loader = N3KBLoader(settings)
for filename in settings["kb_files"]:
    loader.load_n3file(filename)

# creating an instance of Flask
# and one of the authenticator
app = Flask(__name__)
auth = HTTPBasicAuth()

# creating an instance of each controller
reservations_controller = ReservationsController(settings)
gss_controller = GroundStationsController(settings)
vehicles_controller = VehiclesController(settings)
users_controller = UsersController(settings)
auth_controller = AuthController(settings)


################################################
#
# login methods
#
################################################

@auth.get_password
def get_password(username):

    """This is a callback used by the server to retrieve
    the password for a given username"""

    # invoke the auth controller
    res = auth_controller.get_password(username)

    # return
    return res


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@app.route('/logout', methods=['GET'])
def logout():
    
    # TODO: yet to implement!
    pass


################################################
#
# setting routes for static pages
#
################################################

@app.route('/', methods=['GET'])
def mainpage():

    return render_template("main.html", title="OTM Booking Service")


################################################
#
# setting routes for the vehicle controller
#
################################################

@app.route('/users/<user_id>/vehicles', methods=['GET'])
@auth.login_required
def users_vehicles(user_id):

    # invoke the controller
    res = vehicles_controller.show_vehicles(user_id)

    # select the proper output form
    try:
        if request.headers.has_key('Accept') and request.headers['Accept'] == 'application/json':
            return jsonify(results = res)
    except:
        pass
        
    try:
        if request.args.has_key('format') and request.args['format'] == "json":
            return jsonify(results = res)
    except:
        pass

    return render_template("show_vehicles.html", title="Vehicles", entries=res)


@app.route('/vehicles', methods=['GET'])
def vehicles_showall():

    # check if the user_id is given
    user_id = None
    if request.args.has_key('user_id'):
        user_id = request.args['user_id']

    # invoke the controller
    res = vehicles_controller.show_vehicles(user_id)

    # select the proper output form
    try:
        if request.headers.has_key('Accept') and request.headers['Accept'] == 'application/json':
            return jsonify(results = res)
    except:
        pass
        
    try:
        if request.args.has_key('format') and request.args['format'] == "json":
            return jsonify(results = res)
    except:
        pass

    return render_template("show_vehicles.html", title="Vehicles", entries=res)


@app.route('/vehicles/<vehicle_id>', methods=['GET'])
def vehicles_show(vehicle_id):

    # invoke the controller
    res = vehicles_controller.show_vehicle(vehicle_id)

    # select the proper output form
    try:
        if request.headers.has_key('Accept') and request.headers['Accept'] == 'application/json':
            return jsonify(results = res)
    except:
        pass
        
    try:
        if request.args.has_key('format') and request.args['format'] == "json":
            return jsonify(results = res)
    except:
        pass

    return render_template("show_vehicle.html", entry=res, title="Vehicle details")


@app.route('/vehicles/<vehicle_id>/edit', methods=['GET'])
def vehicles_edit(vehicle_id):

    # get all the available users to fill a combo in the view
    users_list = users_controller.show_users()

    # get the vehicle to modify
    vehicle = vehicles_controller.show_vehicle(vehicle_id)

    # render the html form
    return render_template("edit_vehicle.html", users=users_list, vehicle=vehicle, title="Edit vehicle")


@app.route('/vehicles/<vehicle_id>', methods=['PUT'])
@app.route('/vehicles/update/<vehicle_id>', methods=['POST'])
def vehicles_update(vehicle_id):

    # verify if the payload is json
    try:
        if request.content_type == "application/json":
            data = json.loads(request.data)
            model = data["model"]
            manufacturer = data["manufacturer"]
            user_uid = data["user_uid"]
            
            # invoke the controller
            status, vehicle = vehicles_controller.update_vehicle(vehicle_id, manufacturer, model, user_uid)

            # redirect to the index
            return jsonify(results = vehicle)

    except Exception as e:
        print e
        pass

    # read the form
    vehicle_model = request.form["model"]
    vehicle_user_id = request.form["user_uid"]
    vehicle_manufacturer = request.form["manufacturer"]

    # invoke the controller
    res, newmodel = vehicles_controller.update_vehicle(vehicle_id, vehicle_manufacturer, vehicle_model, vehicle_user_id)

    # redirect to the index
    return redirect("/vehicles/%s" % newmodel["vehicle_id"])


@app.route('/vehicles/new', methods=['GET'])
def vehicles_new():

    # get all the available users to fill a combo in the view
    users_list = users_controller.show_users()

    # render the html form
    return render_template("new_vehicle.html", users=users_list, title="New Vehicle")


@app.route('/vehicles', methods=['POST'])
@auth.login_required
def vehicles_create():
    
    # verify if the payload is json
    try:
        if request.content_type == "application/json":
            data = json.loads(request.data)
            model = data["model"]
            manufacturer = data["manufacturer"]
            user_uid = data["user_uid"]
            
            # invoke the controller
            status, vehicle = vehicles_controller.create_vehicle(manufacturer, model, user_uid)

            # redirect to the index
            return jsonify(results = vehicle)

    except Exception as e:
        print e
        pass

    # invoke the controller
    status, vehicle = vehicles_controller.create_vehicle(request.form["manufacturer"], request.form["model"], request.form["user_uid"])

    # redirect to the index
    return redirect("/vehicles/%s" % vehicle["vehicle_id"])


@app.route('/vehicles/delete/<vehicle_id>', methods=['GET'])
@app.route('/vehicles/<vehicle_id>', methods=['DELETE'])
# @auth.login_required
def vehicles_delete(vehicle_id):
    
    # invoke the controller
    res = vehicles_controller.delete_vehicle(vehicle_id)
    
    # select the proper output form
    try:
        if request.headers.has_key('Accept') and request.headers['Accept'] == 'application/json':
            if res:
                return make_response(jsonify({'OK': 'Vehicle Deleted'}), 200)        
            else:
                return make_response(jsonify({'error': 'Vehicle not Deleted'}), 401)
    except:
        pass
        
    try:
        if request.args.has_key('format') and request.args['format'] == "json":
            if res:
                return make_response(jsonify({'OK': 'Vehicle Deleted'}), 200)        
            else:
                return make_response(jsonify({'error': 'Vehicle not Deleted'}), 401)
    except:
        pass
    
    # redirect to the index
    return redirect("/vehicles")


################################################
#
# setting routes for the user controller
#
################################################

@app.route('/users', methods=['GET'])
def users_showall():

    # invoke the controller
    res = users_controller.show_users()

    # select the proper output form
    try:
        if request.headers.has_key('Accept') and request.headers['Accept'] == 'application/json':
            return jsonify(results = res)
    except:
        pass
        
    try:
        if request.args.has_key('format') and request.args['format'] == "json":
            return jsonify(results = res)
    except:
        pass

    return render_template("show_users.html", entries=res, title="Users")


@app.route('/users/<user_id>', methods=['GET'])
def users_show(user_id):


    # invoke the controller
    res = users_controller.show_user(user_id)

    # select the proper output form
    try:
        if request.headers.has_key('Accept') and request.headers['Accept'] == 'application/json':
            return jsonify(results = res)
    except:
        pass
        
    try:
        if request.args.has_key('format') and request.args['format'] == "json":
            return jsonify(results = res)
    except:
        pass

    return render_template("show_user.html", entry=res, title="User details")


@app.route('/users/delete/<user_id>', methods=['GET'])
@app.route('/users/<user_id>', methods=['DELETE'])
# @auth.login_required
def users_delete(user_id):
    
    # invoke the controller
    res = users_controller.delete_user(user_id)
    
    # redirect to the index
    return redirect(url_for("users_showall"))


@app.route('/users/<user_id>/edit', methods=['GET'])
def users_edit(user_id):

    # retrieve the user
    user = users_controller.show_user(user_id)

    # render the html form
    return render_template("edit_user.html", user=user, title="Edit user")


@app.route('/users/new', methods=['GET'])
def users_new():

    # render the html form
    return render_template("new_user.html", title="New User")


@app.route('/users', methods=['POST'])
def users_create():
        
    # verify if the payload is json
    try:
        if request.content_type == "application/json":
            data = json.loads(request.data)
            print data
            print data.keys()
            name = data["name"]
            nick = data["nickname"]
            passwd = data["password"]
            
            # invoke the controller
            status, user = users_controller.create_user(name, nick, passwd)

            # if OK
            if status:
                return jsonify(results = user)

            else:
                return make_response(jsonify({'error': 'Nickname already taken'}), 406)

    except Exception as e:
        print e
        pass

    # invoke the controller
    status, user = users_controller.create_user(request.form["name"], request.form["nickname"], request.form["password"])

    # redirect to the index
    if status:
        return redirect("/users/%s" % user["user_uid"])
    else:
        return redirect("/users")


@app.route('/users/<user_id>', methods=['PUT'])
@app.route('/users/update/<user_id>', methods=['POST'])
def users_update(user_id):
        
    # verify if the payload is json
    try:
        if request.content_type == "application/json":
            data = json.loads(request.data)
            name = data["name"]
            passwd = data["password"]
            
            # invoke the controller
            status, user = users_controller.update_user(user_id, name, passwd)

            # redirect to the index
            return jsonify(results = user)

    except Exception as e:
        print e
        pass

    # invoke the controller
    status, user = users_controller.update_user(user_id, request.form["name"], request.form["password"])

    # redirect to the index
    return redirect("/users/%s" % user["user_uid"])


################################################
#
# setting routes for the groundstation controller
#
################################################

@app.route('/groundstations', methods=['GET'])
def gss_showall():
    
    # get the list of the ground stations
    res = gss_controller.show_gss()

    # select the proper output form
    try:
        if request.headers.has_key('Accept') and request.headers['Accept'] == 'application/json':
            return jsonify(results = res)
    except:
        pass
        
    try:
        if request.args.has_key('format') and request.args['format'] == "json":
            return jsonify(results = res)
    except:
        pass

    return render_template("show_gss.html", gss = res, title="GroundStations")


@app.route('/groundstations/<gs_id>', methods=['GET'])
def gss_show(gs_id):
 
    # get the list of the ground stations
    gs = gss_controller.show_gs(gs_id)

    # select the proper output form
    try:
        if request.headers.has_key('Accept') and request.headers['Accept'] == 'application/json':
            return jsonify(results = gs)
    except:
        pass
        
    try:
        if request.args.has_key('format') and request.args['format'] == "json":
            return jsonify(results = gs)
    except:
        pass
    
    return render_template("show_gs.html", entry = gs, title="GroundStation details")


@app.route('/groundstations/new', methods=['GET'])
def gss_new():

    # render the html form
    return render_template("new_gs.html", title="New GroundStation")


@app.route('/groundstations', methods=['POST'])
def gss_create():
    
    # verify if the payload is json
    try:
        if request.content_type == "application/json":

            # extract data
            data = json.loads(request.data)
            slat = data["slatitude"]
            slong = data["slongitude"]
            elat = data["elatitude"]
            elong = data["elongitude"]
            name = data["name"]

            # invoke the controller
            status, gs = gss_controller.create_gs(name, slat, slong, elat, elong)

            # redirect to the index
            return jsonify(results = gs)

    except Exception as e:
        print e
        pass

    # invoke the controller
    status, gs = gss_controller.create_gs(request.form["name"], 
                                          request.form["slatitude"], request.form["slongitude"], 
                                          request.form["elatitude"], request.form["elongitude"])

    # redirect to the index
    return redirect("/groundstations")


@app.route('/groundstations/delete/<gs_id>', methods=['GET'])
@app.route('/groundstations/<gs_id>', methods=['DELETE'])
# @auth.login_required
def gss_delete(gs_id):
    
    # invoke the controller
    res = gss_controller.delete_gs(gs_id)
    
    # redirect to the index
    # return redirect("/groundstations", methods=['GET'])
    return redirect(url_for("gss_showall"))


@app.route('/groundstations/<gs_id>/edit', methods=['GET'])
def gss_edit(gs_id):

    # invoke the controller in order to retrieve
    # the gs that should be modified
    res = gss_controller.show_gs(gs_id)

    # now render the edit template with the field
    # filled with the previous results
    return render_template("edit_gs.html", gs=res, title="Edit GroundStation")


@app.route('/groundstations/<gs_id>', methods=['PUT'])
@app.route('/groundstations/update/<gs_id>', methods=['POST'])
def gss_update(gs_id):
    
    # verify if the payload is json
    try:
        if request.content_type == "application/json":

            # extract data
            data = json.loads(request.data)
            slat = data["slatitude"]
            slong = data["slongitude"]
            elat = data["elatitude"]
            elong = data["elongitude"]
            name = data["name"]

            # invoke the controller
            status, gs = gss_controller.update_gs(gs_id, name, slat, slong, elat, elong)

            # redirect to the index
            return jsonify(results = gs)

    except Exception as e:
        print e
        pass

    # read the form
    gs_name = request.form["name"]
    gs_slat = request.form["slatitude"]
    gs_elat = request.form["elatitude"]
    gs_slong = request.form["slongitude"]
    gs_elong = request.form["elongitude"]

    # invoke the controller
    res, newmodel = gss_controller.update_gs(gs_id, gs_name, gs_slat, gs_slong, gs_elat, gs_elong)

    # redirect to the index
    return redirect("/groundstations/%s" % newmodel["gs_id"])


################################################
#
# setting routes for the reservation controller
#
################################################

@app.route('/reservations', methods=['GET'])
def reservations_check():

    # check if a gs is reserved
    try:
        if request.content_type == "application/json":
            data = json.loads(request.data)
            gs_id = data["gs_id"]
            vehicle_id = data["vehicle_id"]
            user_id = data["user_id"]    

            # invoke the controller
            status = reservations_controller.check_reservation(gs_id, vehicle_id,  user_id)

            # return
            if res:
                return make_response(jsonify({'OK': 'Valid Reservation'}), 200)        
            else:
                return make_response(jsonify({'error': 'Reservation not found'}), 404)

    except Exception as e:
        print e
        return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route('/reservations', methods=['GET'])
def reservations_showall():

    # check if the user_id was given
    user_id = None
    if request.args.has_key('user_id'):
        user_id = request.args['user_id']

    # invoking the controller
    res = reservations_controller.show_reservations(user_id)

    # select the proper output form
    try:
        if request.headers.has_key('Accept') and request.headers['Accept'] == 'application/json':
            return jsonify(results = res)
    except:
        pass
        
    try:
        if request.args.has_key('format') and request.args['format'] == "json":
            return jsonify(results = res)
    except:
        pass

    return render_template("show_reservations.html", entries=res, title="Reservations")
    

@app.route('/users/<user_id>/reservations', methods=['GET'])
@auth.login_required
def user_reservations(user_id):

    # invoking the controller
    res = reservations_controller.show_reservations(user_id)

    # select the proper output form
    try:
        if request.headers.has_key('Accept') and request.headers['Accept'] == 'application/json':
            return jsonify(results = res)
    except:
        pass
        
    try:
        if request.args.has_key('format') and request.args['format'] == "json":
            return jsonify(results = res)
    except:
        pass

    return render_template("show_reservations.html", entries=res, title="Reservations")


@app.route('/reservations/<reservation_id>', methods=['GET'])
def reservations_show(reservation_id):
    
    # invoking the controller
    res = reservations_controller.show_reservation(reservation_id)

    # select the proper output form
    try:
        if request.headers.has_key('Accept') and request.headers['Accept'] == 'application/json':
            return jsonify(results = res)
    except:
        pass
        
    try:
        if request.args.has_key('format') and request.args['format'] == "json":
            return jsonify(results = res)
    except:
        pass

    return render_template("show_reservation.html", entry = res, title="Reservation details")


@app.route('/reservations/delete/<reservation_id>', methods=['GET'])
@app.route('/reservations/<reservation_id>', methods=['DELETE'])
# @auth.login_required
def reservations_delete(reservation_id):
    
    # invoke the controller
    res = reservations_controller.delete_reservation(reservation_id)
    
    # select the proper output form
    try:
        if request.headers.has_key('Accept') and request.headers['Accept'] == 'application/json':
            if res:
                return make_response(jsonify({'OK': 'Reservation Retired'}), 200)        
            else:
                return make_response(jsonify({'error': 'Reservation not retired'}), 401)
    except:
        pass
        
    try:
        if request.args.has_key('format') and request.args['format'] == "json":
            if res:
                return make_response(jsonify({'OK': 'Reservation Retired'}), 200)        
            else:
                return make_response(jsonify({'error': 'Reservation not retired'}), 401)
    except:
        pass

    # redirect to the index
    return redirect(url_for("reservations_showall"))


@app.route('/reservations/new', methods=['GET'])
def reservations_new():

    # get all the available ground stations
    gss_list = gss_controller.show_gss()

    # get all the available vehicles
    vehicles_list = vehicles_controller.show_vehicles()
    
    # check if a ground station was already selected
    if request.args.has_key('gs_id'):
        gs_id = request.args["gs_id"]
    else:
        gs_id = None

    # render the html form
    return render_template("new_reservation.html", gss=gss_list, vehicles=vehicles_list, title="New Reservation", selected_gs = gs_id)


@app.route('/reservations', methods=['POST'])
def reservations_create():

    # verify if the payload is json
    try:
        if request.content_type == "application/json":
            data = json.loads(request.data)
            gs_id = data["gs_id"]
            vehicle_id = data["vehicle_id"]
            user_id = data["user_id"]    

            # invoke the controller
            status, reservation = reservations_controller.create_reservation(gs_id, vehicle_id,  user_id)

            # redirect to the index
            return jsonify(results = reservation)

    except Exception as e:
        print e
        pass

    # invoke the controller
    vehicle_id = request.form["user_car"].split("|")[0]
    user_id = request.form["user_car"].split("|")[1] 
    status, res = reservations_controller.create_reservation(request.form["gs"], vehicle_id, user_id)

    # redirect to the index
    return redirect("/reservations/%s" % res["reservation_id"])


@app.route('/reservations/<reservation_id>/edit', methods=['GET'])
def reservations_edit(reservation_id):

    # get all the available ground stations
    gss_list = gss_controller.show_gss()

    # get all the available vehicles
    vehicles_list = vehicles_controller.show_vehicles()

    # get the current reservation
    res = reservations_controller.show_reservation(reservation_id)    

    # render the html form
    return render_template("edit_reservation.html", gss=gss_list, vehicles=vehicles_list, reservation = res, title="Edit reservation")


@app.route('/reservations/<reservation_id>', methods=['PUT'])
@app.route('/reservations/update/<reservation_id>', methods=['POST'])
def reservations_update(reservation_id):

    # verify if the payload is json
    try:
        if request.content_type == "application/json":
            data = json.loads(request.data)
            gs_id = data["gs_id"]
            vehicle_id = data["vehicle_id"]
            user_id = data["user_id"]    

            # invoke the controller
            status, reservation = reservations_controller.update_reservation(reservation_id, gs_id, vehicle_id,  user_id)

            # redirect to the index
            return jsonify(results = reservation)

    except Exception as e:
        print e
        pass

    # invoke the controller
    vehicle_id = request.form["user_car"].split("|")[0]
    user_id = request.form["user_car"].split("|")[1] 
    status, res = reservations_controller.update_reservation(reservation_id, request.form["gs"], vehicle_id, user_id)

    # redirect to the index
    return redirect("/reservations/%s" % res["reservation_id"])


################################################
#
# Traditional Booking Service Interface
#
################################################

@app.route('/bs/users', methods=['GET'])
def users():

    """Returns the list of the users of the booking service.
    The default data format for the results is JSON."""

    # get the user list
    kp = m3_kp_api(False, settings["sib_host"], settings["sib_port"])
    kp.load_query_sparql(users_query)
    results = kp.result_sparql_query
    
    # parse the results
    users = []
    for result in results:
        user = {}
        user["uri"] = result[0][2]
        user["name"] = result[1][2]
        user["id"] = result[2][2]
        users.append(user)

    # return
    return jsonify(results = users)


@app.route('/bs/vehicles', methods=['GET'])
def vehicles():

    """Returns the list of vehicles. Default
    data format for the results is JSON.
    Note: the user_id must be provided. """

    # check if the user_id was provided user_id = None if
    if request.args.has_key('user_id'):

        # read the user_id
        user_id = request.args['user_id']

        # get the vehicle list
        kp = m3_kp_api(False, settings["sib_host"], settings["sib_port"])
        print vehicles_query % user_id
        kp.load_query_sparql(vehicles_query % user_id)
        results = kp.result_sparql_query

        # parse the results
        vehicles = []
        for result in results:
            vehicle = {}
            for field in result:
                vehicle[field[0]] = field[2]
            vehicles.append(vehicle)

    else:
         return make_response(jsonify({'error': 'Bad Request - The user_id must be provided'}), 401)

    # return
    return jsonify(results = vehicles)


@app.route('/bs/gcps', methods=['GET'])
def gcps():

    """Returns the list of GCPs. Default
    data format for the results is JSON."""

    # get the list of gcps
    kp = m3_kp_api(False, settings["sib_host"], settings["sib_port"])
    print gcps_query 
    kp.load_query_sparql(gcps_query)
    results = kp.result_sparql_query
    
    # parse the results
    gcps = []
    for result in results:
        gcp = {}
        for field in result:
            gcp[field[0]] = field[2]
        gcps.append(gcp)
                
    # return
    return jsonify(results = gcps)


@app.route('/bs/evses', methods=['GET'])
def evses():

    """Returns the list of evses. Default
    data format for the results is JSON.
    Note: the gcp_name must be provided. """

    # check if the user_id was provided user_id = None if
    if request.args.has_key('gcp_name'):

        # read the user_id
        gcp_name = request.args['gcp_name']

        # get the evse list
        kp = m3_kp_api(False, settings["sib_host"], settings["sib_port"])
        print evses_query % gcp_name
        kp.load_query_sparql(evses_query % gcp_name)
        results = kp.result_sparql_query

        # parse the results
        evses = []
        for result in results:
            evse = {}
            for field in result:
                evse[field[0]] = field[2]
            evses.append(evse)

    else:
         return make_response(jsonify({'error': 'Bad Request - The gcp_name must be provided'}), 401)

    # return
    return jsonify(results = evses)


@app.route('/bs/reservations', methods=['GET'])
@auth.login_required
def reservations():

    """Returns the list of reservations for
    a given user. JSON output."""

    # check if the user_id was provided user_id = None if
    if request.args.has_key('user_id'):

        # read the user_id
        user_id = request.args['user_id']

        # get the reservation list
        kp = m3_kp_api(False, settings["sib_host"], settings["sib_port"])
        print reservations_query % user_id
        kp.load_query_sparql(reservations_query % user_id)
        results = kp.result_sparql_query

        # parse the results
        reservations = []
        for result in results:
            reservation = {}
            for field in result:
                reservation[field[0]] = field[2]
            reservations.append(reservation)

    else:
         return make_response(jsonify({'error': 'Bad Request - The user_id must be provided'}), 401)

    # return
    return jsonify(results = reservations)
    

@app.route('/bs/chargerequests', methods=['GET'])
@auth.login_required
def charge_request():

    # read form data
    try:
        data = request.args
        print data
        lat = data["lat"]
        lng = data["lon"]
        rad = data["radius"]
        timeto = data["timeto"]
        timefrom = data["timefrom"]
        user_uri = NS + data["user_uri"]
        vehicle_uri = NS + data["vehicle_uri"]
        bidirectional = data["bidirectional"]
        requested_energy = data["requested_energy"]
    except Exception as e:
        print "ECCEXIONE:" + str(e)
        print e
    
    # generate UUIDs
    request_uri = NS + str(uuid4())
    time_interval_uri = NS + str(uuid4())
    energy_uri = NS + str(uuid4())
    spatial_range_uri = NS + str(uuid4())

    # insert
    triple_list = []
    triple_list.append(Triple(URI(request_uri), URI(RDF_TYPE), URI(NS + "ChargeRequest")))
    triple_list.append(Triple(URI(request_uri), URI(NS + "hasRequestingVehicle"), URI(vehicle_uri)))
    triple_list.append(Triple(URI(request_uri), URI(NS + "hasRequestingUser"), URI(user_uri)))
    triple_list.append(Triple(URI(request_uri), URI(NS + "allowBidirectional"), LLiteral("true")))
    triple_list.append(Triple(URI(time_interval_uri), URI(RDF_TYPE), URI(NS + "TimeInterval")))
    triple_list.append(Triple(URI(request_uri), URI(NS + "hasTimeInterval"), URI(time_interval_uri)))
    triple_list.append(Triple(URI(time_interval_uri), URI(NS + "hasFromTimeMillisec"), LLiteral(str(timefrom))))
    triple_list.append(Triple(URI(time_interval_uri), URI(NS + "hasToTimeMillisec"), LLiteral(timeto)))
    triple_list.append(Triple(URI(energy_uri), URI(RDF_TYPE), URI(NS + "EnergyData")))
    triple_list.append(Triple(URI(request_uri), URI(NS + "hasRequestedEnergy"), URI(energy_uri)))
    triple_list.append(Triple(URI(energy_uri), URI(NS + "hasUnitOfMeasure"), URI(NS + "kiloWattHour")))
    triple_list.append(Triple(URI(energy_uri), URI(NS + "hasValue"), LLiteral(requested_energy)))
    triple_list.append(Triple(URI(spatial_range_uri), URI(RDF_TYPE), URI(NS + "SpatialRangeData")))
    triple_list.append(Triple(URI(request_uri), URI(NS + "hasSpatialRange"), URI(spatial_range_uri)))
    triple_list.append(Triple(URI(spatial_range_uri), URI(NS + "hasGPSLatitude"), LLiteral(lat)))
    triple_list.append(Triple(URI(spatial_range_uri), URI(NS + "hasGPSLongitude"), LLiteral(lng)))
    triple_list.append(Triple(URI(spatial_range_uri), URI(NS + "hasRadius"), LLiteral(rad)))
    kp = m3_kp_api(False, settings["sib_host"], settings["sib_port"])
    kp.load_rdf_insert(triple_list)

    # query (instead of subscription)
    results = False
    while not results:
        
        # perform the query
        kp.load_query_rdf(Triple(None, URI(NS + "hasRelatedRequest"), URI(request_uri)))
        query_results = kp.result_rdf_query
        if len(query_results) > 0:
            results = query_results

    # query:
    res_uri = results[0][0]
    print res_uri
    print chargeresponse_query % (res_uri, res_uri)
    kp.load_query_sparql(chargeresponse_query % (res_uri, res_uri))
    charge_requests = []
    results2 = kp.result_sparql_query
    
    # parse the results
    charge_requests = []
    for result in results2:
        charge_request = {}
        for field in result:
            charge_request[field[0]] = field[2]
        charge_requests.append(charge_request)

    # return
    # TODO: gestire caso d'errore
    return jsonify(results = charge_requests)


@app.route("/bs/chargeoption_confirm", methods=["GET"])
def confirm_chargeoption():

    # read form data
    try:
        data = request.args
        charge_option = data["option"]
    except Exception as e:
        print "ECCEXIONE:" + str(e)
        print e

    # insert the triple
    kp = m3_kp_api(False, settings["sib_host"], settings["sib_port"])
    kp.load_rdf_insert([Triple(URI(NS + charge_option), URI(NS + "confirmByUser"), LLiteral("true"))])

    # look for system confirm
    # (subscription replaced by iterative query)
    results = None
    while not results:
        kp.load_query_rdf(Triple(URI(NS + charge_option), URI(NS + "confirmBySystem"), None))        
        results = kp.result_rdf_query
    sysconfirm = results[0][2]

    # send ACK
    if str(sysconfirm).lower() == "true":
        kp.load_rdf_insert([Triple(URI(NS + charge_option), URI(NS + "ackByUser"), LLiteral("true"))])
        return make_response(jsonify({'OK': 'Reservation confirmed'}), 200)        
    else:
        return make_response(jsonify({'error': 'Reservation Not confirmed'}), 401)


@app.route("/bs/reservations/<res_id>", methods=["DELETE"])
def reservation_retire(res_id):

    # initialize the return value
    success = True

    # connect to the SIB
    try:
        kp = m3_kp_api(False, settings["sib_host"], settings["sib_port"])

        # get the res_uri
        res_uri = NS + res_id
        
        # generate a reservation retire uri
        res_ret_uri = NS + str(uuid4())

        # get the reservation user
        kp.load_query_rdf(Triple(URI(res_uri), URI(NS + "reservationHasUser"), None))
        query_results = kp.result_rdf_query
        user_uri = query_results[0][2]

        # build the triple list
        triple_list = []
        triple_list.append(Triple(URI(res_ret_uri), URI(RDF_TYPE), URI(NS + "ReservationRetire")))
        triple_list.append(Triple(URI(res_ret_uri), URI(NS + "retiredByUser"), URI(user_uri)))
        triple_list.append(Triple(URI(res_ret_uri), URI(NS + "retiredReservation"), URI(res_uri)))
        
        # insert the reservation retire request
        kp.load_rdf_insert(triple_list)

    except:
    
        # no success :'(
        success = False
    
    # send ACK
    if success:
        return make_response(jsonify({'OK': 'Reservation Retired'}), 200)        
    else:
        return make_response(jsonify({'error': 'Reservation Not Retired'}), 401)


################################################
#
# TODO -- alfred non-rest interface
#
################################################
@app.route('/alfred', methods=['GET', 'POST'])
def alfred_routes():

    print "***********************************************************"
    print request.args
    print "***********************************************************"
    print request.form
    print "***********************************************************"

    # variables
    action = None
    data_format = None
    resource_id = None
    form_parameters = None

    # retrieve the desired action, if present
    if request.args.has_key('action'):    
        action = request.args["action"]

    # retrieve the desired data format, if present
    if request.args.has_key('format'):
        data_format = request.args["format"]

    # retrieve the id, if present
    if request.args.has_key('id'):
        resource_id = request.args["id"]

    # then call the proper action
    # TODO: this is not complete
    # TODO: optional arguments must be considered
    # TODO: only GET are ok
    if ALF_ACTIONS[action]["method"] == "GET":

        # vehicle related request 
        if action in ["showvehicles", "showvehicle", "deletevehicle"]:
            return redirect(url_for(ALF_ACTIONS[action]["name"], vehicle_id = resource_id, format = data_format))

        # user related request
        if action in ["showusers", "showuser", "deleteuser"]:
            return redirect(url_for(ALF_ACTIONS[action]["name"], user_id = resource_id, format = data_format))

        # gss related request
        if action in ["showgss", "showgs", "deletegs"]:
            return redirect(url_for(ALF_ACTIONS[action]["name"], gs_id = resource_id, format = data_format))

        # reservations related request
        if action in ["showreservations", "showreservation", "deletereservation"]:
            return redirect(url_for(ALF_ACTIONS[action]["name"], reservation_id = resource_id, format = data_format))

    else:

        # JSON form
        json_data = {}
        for k in request.args.keys():
            json_data[k] = request.args[k]

        # TODO: implement post!
        pass


# main
if __name__ == '__main__':


    # arrowhead interaction
    if settings["ah_enabled"]:
        ah = ArrowheadClient(settings["ah_host"], settings["ah_port"])
        res = ah.publish(settings["ah_service_domain"],
                         settings["ah_service_host"],
                         settings["ah_service_name"],
                         str(settings["ah_service_port"]),
                         {"path":settings["ah_service_path"]},
                         settings["ah_service_type"])
        if not res:
            print "Arrowhead registration failed!"
        else:
            print "Arrowhead service registered!"
    
    # start the server
    try:
        app.run(debug = True, host = settings["flask_host"], port = settings["flask_port"])
    except KeyboardInterrupt:
        res = ah.unpublish(settings["ah_service_host"], settings["ah_service_name"], str(settings["ah_service_port"]), settings["ah_service_type"])
        if not res:
            print "Arrowhead service not retired"
        else:
            print "Arrowhead service retired"

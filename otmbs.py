#!/usr/bin/python

# system-wide requirements
from flask import Flask, jsonify, render_template, request, redirect, url_for, make_response, flash
from flask.ext.httpauth import HTTPBasicAuth
from smart_m3.m3_kp_api import *
from smart_m3.m3_kp_api import Literal as LLiteral
from termcolor import colored
from arrowheadlibs import *
from uuid import uuid4
import ConfigParser
import traceback
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
from controllers.TradController import *

# importing other local libraries
from libs.traditional_bs_queries import *
from libs.otmbs_constants import *
from libs.utilities import *
from libs.n3loader import *

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
trad_controller = TradController(settings)

################################################
#
# login methods
#
################################################

@auth.get_password
def get_password(username):

    """This is a callback used by the server to retrieve
    the password for a given username"""

    res = auth_controller.get_password(username)
    return res


@auth.error_handler
def unauthorized():

    print colored("main> ", "red", attrs=["bold"]) + " Unauthorized access!"
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


################################################
#
# setting routes for static pages
#
################################################

@app.route('/', methods=['GET'])
def mainpage():
    return render_template("main.html", title="ElectroMobility Booking Service")


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
    if output_format(request) == JSON:
        return jsonify(results = res)
    else:
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
    if output_format(request) == JSON:
        return jsonify(results = res)
    else:    
        return render_template("show_vehicles.html", title="Vehicles", entries=res)


@app.route('/vehicles/<vehicle_id>', methods=['GET'])
def vehicles_show(vehicle_id):

    # invoke the controller
    res = vehicles_controller.show_vehicle(vehicle_id)

    # select the proper output form
    if output_format(request) == JSON:
        return jsonify(results = res)
    else:
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

    # input
    if input_format(request) == JSON:
        data = get_input_data(request)
    else:
        data = request.form
           
    # invoke the controller
    res, vehicle = vehicles_controller.update_vehicle(data["vehicle_id"], data["manufacturer"], data["model"], data["plate"], data["user_uid"])

    # output
    if output_format(request) == JSON:
        return jsonify(results = vehicle)
    else:
        return redirect("/vehicles/%s" % vehicle["vehicle_id"])


@app.route('/vehicles/new', methods=['GET'])
def vehicles_new():

    # get all the available users to fill a combo in the view
    users_list = users_controller.show_users()

    # render the html form
    return render_template("new_vehicle.html", users=users_list, title="New Vehicle")


@app.route('/vehicles', methods=['POST'])
@auth.login_required
def vehicles_create():

    # input
    if input_format(request) == JSON:
        data = get_input_data(request)
    else:
        data = request.form

    # invoke the controller    
    status, vehicle = vehicles_controller.create_vehicle(data["manufacturer"], data["model"], data["plate"], data["user_uid"])
        
    # output
    if output_format(request) == JSON:
        return jsonify(results = vehicle)
    else:
        return redirect("/vehicles/%s" % vehicle["vehicle_id"])


@app.route('/vehicles/delete/<vehicle_id>', methods=['GET'])
@app.route('/vehicles/<vehicle_id>', methods=['DELETE'])
@auth.login_required
def vehicles_delete(vehicle_id):
    
    # invoke the controller
    res = vehicles_controller.delete_vehicle(vehicle_id)
    
    # select the proper output form
    if output_format(request) == JSON:
        if res:
            return make_response(jsonify({'OK': 'Vehicle Deleted'}), 200)        
        else:
            return make_response(jsonify({'error': 'Vehicle not Deleted'}), 401)
    else:
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
    if output_format(request) == JSON:
        return jsonify(results = res)
    else:
        return render_template("show_users.html", entries=res, title="Users")


@app.route('/users/<user_id>', methods=['GET'])
def users_show(user_id):

    # invoke the controller
    res = users_controller.show_user(user_id)

    # select the proper output form
    if output_format(request) == JSON:
        return jsonify(results = res)
    else:
        return render_template("show_user.html", entry=res, title="User details")


@app.route('/users/delete/<user_id>', methods=['GET'])
@app.route('/users/<user_id>', methods=['DELETE'])
@auth.login_required
def users_delete(user_id):

    # invoke the controller
    res = users_controller.delete_user(user_id)

    # select the proper output form
    if output_format(request) == JSON:
        if res:
            return make_response(jsonify({'OK': 'User Deleted'}), 200)        
        else:
            return make_response(jsonify({'error': 'User not Deleted'}), 401)
    else:
        return redirect("/users")


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
        
    # input
    if input_format == JSON:
        data = get_input_data(request)
    else:
        data = request.form

    # invoke the controller
    status, user = users_controller.create_user(data["name"], data["nick"], data["password"])

    # output
    if output_format == JSON:
        if status:
            return jsonify(results = user)          
        else:
            return make_response(jsonify({'error': 'Nickname already taken'}), 406)
    else:
        if status:
            return redirect("/users/%s" % user["user_uid"])
        else:
            return redirect("/users")


@app.route('/users/<user_id>', methods=['PUT'])
@app.route('/users/update/<user_id>', methods=['POST'])
def users_update(user_id):
        
    # input
    if input_format == JSON:
        data = get_input_data(request)
    else:
        data = request.form

    # invoke the controller
    status, user = users_controller.update_user(user_id, name, passwd)
    
    # output
    if output_format == JSON:
        return jsonify(results = user)
    else:
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

    # output
    if output_format(request) == JSON:
        return jsonify(results = res)
    else:
        return render_template("show_gss.html", gss = res, title="GroundStations")


@app.route('/groundstations/<gs_id>', methods=['GET'])
def gss_show(gs_id):
 
    # get the list of the ground stations
    gs = gss_controller.show_gs(gs_id)

    # output
    if output_format(request):
        return jsonify(results = gs)
    else:
        return render_template("show_gs.html", entry = gs, title="GroundStation details")


@app.route('/groundstations/new', methods=['GET'])
def gss_new():

    # render the html form
    return render_template("new_gs.html", title="New GroundStation")


@app.route('/groundstations', methods=['POST'])
def gss_create():
    
    # input
    if input_format(request) == JSON:
        data = get_input_data(request)
    else:
        data = request.form

    # invoke the controller
    status, gs = gss_controller.create_gs(data["name"], data["slatitude"], data["slongitude"], data["elatitude"], data["elongitude"])

    # output
    if output_format(request) == JSON:
        return jsonify(results = gs)
    else:
        return redirect("/groundstations")


@app.route('/groundstations/delete/<gs_id>', methods=['GET'])
@app.route('/groundstations/<gs_id>', methods=['DELETE'])
# @auth.login_required
def gss_delete(gs_id):
    
    # invoke the controller
    status = gss_controller.delete_gs(gs_id)
    
    # select the proper output form
    if output_format(request) == JSON:
        if res:
            return make_response(jsonify({'OK': 'GS Deleted'}), 200)        
        else:
            return make_response(jsonify({'error': 'GS not Deleted'}), 401)
    else:
        return redirect("/groundstations")


@app.route('/groundstations/<gs_id>/edit', methods=['GET'])
def gss_edit(gs_id):

    # retrieve the gs that should be modified
    res = gss_controller.show_gs(gs_id)

    # now render the template filled with the results
    return render_template("edit_gs.html", gs=res, title="Edit GroundStation")


@app.route('/groundstations/<gs_id>', methods=['PUT'])
@app.route('/groundstations/update/<gs_id>', methods=['POST'])
def gss_update(gs_id):

    # input
    if input_format(request) == JSON:
        data = get_input_data(request)
    else:
        data = request.form

    # invoke the controller
    status, gs = gss_controller.update_gs(gs_id, data["name"], data["slatitude"], data["slongitude"], data["elatitude"], data["elongitude"])

    # output
    if output_format(request) == JSON:
        return jsonify(results = gs)
    else:
        return redirect("/groundstations/%s" % newmodel["gs_id"])


################################################
#
# setting routes for the reservation controller
#
################################################

@app.route('/reservations/status', methods=['GET'])
def reservations_check():

    # check if a gs is reserved
    if input_format(request) == JSON:
        data = get_input_data(request)
    else:
        return make_response(jsonify({'error': 'Bad Request'}), 400)
            
    # invoke the controller
    try:
        status = reservations_controller.check_reservation(data["gs_id"], data["vehicle_id"],  data["user_id"], data["res_type"])
    except:
        return make_response(jsonify({'error': 'Bad Request'}), 400)

    # output
    if output_format(request) == JSON:
        if status:
            return make_response(jsonify({'OK': 'Valid Reservation'}), 200)        
        else:
            return make_response(jsonify({'error': 'Reservation not found'}), 404)            
    else:
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
    if output_format(request) == JSON:        
        return jsonify(results = res)
    else:
        return render_template("show_reservations.html", entries=res, title="Reservations")
    

@app.route('/users/<user_id>/reservations', methods=['GET'])
@auth.login_required
def user_reservations(user_id):

    # invoking the controller
    res = reservations_controller.show_reservations(user_id)

    # output
    if output_format(request) == JSON:        
        return jsonify(results = res)
    else:
        return render_template("show_reservations.html", entries=res, title="Reservations")


@app.route('/reservations/<reservation_id>', methods=['GET'])
def reservations_show(reservation_id):
    
    # invoking the controller
    res = reservations_controller.show_reservation(reservation_id)
    
    # output
    if output_format(request) == "json":        
        return jsonify(results = res)
    else:
        return render_template("show_reservation.html", entry = res, title="Reservation details")


@app.route('/reservations/delete/<reservation_id>', methods=['GET'])
@app.route('/reservations/<reservation_id>', methods=['DELETE'])
@auth.login_required
def reservations_delete(reservation_id):
    
    # invoke the controller
    res = reservations_controller.delete_reservation(reservation_id)
    
    # select the proper output form
    if output_format(request) == JSON:
        if res:
            return make_response(jsonify({'OK': 'Reservation Retired'}), 200)        
        else:
            return make_response(jsonify({'error': 'Reservation not retired'}), 401)
    else:
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

    # input
    if input_format(request) == JSON:
        data = get_input_data(request)
        vehicle_id = data["vehicle_id"]
        user_id = data["user_id"]
    else:
        data = request.form
        vehicle_id = request.form["user_car"].split("|")[0]
        user_id = request.form["user_car"].split("|")[1] 
               
    # invoke the controller
    status, reservation = reservations_controller.create_reservation(data["gs_id"], vehicle_id,  user_id)

    # output
    if output_format(request) == JSON:
        return jsonify(results = reservation)
    else:
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

    # input
    if input_format(request) == JSON:
        data = get_input_data(request)
        vehicle_id = data["vehicle_id"]
        user_id = data["user_id"]
    else:
        data = request.form
        vehicle_id = request.form["user_car"].split("|")[0]
        user_id = request.form["user_car"].split("|")[1] 

    # invoke the controller
    status, reservation = reservations_controller.update_reservation(reservation_id, data["gs_id"], vehicle_id,  user_id)

    # output
    if output_format(request) == JSON:        
        return jsonify(results = reservation)
    else:
        return redirect("/reservations/%s" % res["reservation_id"])


################################################
#
# Traditional Booking Service Interface
# Routes for: GCPs
#
################################################

@app.route('/gcps', methods=['GET'])
def gcps_showall():

    """This function is used to get a list of the GCPs"""

    # invoke the controller
    res = trad_controller.get_gcp_list()

    # return data
    if output_format(request) == JSON:        
        return jsonify(results = res)
    else:
        return render_template("show_gcps.html", title="GCPs", gcps=res)


@app.route('/gcps/<gcp_name>', methods=['GET'])
def gcps_show(gcp_name):

    """This function is used to get details about a GCP"""

    # invoke the controller
    res = trad_controller.get_gcp_details(gcp_name)

    # return data
    if output_format(request) == JSON:                
        return jsonify(res)
    else:
        return render_template("show_gcp.html", title="GCP %s" % gcp_name, gcps = res, gcpname = gcp_name)

################################################
#
# Traditional Booking Service Interface
# Routes for: EVSEs
#
################################################

@app.route('/evses/<evse_id>', methods=['PUT'])
@app.route('/evses/update/<evse_id>', methods=['POST'])
def evses_set_status(evse_id):

    """This function is used to set the status of an EVSE,
    to signal the start or the end of a recharge"""

    # get input data
    data = get_input_data(request)

    # invoke the controller
    res = trad_controller.set_evse_status(evse_id, data["status"], data["reservation"])

    # return
    if res:
        make_response(jsonify({'status': 'OK'}), 200)        
    else:
        make_response(jsonify({'status': 'error'}), 400)        


@app.route('/evses/<evse_id>', methods=['GET'])
def evses_status(evse_id):

    """It returns the status of the EVSE specifying
    if it is currently reserved and when it is scheduled
    the next reservation"""

    # get input data    
    data = get_input_data(request)

    # invoke the controller
    res = trad_controller.check_evse_status(data["evse_id"])

    # build a reply
    return make_response(jsonify(res), 200)        


@app.route('/evses/<evse_id>/check', methods=['GET'])
def user_authorization_check(evse_id):

    """This function is used to check if a user
    can be authorized to recharge his vehicle"""

    # read data    
    data = get_input_data(request)

    # invoke the controller
    print "Invoking the controller"
    res = trad_controller.check_user_authorization(data["evse_id"], data["user_id"], data["tolerance"])

    # build a reply
    return make_response(jsonify(res), 200)        


################################################
#
# Traditional Booking Service Interface
# Routes for: traditional reservations
#
################################################

@app.route('/treservations', methods=['GET'])
@auth.login_required
def treservations_showall():

    # invoke the controller
    status, res = trad_controller.get_tres_list()

    # output
    if output_format(request) == JSON:
        return make_response(jsonify(results = res))
    else:
        return render_template("show_treservations.html", entries = res, title = "Traditional Reservations")



@app.route('/treservations/get_options', methods=['GET'])
@auth.login_required
def chargeoptions_request():

    # input
    data = None
    if input_format(request) == JSON:    
        data = get_input_data(request)
    else:
        data = request.args
        print data

    # invoke the controller
    charge_options = trad_controller.get_charge_options(data["lat"], data["lon"], data["radius"], data["timeto"], data["timefrom"], data["user_uri"], data["vehicle_uri"], data["bidirectional"], data["requested_energy"])

    # output
    if output_format(request) == JSON:
        return make_response(jsonify(results = charge_options))
    else:
        return make_response(jsonify({'error': 'Bad Request - Only JSON is accepted!'}), 401)


@app.route("/treservations/<option_id>/confirm", methods=["POST"])
def chargeoptions_confirm(option_id):

    # invoke the controller
    status = trad_controller.charge_option_confirm(option_id)

    # output
    if output_format(request) == JSON:
        if status:
            return make_response(jsonify({'OK': 'Reservation confirmed'}), 200)        
        else:
            return make_response(jsonify({'error': 'Reservation Not confirmed'}), 401)
    else:
        return make_response(jsonify({'error': 'Bad Request - Only JSON is accepted!'}), 401)    


@app.route('/treservations/check', methods=['GET'])
def treservations_check():

    """This function is used to check if a user
    can be authorized to recharge his vehicle"""

    # get input data
    data = get_input_data(request)

    # invoke the controller
    if data:
        res = trad_controller.check_treservation(data["user_id"], data["evse_id"])
        return jsonify(res)
    else:
        return make_response(jsonify({'error': 'Bad request'}), 400)


@app.route("/treservations/delete/<res_id>", methods=["GET"])
@app.route("/treservations/<res_id>", methods=["DELETE"])
def reservation_deletion(res_id):

    # invoke the controller
    success = trad_controller.delete_reservation(res_id)
    
    # output
    if output_format(request) == JSON:
        if success:
            return make_response(jsonify({'OK': 'Reservation Retired'}), 200)        
        else:
            return make_response(jsonify({'error': 'Reservation Not Retired'}), 401)
    else:
        return make_response(jsonify({'error': 'Bad Request - Only JSON is accepted!'}), 401)


################################################
#
# Traditional Booking Service Interface
# Routes for: other
#
################################################
    

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

        # get the evse list
        kp = m3_kp_api(False, settings["sib_host"], settings["sib_port"])
        print evses_query_all
        kp.load_query_sparql(evses_query_all)
        results = kp.result_sparql_query

        # parse the results
        evses = []
        for result in results:
            evse = {}
            for field in result:
                evse[field[0]] = field[2]
            evses.append(evse)

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

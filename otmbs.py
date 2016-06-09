#!/usr/bin/python

# system-wide requirements
from flask import Flask, jsonify, render_template, request, redirect, url_for
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

# importing other local libraries
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
settings["block_size"] = settingsParser.getint("kb", "block_size")
settings["kb_files"] = []
for filename in settingsParser.get("kb", "kb_file").split("%"):
    settings["kb_files"].append(filename)

# loading the KB
loader = N3KBLoader(settings)
for filename in settings["kb_files"]:
    loader.load_n3file(filename)

# creating an instance of Flask
app = Flask(__name__)

# creating an instance of each controller
reservations_controller = ReservationsController(settings)
gss_controller = GroundStationsController(settings)
vehicles_controller = VehiclesController(settings)
users_controller = UsersController(settings)


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
def vehicles_delete(vehicle_id):
    
    # invoke the controller
    res = vehicles_controller.delete_vehicle(vehicle_id)
    
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
        

    print "CREAZIONEEEEEEEEEEEEEEEEEEEEEEEEE"

    # verify if the payload is json
    try:
        if request.content_type == "application/json":
            data = json.loads(request.data)
            name = data["name"]
            
            # invoke the controller
            status, user = users_controller.create_user(name)

            # redirect to the index
            return jsonify(results = user)

    except Exception as e:
        print e
        pass

    # invoke the controller
    status, user = users_controller.create_user(request.form["name"])

    # redirect to the index
    return redirect("/users/%s" % user["user_uid"])


@app.route('/users/<user_id>', methods=['PUT'])
@app.route('/users/update/<user_id>', methods=['POST'])
def users_update(user_id):
        
    # verify if the payload is json
    try:
        if request.content_type == "application/json":
            data = json.loads(request.data)
            name = data["name"]
            
            # invoke the controller
            status, user = users_controller.update_user(user_id, name)

            # redirect to the index
            return jsonify(results = user)

    except Exception as e:
        print e
        pass

    # invoke the controller
    status, user = users_controller.update_user(user_id, request.form["name"])

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
def reservations_showall():

    # invoking the controller
    res = reservations_controller.show_reservations()

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
def reservations_delete(reservation_id):
    
    # invoke the controller
    res = reservations_controller.delete_reservation(reservation_id)
    
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
# alfred non-rest interface
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
    app.run(debug = True, host = settings["flask_host"], port = settings["flask_port"])

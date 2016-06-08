#!/usr/bin/python

# system-wide requirements
from flask import Flask, jsonify, render_template, request, redirect, url_for
import ConfigParser
import requests

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

    # invoke the controller
    res = vehicles_controller.show_vehicles()

    # select the proper output form
    if request.args.has_key('format'):
        if request.args['format'] == 'json':
            return jsonify(results = res)
    else:
        print res
        return render_template("show_vehicles.html", title="Vehicles", entries=res)


@app.route('/vehicles/<vehicle_id>', methods=['GET'])
def vehicles_show(vehicle_id):

    # invoke the controller
    res = vehicles_controller.show_vehicle(vehicle_id)

    # select the proper output form
    if request.args.has_key('format'):
        if request.args['format'] == 'json':
            return jsonify(results = res)
    else:
        print res
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

    # read the form
    vehicle_model = request.form["model"]
    vehicle_user_id = request.form["user_uid"]
    vehicle_manufacturer = request.form["manufacturer"]

    # invoke the controller
    res = vehicles_controller.update_vehicle(vehicle_id, vehicle_manufacturer, vehicle_model, vehicle_user_id)

    # redirect to the index
    return redirect("/vehicles")


@app.route('/vehicles/new', methods=['GET'])
def vehicles_new():

    # get all the available users to fill a combo in the view
    users_list = users_controller.show_users()

    # render the html form
    return render_template("new_vehicle.html", users=users_list, title="New Vehicle")


@app.route('/vehicles', methods=['POST'])
def vehicles_create():
    
    # invoke the controller
    res = vehicles_controller.create_vehicle(request.form["manufacturer"], request.form["model"], request.form["user_uri"])

    # redirect to the index
    return redirect("/vehicles")


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

    # invoking the controller
    res = users_controller.show_users()

    # select the proper output form
    if request.args.has_key('format'):
        if request.args['format'] == 'json':
            return jsonify(results = res)
    else:

        print res
        return render_template("show_users.html", entries=res, title="Users")


@app.route('/users/<user_id>', methods=['GET'])
def users_show(user_id):

    # invoking the controller
    res = users_controller.show_user(user_id)

    # select the proper output form
    if request.args.has_key('format'):
        if request.args['format'] == 'json':
            return jsonify(results = res)
    else:
        print res
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

    print "***********************************************************"
    print request.args
    print "***********************************************************"
    print request.form
    print "***********************************************************"
    
    # invoke the controller
    res = users_controller.create_user(request.form["name"])

    # redirect to the index
    return redirect("/users")


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
    if request.args.has_key('format'):
        if request.args['format'] == 'json':
            return jsonify(results = res)
    else:
        return render_template("show_gss.html", gss = res, title="GroundStations")


@app.route('/groundstations/<gsid>', methods=['GET'])
def gss_show(gsid):
    
    # get the list of the ground stations
    gs = gss_controller.show_gs(gsid)

    # select the proper output form
    if request.args.has_key('format'):
        if request.args['format'] == 'json':
            return jsonify(results = gs)
    else:
        # render the html view
        return render_template("show_gs.html", entry = gs, title="GroundStation details")


@app.route('/groundstations/new', methods=['GET'])
def gss_new():

    # render the html form
    return render_template("new_gs.html", title="New GroundStation")


@app.route('/groundstations', methods=['POST'])
def gss_create():
    
    # invoke the controller
    res = gss_controller.create_gs(request.form["name"], request.form["latitude"], request.form["longitude"])

    # redirect to the index
    return redirect("/groundstations")


@app.route('/groundstations/delete/<gsid>', methods=['GET'])
@app.route('/groundstations/<gsid>', methods=['DELETE'])
def gss_delete(gsid):
    
    # invoke the controller
    res = gss_controller.delete_gs(gsid)
    
    # redirect to the index
    # return redirect("/groundstations", methods=['GET'])
    return redirect(url_for("gss_showall"))


@app.route('/groundstations/<gsid>/edit', methods=['GET'])
def gss_edit(gsid):

    # invoke the controller in order to retrieve
    # the gs that should be modified
    res = gss_controller.show_gs(gsid)

    # now render the edit template with the field
    # filled with the previous results
    return render_template("edit_gs.html", gs=res, title="Edit GroundStation")


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
    if request.args.has_key('format'):
        if request.args['format'] == 'json':
            return jsonify(results = res)
    else:
        print res
        return render_template("show_reservations.html", entries=res, title="Reservations")
    

@app.route('/reservations/<reservation_id>', methods=['GET'])
def reservations_show(reservation_id):
    
    # invoking the controller
    res = reservations_controller.show_reservation(reservation_id)

    # select the proper output form
    if request.args.has_key('format'):
        if request.args['format'] == 'json':
            return jsonify(results = res)
    else:
        # render the html view
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

    # invoke the controller
    print request.form
    res = reservations_controller.create_reservation(request.form["gs"], request.form["user_car"])

    # redirect to the index
    return redirect("/reservations")


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

    # invoke the controller
    print request.form
    res = reservations_controller.update_reservation(reservation_id, request.form["gs"], request.form["user_car"])

    # redirect to the index
    return redirect("/reservations")

    request.form["gs"], request.form["user_car"]


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
    if ALF_ACTIONS[action]["method"] == "GET":
        return redirect(url_for(ALF_ACTIONS[action]["name"], user_id = resource_id))
    else:
        # implement post!
        pass


# main
if __name__ == '__main__':
    app.run(debug = True, host = settings["flask_host"], port = settings["flask_port"])

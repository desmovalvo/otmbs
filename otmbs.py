#!/usr/bin/python

# system-wide requirements
from flask import Flask, jsonify, render_template, request, redirect
import ConfigParser

# importing models, controllers and views
from libs.n3loader import *
from models.user import *
from models.gpsdata import *
from models.vehicle import *
from models.reservation import *
from models.groundstation import *
from controllers.GroundStationsController import *
from controllers.ReservationsController import *
from controllers.VehiclesController import *
from controllers.UsersController import *

# reading configuration
settings = {}
settingsParser = ConfigParser.ConfigParser()
settingsParser.readfp(open("otmbs.conf"))
settings["sib_host"] = settingsParser.get("sib", "host")
settings["sib_port"] = settingsParser.getint("sib", "port")
settings["flask_port"] = settingsParser.getint("flask", "port")
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
        return render_template("show_vehicles.html", entries=res)


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
        return render_template("show_vehicle.html", entry=res)


@app.route('/vehicles/new', methods=['GET'])
def vehicles_new():

    # get all the available users to fill a combo in the view
    users_list = users_controller.show_users()

    # render the html form
    return render_template("new_vehicle.html", users=users_list)


@app.route('/vehicles', methods=['POST'])
def vehicles_create():
    
    # invoke the controller
    res = vehicles_controller.create_vehicle(request.form["manufacturer"], request.form["model"], request.form["user_uri"])

    # redirect to the index
    return redirect("/vehicles")


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
        return render_template("show_users.html", entries=res)



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
        return render_template("show_user.html", entry=res)



################################################
#
# setting routes for the groundstation controller
#
################################################

@app.route('/groundstations', methods=['GET'])
def gss_showall():
    
    # get the list of the ground stations
    gss_list = gss_controller.show_gss()

    # build the list for the map
    markers = []
    for gs in gss_list:
        marker = {}
        marker["lat"] = gs["latitude"]
        marker["lng"] = gs["longitude"]
        marker["name"] = gs["gsname"]
        marker["gsidentifier"] = gs["gsidentifier"]
        marker["url"] = ""
        markers.append(marker)
    print "MARKERS:"
    print markers

    # render the html view
    return render_template("show_gss.html", gss = gss_list, markers = markers)


@app.route('/groundstations/<gsid>', methods=['GET'])
def gss_show(gsid):
    
    # get the list of the ground stations
    gs = gss_controller.show_gs(gsid)

    # render the html view
    return render_template("show_gs.html", entry = gs)


@app.route('/groundstations/new', methods=['GET'])
def gss_new():

    # render the html form
    return render_template("new_gs.html")


@app.route('/groundstations', methods=['POST'])
def gss_create():
    
    # invoke the controller
    res = gss_controller.create_gs(request.form["name"], request.form["latitude"], request.form["longitude"])

    # redirect to the index
    return redirect("/groundstations")


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
        return render_template("show_reservations.html", entries=res)
    

@app.route('/reservations/<reservation_id>', methods=['GET'])
def reservations_show(reservation_id):
    
    # invoking the controller
    res = reservations_controller.show_reservation(reservation_id)

    # render the html view
    return render_template("show_reservation.html", entry = res)



# main
if __name__ == '__main__':
    app.run(debug = True, port = settings["flask_port"])

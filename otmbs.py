#!/usr/bin/python

# system-wide requirements
from flask import Flask, jsonify, render_template, request, redirect
import ConfigParser

# importing models, controllers and views
from libs.n3loader import *
from models.user import *
from models.vehicle import *
from models.groundstation import *
from controllers.GroundStationsController import *
from controllers.VehiclesController import *
from controllers.UsersController import *

# reading configuration
settings = {}
settingsParser = ConfigParser.ConfigParser()
settingsParser.readfp(open("otmbs.conf"))
settings["sib_host"] = settingsParser.get("sib", "host")
settings["sib_port"] = settingsParser.getint("sib", "port")
settings["flask_port"] = settingsParser.getint("flask", "port")
settings["kb_file"] = settingsParser.get("kb", "kb_file")
settings["block_size"] = settingsParser.getint("kb", "block_size")

# loading the KB
loader = N3KBLoader(settings)
loader.load_n3file(settings["kb_file"])

# creating an instance of Flask
app = Flask(__name__)

# creating an instance of each controller
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
    res = vehicles_controller.show()

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
    res = vehicles_controller.show(vehicle_id)

    # return
    return jsonify(results = res)


@app.route('/vehicles/new', methods=['GET'])
def vehicles_new():

    # get all the available users to fill a combo in the view
    users_list = users_controller.show()

    # render the html form
    return render_template("new_vehicle.html", users=users_list)


@app.route('/vehicles', methods=['POST'])
def vehicles_create():
    
    # invoke the controller
    res = vehicles_controller.create_vehicle(request.form["manufacturer"], request.form["model"], request.form["user_uri"])

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
    gss_list = gss_controller.show()
    print gss_list

    # build the list for the map
    markers = []
    for gs in gss_list:
        print "**************************** " + str(gs)
        marker = {}
        marker["lat"] = gs["latitude"]
        marker["lng"] = gs["longitude"]
        marker["name"] = gs["gsname"]
        marker["url"] = ""
        markers.append(marker)
    print markers

    # render the html view
    return render_template("show_gss.html", gss = gss_list, markers = markers)


# main
if __name__ == '__main__':
    app.run(debug = True, port = settings["flask_port"])

#!/usr/bin/python

# system-wide requirements
from flask import Flask, jsonify
import ConfigParser

# importing models, controllers and views
from libs.n3loader import *
from models.vehicle import *
from controllers.VehiclesController import *

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
vehicles_controller = VehiclesController(settings)

# setting routes for the vehicle controller
@app.route('/vehicles', methods=['GET'])
def vehicles_controller_showall():
    res = vehicles_controller.showall()
    print res
    return jsonify(results = res)

# main
if __name__ == '__main__':
    app.run(debug = True, port = settings["flask_port"])

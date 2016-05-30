#!/usr/bin/python

# import models
from models.vehicle import *

class VehiclesController:

    """Controller for the vehicles-related operations"""


    # constructor
    def __init__(self, settings):

        """Constructor of the VehiclesController"""
        
        # storing otmbs settings
        self.settings = settings


    # show all
    def show(self, vehicle_id = None):
        
        """This method is used to retrieve all the Vehicles"""

        v = Vehicle(self.settings)
        if vehicle_id:
            vehicles_list = v.find(vehicle_id)
        else:
            vehicles_list = v.find()

        # transform the results in a "jsonifiable"-form
        json_results = []
        for vehicle in vehicles_list:
            json_vehicle = {}
            for field in vehicle:
                json_vehicle[field[0]] = field[2]
            json_results.append(json_vehicle)

        # return
        print json_results
        return json_results

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
    def show_vehicles(self):
        
        """This method is used to retrieve all the Vehicles"""

        v = Vehicle(self.settings)
        vehicles_list = v.find_vehicles()

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


    # show one
    def show_vehicle(self, vehicle_id):
        
        """This method is used to retrieve a single Vehicle"""

        v = Vehicle(self.settings)
        vehicles_list = v.find_vehicle(vehicle_id)

        # transform the results in a "jsonifiable"-form
        json_vehicle = {}
        for vehicle in vehicles_list:
            for field in vehicle:
                json_vehicle[field[0]] = field[2]

        # add the vehicle id
        json_vehicle["vehicle_id"] = vehicle_id

        # return
        print json_vehicle
        return json_vehicle


    # create vehicle
    def create_vehicle(self, manufacturer, model, user_uri):

        """This method is used to create a new vehicle"""

        # create the vehicle
        v = Vehicle(self.settings)
        status = v.create(manufacturer, model, user_uri)
        
        # return
        return status


    # delete vehicle
    def delete_vehicle(self, vehicle_id):

        """This method is used to delete a vehicle"""

        # ask the model to delete the vehicle
        vm = Vehicle()
        v = vm.find_vehicle(vehicle_id)
        status = v.delete()

        # return
        return status

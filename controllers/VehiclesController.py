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
            json_results.append(vehicle.to_json())

        # return
        return json_results


    # show one
    def show_vehicle(self, vehicle_id):
        
        """This method is used to retrieve a single Vehicle"""

        v = Vehicle(self.settings)
        v = v.find_vehicle(vehicle_id)

        # transform the results in a "jsonifiable"-form
        json_vehicle = v.to_json()

        # return
        return json_vehicle


    # create vehicle
    def create_vehicle(self, manufacturer, model, user_uid):

        """This method is used to create a new vehicle"""

        # create the vehicle
        v = Vehicle(self.settings)
        status, vehicle = v.create(manufacturer, model, user_uid)
        json_vehicle = vehicle.to_json()

        # return
        return status, json_vehicle


    # create vehicle
    def update_vehicle(self, vehicle_id, manufacturer, model, user_id):

        """This method is used to update a vehicle"""

        # find the vehicle
        v = Vehicle(self.settings)
        v = v.find_vehicle(vehicle_id)
        
        # update it
        status, newmodel = v.update(manufacturer, model, user_id)
        jsonmodel = newmodel.to_json()
        
        # return
        return status, jsonmodel


    # delete vehicle
    def delete_vehicle(self, vehicle_id):

        """This method is used to delete a vehicle"""

        # ask the model to delete the vehicle
        vm = Vehicle(self.settings)
        status = vm.delete(vehicle_id)

        # return
        return status


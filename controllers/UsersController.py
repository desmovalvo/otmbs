#!/usr/bin/python

# import models
from models.user import *
from models.vehicle import *

class UsersController:

    """Controller for the users-related operations"""


    # constructor
    def __init__(self, settings):

        """Constructor of the UsersController"""
        
        # storing otmbs settings
        self.settings = settings


    # show all
    def show_users(self):
        
        """This method is used to retrieve all the Users"""

        u = User(self.settings)
        users_list = u.find_users()

        # transform the results in a "jsonifiable"-form
        json_results = []
        for user in users_list:
            json_user = {}
            for field in user:
                json_user[field[0]] = field[2]
            json_results.append(json_user)

        # return
        return json_results


    # show one
    def show_user(self, user_id):
        
        """This method is used to retrieve all the Users"""

        # find the user
        u = User(self.settings)
        users_results = u.find_user(user_id)
    
        # find vehicles of the user
        v = Vehicle(self.settings)
        vehicles_results = v.find_by_user_id(user_id)

        # transform the results in a "jsonifiable"-form
        json_user = {}
        for user in users_results:
            for field in user:
                json_user[field[0]] = field[2]

        # add the person uid 
        json_user["person_uid"] = user_id

        # add the vehicles to the results
        json_user["vehicles"] = []
        for vehicle in vehicles_results:
            json_vehicle = {}
            for field in vehicle:
                json_vehicle[field[0]] = field[2]
            json_user["vehicles"].append(json_vehicle)

        # return
        print json_user
        return json_user


    # delete user
    def delete_user(self, user_id):

        """This method is used to delete a person"""

        # ask the model to delete the user
        um = User(self.settings)
        status = um.delete(user_id)

        # return
        return status


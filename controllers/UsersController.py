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
            json_results.append(user.to_json())

        # return
        return json_results


    # show one
    def show_user(self, user_id):
        
        """This method is used to retrieve all the Users"""

        # find the user
        u = User(self.settings)
        u = u.find_user(user_id)

        # transform the results in a "jsonifiable"-form
        json_user = u.to_json()

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


    # create user
    def create_user(self, name):

        """Method to create a person"""

        # create!
        u = User(self.settings, name)
        status = u.create()
        
        # return
        return status

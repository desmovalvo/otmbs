#!/usr/bin/python

# import models
from models.user import *

class UsersController:

    """Controller for the users-related operations"""


    # constructor
    def __init__(self, settings):

        """Constructor of the UsersController"""
        
        # storing otmbs settings
        self.settings = settings


    # show all
    def show(self, user_id = None):
        
        """This method is used to retrieve all the Users"""

        u = User(self.settings)
        if user_id:
            users_list = u.find(user_id)
        else:
            users_list = u.find()

        # transform the results in a "jsonifiable"-form
        json_results = []
        for user in users_list:
            json_user = {}
            for field in user:
                json_user[field[0]] = field[2]
            json_results.append(json_user)

        # return
        print json_results
        return json_results

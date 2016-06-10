#!/usr/bin/python

# local import
from models.user import *


# the AuthController
class AuthController:

    """This class is used to retrieve data for
    the authentication of the users"""

    # constructor
    def __init__(self, settings):

        """Constructor of the AuthController"""

        # store settings
        self.settings = settings


    # find user's password
    def get_password(self, user_id):

        # find the user
        print "UTENTE: " + str(user_id)
        um = User(self.settings)
        u = um.find_user(user_id)

        # return the password
        if u.user_password:
            return u.user_password
        else:
            return None

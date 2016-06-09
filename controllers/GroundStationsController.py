#!/usr/bin/python

# import models
from models.groundstation import *

class GroundStationsController:

    """The controller for the Ground Stations"""

    # constructor
    def __init__(self, settings):
        
        """Constructor for the GroundStation controller"""

        # store settings
        self.settings = settings


    # show gss
    def show_gss(self):

        """Show all the GroundStations"""

        # create an instance of the model
        gs = GroundStation(self.settings)

        # query the model
        results = []
        results = gs.find_gss()

        # return the result in a json-ifiable form
        json_results = []
        for station in results:
            json_results.append(station.to_json())

        # return
        return json_results

            
    # show gss
    def show_gs(self, gsid):

        """Show a single GroundStation based on its id"""

        # create an instance of the model
        gs = GroundStation(self.settings)

        # query the model
        results = []
        results = gs.find_gs(gsid)

        # transform the result in a json-ifiable form
        json_gs = results.to_json()

        # return
        print json_gs
        return json_gs

            
    # create gs
    def create_gs(self, name, slatitude, slongitude, elatitude, elongitude):

        """Method to create a new GroundStation"""

        # Instantiate the GS model
        gs_model = GroundStation(self.settings, name, slatitude, slongitude,
                                 elatitude, elongitude)
        status, gs = gs_model.create()

        # return the gs
        json_gs = gs.to_json()
        return status, json_gs


    # update a gs
    def update_gs(self, gs_id, name, slatitude, slongitude, elatitude, elongitude):

        """Method to update a GroundStation"""

        # instantiate the GS model
        gs_model = GroundStation(self.settings)

        # find the GS
        gs_model = gs_model.find_gs(gs_id)

        # update it
        status = gs_model.update(name, slatitude, slongitude, elatitude, elongitude)

        # json form
        json_gs = gs_model.to_json()

        # return
        return status, json_gs


    # delete groundstation
    def delete_gs(self, gs_id):

        """This method is used to delete a groundstation.
        All the reservations to the groundstation are also deleted"""

        # retrieve the groundstation
        gm = GroundStation(self.settings)
        gm = gm.find_gs(gs_id)

        # delete!
        status = gm.delete()

        # return
        return status

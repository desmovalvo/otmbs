#!/usr/bin/python

# import models
from models.gpsdata import *
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
    def create_gs(self, name, latitude, longitude):

        """Method to create a new GroundStation"""

        print "HERE I AM"

        # create the GPS Data
        gpsdata = GPSData(self.settings)
        gpsdata.latitude = latitude
        gpsdata.longitude = longitude
        status = gpsdata.create()
        print status
        print gpsdata.gpsdata_uri

        # create the gs
        if status:
            gs = GroundStation(self.settings, name, gpsdata)
            status = gs.create()            

        print gs
        print status

        print "DONE"

        # return
        if status:
            return True


    # delete groundstation
    def delete_gs(self, gs_id):

        """This method is used to delete a groundstation.
        All the reservations to the groundstation are also deleted"""

        # retrieve the groundstation
        gm = GroundStation(self.settings)

        # delete!
        status = gm.delete(gs_id)

        # return
        return status

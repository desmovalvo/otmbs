#!/usr/bin/python

# import models
from models.groundstation import *

class GroundStationsController:

    """The controller for the Ground Stations"""
    
    def __init__(self, settings):

        # store settings
        self.settings = settings


    def show(self, gsid = None):

        # create an instance of the model
        gs = GroundStation(self.settings)

        # query the model
        results = []
        if gsid:
            results = gs.find(gsid)
        else:
            results = gs.find()
            print results

        # return the result in a json-ifiable form
        json_results = []
        for station in results:
            json_station = {}
            for field in station:
                json_station[field[0]] = field[2]
            json_results.append(json_station)

        # return
        print json_results
        return json_results

            

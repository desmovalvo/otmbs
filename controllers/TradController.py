#!/usr/bin/python

# global libraries
import time
import traceback
from smart_m3.m3_kp_api import *

# local libraries
from libs.traditional_bs_queries import *

# controller
class TradController:

    """The controller for the Traditional Reservations"""

    # constructor
    def __init__(self, settings):
        
        """Constructor for the Traditional Reservation controller"""

        # store settings
        self.settings = settings


    # check EVSE status
    def check_evse_status(self, evse_id):

        """This method is used to get the status of the EVSE"""

        # initialize results
        res = {}
        
        # perform the SPARQL query
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
        kp.load_query_sparql(evse_status_query % evse_id)
        query_results = kp.result_sparql_query           

        # parse the results
        if len(query_results) == 0:

            # no reservation is active and
            # no reservation is scheduled!

            res = {
                "nextReservationIn":None,
                "isReservedNow":False
            }

        else:

            # get the current time in ms
            now = int(round(time.time() * 1000))

            # initialize results
            reserved_now = False
            nextreservation = None
            
            # check if it is reserved now
            for res in query_results:
                if int(res[2][2]) <= now <= int(res[3][2]):
                    reserved_now = True
                    break

            # check when is the next reservation
            for res in query_results:

                # check future reservations
                if int(res[2][2]) > now:

                    # if we have still not found a future reservation
                    if not nextreservation:
                        nextreservation = int(res[2][2])
                        
                    # if we already found a future reservation
                    else:
                        if int(res[2][2]) < nextreservation:
                            nextreservation = int(res[2][2])

            # if a nextreservation is found, then we have
            # to calculate the time difference in ms
            if nextreservation:
                nextreservation = nextreservation - now

            res = {
                "nextReservationIn":nextreservation,
                "isReservedNow":reserved_now
            }

        # return
        return res

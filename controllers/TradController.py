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
            res = { "nextReservationIn":None, "isReservedNow":False }

        else:

            # get the current time in ms
            now = int(round(time.time() * 1000))

            # initialize results
            reserved_now = False
            nextreservation = None
            nextuser = None
            
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
                        nextuser = res[4][2]
                        
                    # if we already found a future reservation
                    else:
                        if int(res[2][2]) < nextreservation:
                            nextreservation = int(res[2][2])
                            nextuser = res[4][2]

            # if a nextreservation is found, then we have
            # to calculate the time difference in ms
            if nextreservation:
                nextreservation = nextreservation - now

            res = {
                "nextReservationIn":nextreservation,
                "isReservedNow":reserved_now,
                "nextUser":nextuser
            }

        # return
        return res


    # check EVSE status
    def check_user_authorization(self, evse_id, user_id, tolerance):

        """This method is used to check if the user can recharge"""

        # initialize results
        res = {}
        authorized = False

        # determine current time
        now = int(round(time.time() * 1000))        
        
        # check if the user reserved the EVSE for this time
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
        kp.load_query_sparql(user_auth_query % (evse_id, user_id))
        query_results = kp.result_sparql_query
        for res in query_results:
            if int(res[2][2]) <= now <= int(res[3][2]):
                return {"confirmed":True}

        
        # check if the user that reserved the EVSE is himself
        status = self.check_evse_status(evse_id)
        if status["nextUser"] == user_id and status["nextReservationIn"] <= tolerance:
            return {"confirmed":True}

        # ...else...
        return {"confirmed":False}
        
        
    # get GCP list
    def get_gcp_list(self):

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
        kp.load_query_sparql(gcps_list_query)
        query_results = kp.result_sparql_query

        # build a dict
        results = []
        for res in query_results:
            results.append({ "gcp_uri" : res[0][2],
                             "gcp_name" : res[1][2],
                             "gcp_lat" : res[2][2],
                             "gcp_lng" : res[3][2] })

        # return results
        return results


    # get GCP details
    def get_gcp_details(self, evse_name):

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # perform the query
        kp.load_query_sparql(gcp_details_query % evse_name)
        query_results = kp.result_sparql_query

        # build a dict
        results = []
        for res in query_results:
            results.append({ "gcp_connector" : res[0][2],
                             "gcp_evsename" : res[1][2],
                             "gcp_pow" : res[2][2],
                             "gcp_volt" : res[3][2],
                             "gcp_price" : res[4][2],
                             "gcp_cout" : res[5][2],
                             "gcp_cin" : res[6][2],
                             "gcp_stat" : res[7][2],
                         })

        # return results
        return results


    def check_treservations(self, user_id, evse_id):
        
        """This method is used to check if the user can
        be authorized to perform a recharge"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # perform the query
        kp.load_query_sparql(check_trad_res_query % (evse_id, user_id))
        query_results = kp.result_sparql_query
        
        # results initialization
        status = {"status":"error", "reservation":None}
        Tnow = int(round(time() * 1000))
        minDifference = 0
        reservationf = ""
	
	# building results
        for results in query_results:
            for result in results:
                if result[0] == "Tstart":
                    tstart = result[2]
                elif result[0] == "Tend":
                    tend = result[2]
                elif result[0] == "r":
                    reservation = result[2]
                elif result[0] == "end":
                    end = result[2]
            difference = int(tstart) - int(Tnow)
            if( (int(tend) - int(Tnow) > 0) and (end == None) and ((difference  < minDifference) or (minDifference == 0)) ):
                minDifference=difference
                reservationf = reservation
                status = {"status":"OK", "reservation":reservationf}

        # return
        return status
            

    def set_evse_status(self, evse_id, status, reservation):
    
        """Method used to set the status of an EVSE"""

        # calculate current time
        Tnow = int(round(time() * 1000))

        try:
            if status.lower() == "start":
                self.KP.load_update_sparql(set_evse_status_start % (reservation, Tnow))
            elif status.lower() == "stop":
                self.KP.load_update_sparql(set_evse_status_stop % (reservation, Tnow))
            return True
            
        except Exception as e:
            return False
            
        

#!/usr/bin/python

# global libraries
import time
import traceback
from uuid import uuid4
from smart_m3.m3_kp_api import *
from smart_m3.m3_kp_api import Literal as LLiteral

# local libraries
from libs.otmbs_constants import *
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
            
        
    def get_charge_options(self, lat, lng, rad, timeto, timefrom, user_uri, vehicle_uri, bidirectional, req_energy):

        """Method used to retrieve the possible charge options"""
        
        # generate UUIDs
        request_uri = NS + str(uuid4())
        time_interval_uri = NS + str(uuid4())
        energy_uri = NS + str(uuid4())
        spatial_range_uri = NS + str(uuid4())

        # insert
        triple_list = []
        triple_list.append(Triple(URI(request_uri), URI(RDF_TYPE), URI(NS + "ChargeRequest")))
        triple_list.append(Triple(URI(request_uri), URI(NS + "hasRequestingVehicle"), URI(NS + vehicle_uri)))
        triple_list.append(Triple(URI(request_uri), URI(NS + "hasRequestingUser"), URI(NS + user_uri)))
        triple_list.append(Triple(URI(request_uri), URI(NS + "allowBidirectional"), LLiteral("true")))
        triple_list.append(Triple(URI(time_interval_uri), URI(RDF_TYPE), URI(NS + "TimeInterval")))
        triple_list.append(Triple(URI(request_uri), URI(NS + "hasTimeInterval"), URI(time_interval_uri)))
        triple_list.append(Triple(URI(time_interval_uri), URI(NS + "hasFromTimeMillisec"), LLiteral(str(timefrom))))
        triple_list.append(Triple(URI(time_interval_uri), URI(NS + "hasToTimeMillisec"), LLiteral(timeto)))
        triple_list.append(Triple(URI(energy_uri), URI(RDF_TYPE), URI(NS + "EnergyData")))
        triple_list.append(Triple(URI(request_uri), URI(NS + "hasRequestedEnergy"), URI(energy_uri)))
        triple_list.append(Triple(URI(energy_uri), URI(NS + "hasUnitOfMeasure"), URI(NS + "kiloWattHour")))
        triple_list.append(Triple(URI(energy_uri), URI(NS + "hasValue"), LLiteral(req_energy)))
        triple_list.append(Triple(URI(spatial_range_uri), URI(RDF_TYPE), URI(NS + "SpatialRangeData")))
        triple_list.append(Triple(URI(request_uri), URI(NS + "hasSpatialRange"), URI(spatial_range_uri)))
        triple_list.append(Triple(URI(spatial_range_uri), URI(NS + "hasGPSLatitude"), LLiteral(lat)))
        triple_list.append(Triple(URI(spatial_range_uri), URI(NS + "hasGPSLongitude"), LLiteral(lng)))
        triple_list.append(Triple(URI(spatial_range_uri), URI(NS + "hasRadius"), LLiteral(rad)))

        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
        kp.load_rdf_insert(triple_list)

        # query (instead of subscription)
        results = False
        while not results:
        
            # perform the query
            kp.load_query_rdf(Triple(None, URI(NS + "hasRelatedRequest"), URI(request_uri)))
            query_results = kp.result_rdf_query
            if len(query_results) > 0:
                results = query_results

        # query:
        res_uri = results[0][0]
        kp.load_query_sparql(chargeresponse_query % (res_uri, res_uri))
        charge_requests = []
        results2 = kp.result_sparql_query
    
        # parse the results
        charge_requests = []
        for result in results2:
            charge_request = {}
            for field in result:
                charge_request[field[0]] = field[2]
            charge_requests.append(charge_request)

        # return
        return charge_requests

        
    def charge_option_confirm(self, charge_option):
        
        """This method is used to confirm a charge option"""

        # insert the triple
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
        kp.load_rdf_insert([Triple(URI(NS + charge_option), URI(NS + "confirmByUser"), LLiteral("true"))])
        print "NS: " + str(NS)
        
        # look for system confirm (subscription replaced by iterative query)
        results = None
        while not results:
            kp.load_query_rdf(Triple(URI(NS + charge_option), URI(NS + "confirmBySystem"), None))        
            results = kp.result_rdf_query
        sysconfirm = results[0][2]

        # return
        print "SYSCONFIRM" + str(sysconfirm)
        if str(sysconfirm).lower() == "true":
            kp.load_rdf_insert([Triple(URI(NS + charge_option), URI(NS + "ackByUser"), LLiteral("true"))])
            return True
        else:
            return False


    def delete_reservation(self, res_id):

        """This method is used to retire a reservation"""
        
        # initialize the return value
        success = True

        # connect to the SIB
        try:
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

            # get the res_uri
            res_uri = NS + res_id
        
            # generate a reservation retire uri
            res_ret_uri = NS + str(uuid4())

            # get the reservation user
            kp.load_query_rdf(Triple(URI(res_uri), URI(NS + "reservationHasUser"), None))
            query_results = kp.result_rdf_query
            user_uri = query_results[0][2]

            # build the triple list
            triple_list = []
            triple_list.append(Triple(URI(res_ret_uri), URI(RDF_TYPE), URI(NS + "ReservationRetire")))
            triple_list.append(Triple(URI(res_ret_uri), URI(NS + "retiredByUser"), URI(user_uri)))
            triple_list.append(Triple(URI(res_ret_uri), URI(NS + "retiredReservation"), URI(res_uri)))
            
            # insert the reservation retire request
            kp.load_rdf_insert(triple_list)

        except:
    
            # no success :'(
            success = False

        return success


    def get_tres_list(self):

        """This method is used to retrieve a list of all 
        the traditional reservations"""
        
        # connect to the SIB
        try:
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
            kp.load_query_sparql(tres_list_query)
            results = kp.result_sparql_query

            json_results = []
            for result in results:
                json_result = {}
                for field in result:
                    json_result[field[0]] = field[2]
                json_results.append(json_result)

            return True, json_results

        except:
            return False, None


    def get_tres(self, res_id):

        """This method is used to retrieve a traditional reservation"""
        
        # connect to the SIB
        try:
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
            res = NS + res_id
            kp.load_query_sparql(tres_query % (res, res, res, res, res, res))
            results = kp.result_sparql_query

            json_result = {}
            for field in results[0]:
                json_result[field[0]] = field[2]

            return True, json_result

        except Exception as e:
            print "____________________________________________________"
            print e
            print "____________________________________________________"
            return False, None

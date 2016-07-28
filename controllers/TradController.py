#!/usr/bin/python

# global libraries
import time
import traceback
from uuid import uuid4
from termcolor import colored
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
            res = { "nextReservationIn":None, "isReservedNow":False, "nextUser":None }

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
                return True
        
        # check if the user that reserved the EVSE is himself
        status = self.check_evse_status(evse_id)
        if status["nextUser"] == user_id and status["nextReservationIn"] <= tolerance:
            return True

        # ...else...
        return False
        
        
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
        Tnow = int(round(time.time() * 1000))

        try:
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

            if status.lower() == "start":
                kp.load_query_sparql(set_evse_status_start % (reservation, Tnow))
            elif status.lower() == "stop":
                kp.load_query_sparql(set_evse_status_stop % (reservation, Tnow))
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
        
        # look for system confirm (subscription replaced by iterative query)
        results = None
        while not results:
            kp.load_query_rdf(Triple(URI(NS + charge_option), URI(NS + "confirmBySystem"), None))        
            results = kp.result_rdf_query
        sysconfirm = results[0][2]

        # return
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
            print tres_list_query
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
            q = tres_query % (res, res, res, res, res, res)
            print q
            kp.load_query_sparql(q)
            results = kp.result_sparql_query

            json_result = {}
            for field in results[0]:
                json_result[field[0]] = field[2]

            return True, json_result

        except Exception as e:
            print e
            return False, None


    def new_onthefly(self, evse_id, user_id):
        
        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # build URIs
        requestURI = NS + str(uuid.uuid4())
        intervalURI = NS + str(uuid.uuid4())
        EnergyURI = NS + str(uuid.uuid4())
        spaceURI = NS + str(uuid.uuid4())

        # retrieve evse data (lat, lng, power)
        latitude, longitude, power = self.get_evse_coordinates(evse_id)

        # determine fromtime
        fromTime = str(long(round(time.time())  * 1000))
        
        # determine totime
        # to make a new reservation on the fly we need to know
        # when the next recharge is scheduled
        toTime = None
        evse_status = self.check_evse_status(evse_id)
        if evse_status["nextReservationIn"]:
            toTime = int(fromTime) + int(evse_status["nextReservationIn"]) - 60000
            if (fromTime - toTime) < 900000:
                return False
        else:
            toTime = int(fromTime) + (70*60*1000)

        # determine energy
        energy_value = str(round(((long(toTime)/1000-900) - int(fromTime)) * float(power)/3600))

        # build the query
        print colored("QUERY 1", "blue", attrs=["bold"])
        query1 = '\
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
        PREFIX ns:<http://www.m3.com/2012/05/m3/ioe-ontology.owl#> \
        INSERT { <' + str(requestURI) + '> rdf:type ns:ChargeRequest . \
        <' + str(requestURI) + '> ns:hasRequestingVehicle ns:unknownVehicle . \
        ns:unknownVehicle ns:hasVehicleIdentifier "EM_UnkVeh" . \
        <' + str(requestURI) + '> ns:hasRequestingUser ?user . \
        <' + str(requestURI) + '> ns:hasTimeInterval <' + str(intervalURI) + '> . \
        <' + str(requestURI) + '> ns:hasSpatialRange <' + str(spaceURI) + '> . \
        <' + str(requestURI) + '> ns:hasRequestedEnergy <' + str(EnergyURI) + '> . \
        <' + str(intervalURI) + '> rdf:type ns:TimeInterval . \
        <' + str(intervalURI) + '> ns:hasFromTimeMillisec "' + str(fromTime) + '" . \
        <' + str(intervalURI) + '> ns:hasToTimeMillisec "' + str(toTime) + '" . \
        <' + str(EnergyURI) + '> rdf:type ns:EnergyData . \
        <' + str(EnergyURI) + '> ns:hasValue "' + "1" + '" . \
        <' + str(EnergyURI) + '> ns:hasUnitOfMeasure ns:kiloWatthour . \
        <' + str(spaceURI) + '> rdf:type ns:SpatialRangeData . \
        <' + str(spaceURI) + '> ns:hasGPSLatitude "' + str(latitude) + '" . \
        <' + str(spaceURI) + '> ns:hasGPSLongitude "' + str(longitude) + '" . \
        <' + str(spaceURI) + '> ns:hasRadius "' + str(0.01) +'" \
        } WHERE { \
        ?user ns:hasUserIdentifier "' + str(user_id) + '" \
        }'        
        print query1
        print str(long(round(time.time())))
        kp.load_query_sparql(query1)
        time.sleep(2)

        print colored("QUERY 2", "blue", attrs=["bold"])
        query2= '\
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
        PREFIX ns:<http://www.m3.com/2012/05/m3/ioe-ontology.owl#> \
        SELECT ?option WHERE { \
        ?resp ns:hasRelatedRequest <' + requestURI + '> . \
        ?resp ns:hasChargeOption ?option \
        }'
        print query2
        kp.load_query_sparql(query2)
        queryresponse = kp.result_sparql_query
        attempts=0
        optionURI = None
        while((queryresponse==None) or (attempts < 5)):
            kp.load_query_sparql(query2)
            queryresponse = kp.result_sparql_query
            for results in queryresponse:
                for result in results: 
                    if result[0] == "option":
                        optionURI = result[2]
                        attempts = 5
            attempts = attempts + 1
            time.sleep(1)
            print "OptionURI = " + str(optionURI) 
		
        if(optionURI == None):
            print "No Option found"
            return False
        else:            
            query3 = 'PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
            PREFIX ns:<http://www.m3.com/2012/05/m3/ioe-ontology.owl#> \
            INSERT DATA { <' + optionURI + '> ns:confirmByUser "true" }'
            kp.load_query_sparql(query3)
            print colored("QUERY 3", "blue", attrs=["bold"])
            print query3
            time.sleep(2)
		
        query4= '\
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
        PREFIX ns:<http://www.m3.com/2012/05/m3/ioe-ontology.owl#> \
        SELECT ?confirm WHERE { \
        <' + optionURI + '> ns:confirmBySystem ?confirm }'
        print colored("QUERY 4", "blue", attrs=["bold"])
        print query4
        confirm=""
        kp.load_query_sparql (query4)
        queryresponse = kp.result_sparql_query
        for results in queryresponse:
            for result in results: 
                if result[0] == "confirm":
                    confirm = result[2]
                    
        if (confirm == "true"):
            kp.load_rdf_insert([Triple(URI(optionURI), URI(NS + "ackByUser"), LLiteral("true"))])
            return True
        else:
            return False


    def get_evse_coordinates(self, evse_id):

        """This method is used to retrieve the coordinates of an EVSE"""

        # building the query
        q = evse_coords_query % evse_id
        print q

        # connect to the SIB and perform the query
        try:
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
            kp.load_query_sparql(q)
            results = kp.result_sparql_query

        except Exception as e:
            print e
            return None

        lat = results[0][0][2]
        lng = results[0][1][2]
        powe = results[0][2][2]
        return lat, lng, powe

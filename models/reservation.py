#!/usr/bin/python

# system-wide requirements
import uuid
from os import sys, path
from smart_m3.m3_kp_api import *

# local requirements
from libs.otmbs_constants import *

# Reservation class
class Reservation:

    """This class is responsible for the mapping between the
    service and the SIB content for the reservations"""

    # constructor
    def __init__(self, settings):

        """Constructor for the Reservation class"""

        # settings
        self.settings = settings

    
    # find reservations
    def find_reservations(self):

        """Method used to retrieve all the reservations"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # perform a SPARQL query
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        SELECT ?reservation_uri ?reservation_id ?vehicle_uri ?vehicle_id ?vehicle_manufacturer ?vehicle_model ?user_uri ?user_id ?user_name ?gs_uri ?gs_id
        WHERE {
            ?reservation_uri rdf:type <%s> .
            ?reservation_uri ns:hasReservationIdentifier ?reservation_id .
            ?reservation_uri ns:reservedByVehicle ?vehicle_uri .
            ?vehicle_uri ns:hasVehicleIdentifier ?vehicle_id .
            ?vehicle_uri ns:hasManufacturer ?vehicle_manufacturer .
            ?vehicle_uri ns:hasModel ?vehicle_model .
            ?reservation_uri ns:hasUser ?user_uri .
            ?user_uri ns:hasUserIdentifier ?user_id .
            ?user_uri ns:hasName ?user_name .
            ?reservation_uri ns:hasGS ?gs_uri .
            ?gs_uri ns:hasGSIdentifier ?gs_id
        }"""
        print query % (RDF, NS, RESERVATION_CLASS)
        kp.load_query_sparql(query % (RDF, NS, RESERVATION_CLASS))
        results = kp.result_sparql_query           

        # return
        return results

        
    # find reservation
    def find_reservation(self, reservation_id):

        """Method used to retrieve a reservation given the id"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # perform a SPARQL query
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        SELECT ?reservation_uri ?vehicle_uri ?vehicle_id ?vehicle_manufacturer ?vehicle_model ?user_uri ?user_id ?user_name ?gs_uri ?gs_id
        WHERE {
            ?reservation_uri rdf:type <%s> .
            ?reservation_uri ns:hasReservationIdentifier "%s" .
            ?reservation_uri ns:reservedByVehicle ?vehicle_uri .
            ?vehicle_uri ns:hasVehicleIdentifier ?vehicle_id .
            ?vehicle_uri ns:hasManufacturer ?vehicle_manufacturer .
            ?vehicle_uri ns:hasModel ?vehicle_model .
            ?reservation_uri ns:hasUser ?user_uri .
            ?user_uri ns:hasUserIdentifier ?user_id .
            ?user_uri ns:hasName ?user_name .
            ?reservation_uri ns:hasGS ?gs_uri .
            ?gs_uri ns:hasGSIdentifier ?gs_id
        }"""
        print query % (RDF, NS, RESERVATION_CLASS, reservation_id)
        kp.load_query_sparql(query % (RDF, NS, RESERVATION_CLASS, reservation_id))
        results = kp.result_sparql_query           

        # return
        return results


    # delete reservation
    def delete(self, reservation_id):

        """Method used to delete a reservation"""

        # sparql query
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        DELETE {
            ?reservation_uri rdf:type ns:Reservation .
            ?reservation_uri ns:reservedByVehicle ?vehicle_uri .
            ?reservation_uri ns:hasUser ?user_uri .
            ?reservation_uri ns:hasGS ?gs_uri .
            ?reservation_uri ns:hasReservationIdentifier "%s"
        }
        WHERE {
            ?reservation_uri ns:hasReservationIdentifier "%s" .
        }"""

        # putting triples
        try:
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
            kp.load_query_sparql(query % (RDF, NS, reservation_id, reservation_id))
            return True
        except Exception as e:
            return False


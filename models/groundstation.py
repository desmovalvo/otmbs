#!/usr/bin/python

# system-wide requirements
import uuid
from os import sys, path
from smart_m3.m3_kp_api import *

# local requirements
from libs.otmbs_constants import *

# Vechile class
class GroundStation:

    """This class is responsible for the mapping between the
    service and the SIB content for the Ground Stations"""

    # constructor
    def __init__(self, settings, name = None, gpsdata = None):
        
        """Constructor for the GroundStation model"""

        # setting initial attributes
        self.gs_uri = None
        self.name = name
        self.gpsdata = gpsdata

        # store settings
        self.settings = settings

        
    # create
    def create(self):

        """This method is used to create the gs
        by storing its triples into the SIB"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])    

        # generate an uuid
        self.uuid = str(uuid.uuid4())
        self.gs_uri = NS + self.uuid
        self.gsid = self.uuid.split("-")[0]

        # create the triples
        triples = []
        triples.append(Triple(URI(self.gs_uri), URI(RDF_TYPE), URI(GS_CLASS)))
        triples.append(Triple(URI(self.gs_uri), URI(NS + "hasGSIdentifier"), Literal(self.gsid)))
        triples.append(Triple(URI(self.gs_uri), URI(NS + "hasName"), Literal(self.name)))
        triples.append(Triple(URI(self.gs_uri), URI(NS + "hasGPSData"), URI(self.gpsdata.gpsdata_uri)))

        # putting triples
        try:
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
            kp.load_rdf_insert(triples)
            return True
        except Exception as e:
            return False


    # get the list of the ground stations
    def find_gss(self):
        
        """Retrieves Ground Stations from the SIB"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # perform a SPARQL query
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        SELECT ?gs ?gsidentifier ?gsname ?latitude ?longitude
        WHERE {
            ?gs rdf:type <%s> .
            ?gs ns:hasGSIdentifier ?gsidentifier .
            ?gs ns:hasName ?gsname .
            ?gs ns:hasGPSData ?gpsdata .
            ?gpsdata ns:hasLatitude ?latitude .
            ?gpsdata ns:hasLongitude ?longitude .
        }"""
        print query % (RDF, NS, GS_CLASS)
        kp.load_query_sparql(query % (RDF, NS, GS_CLASS))
        results = kp.result_sparql_query           

        # return
        return results


    # get the list of the ground stations
    def find_gs(self, gsid):
        
        """Retrieves a single Ground Station from the SIB"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # perform the SPARQL query
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        SELECT ?gs ?gsname ?latitude ?longitude
        WHERE {
            ?gs rdf:type <%s> .
            ?gs ns:hasGSIdentifier "%s" .
            ?gs ns:hasName ?gsname .
            ?gs ns:hasGPSData ?gpsdata .
            ?gpsdata ns:hasLatitude ?latitude .
            ?gpsdata ns:hasLongitude ?longitude .
        }"""
        print query % (RDF, NS, GS_CLASS, gsid)
        kp.load_query_sparql(query % (RDF, NS, GS_CLASS, gsid))
        results = kp.result_sparql_query       
        print results    

        # return
        return results


    # get the list of reservations
    def find_gs_reservations(self, gsid):

        """Retrieves the list of reservations for the given ground station"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])        

        # perform the SPARQL query
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        SELECT ?reservation_uri
        WHERE {
            ?reservation_uri rdf:type <%s> .
            ?reservation_uri ns:hasGS ?gs_uri .
            ?gs_uri ns:hasGSIdentifier "%s"
        }"""
        print query % (RDF, NS, RESERVATION_CLASS, gsid)
        kp.load_query_sparql(query % (RDF, NS, RESERVATION_CLASS, gsid))
        results = kp.result_sparql_query       
        print results    

        # return
        return results

        
    # delete gs
    def delete(self, gsid):

        """Delete the ground station"""

        # build the triple list
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        DELETE {
            ?gs_uri rdf:type ns:GroundStation .
            ?gs_uri ns:hasGSIdentifier "%s" .
            ?gs_uri ns:hasName ?gsname .
            ?gs_uri ns:hasGPSData ?gpsdata .
            ?gpsdata ns:hasLatitude ?latitude .
            ?gpsdata ns:hasLongitude ?longitude .
            ?reserv_uri rdf:type ns:Reservation .
            ?reserv_uri ns:reservedByVehicle ?vehicle_uri .
            ?reserv_uri ns:hasUser ?user_uri .
            ?reserv_uri ns:hasGS ?gs_uri .     
            ?reserv_uri ns:hasReservationIdentifier ?reserv_id
        }
        WHERE {
            ?gs_uri ns:hasGSIdentifier "%s" .
        }"""


        # remove the triples
        try:
            # connect to the SIB and remove the triples
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])        
            kp.load_query_sparql(query % (RDF, NS, gsid, gsid))
        except:
            return False

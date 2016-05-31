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
    def __init__(self, settings):
        
        """Constructor for the GroundStation model"""

        # store settings
        self.settings = settings


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

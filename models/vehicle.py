#!/usr/bin/python

# system-wide requirements
import uuid
from os import sys, path
from smart_m3.m3_kp_api import *

# local requirements
from libs.otmbs_constants import *

# Vechile class
class Vehicle:

    """This class is responsible for the mapping between the
    service and the SIB content"""

    # constructor
    def __init__(self, settings):

        """Constructor for the Vehicle class"""

        # settings
        self.settings = settings

        # initialization of class attributes
        self.brand = None
        self.model = None
        self.user_id = None
        self.vehicle_id = None


    # create vehicles
    def create(self, brand, model, user_id):

        """Method used to create a NEW vehicle. Returns True for
        a successful creation, False otherwise"""

        # generating an UUID for the vehicle
        self.vehicle_id = str(uuid.uuid4())
        
        # creating the triples
        triples = []
        triples.append(Triple(URI(NS + self.vehicle_id), URI(RDF_TYPE), URI(VEHICLE_CLASS)))
        triples.append(Triple(URI(NS + self.vehicle_id), URI(NS + "hasBrand"), Literal(brand)))
        triples.append(Triple(URI(NS + self.vehicle_id), URI(NS + "hasModel"), Literal(model)))
        triples.append(Triple(URI(NS + user_id), URI(NS + "hasVehicle"), URI(NS + self.vehicle_id)))
        
        # putting triples
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
        kp.load_rdf_insert(triples)

    
    # find
    def find(self, vehicle_id = None):
        
        """Method used to retrieve vehicles from the SIB"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # query
        if vehicle_id:
            
            query = """PREFIX rdf:<%s>
            PREFIX ns:<%s>
            SELECT ?brand ?model ?person_uri ?person_name
            WHERE {
                ns:%s rdf:type %s .
                ns:%s ns:hasManufacturer ?brand .
                ns:%s ns:hasModel ?model .
                ?person_uri ns:hasVehicle ns:%s .
                ?person_uri ns:hasName ?person_name .
                ?person_uri ns:hasUserIdentifier ?person_uid
            }"""

            kp.load_query_sparql(query % (RDF, NS, vehicle_id, VEHICLE_CLASS, vehicle_id, vehicle_id))
            results = kp.results_sparql_query
            
        else:

            # perform a SPARQL query
            query = """PREFIX rdf:<%s>
            PREFIX ns:<%s>
            SELECT ?vehicle ?brand ?model ?person_uri ?person_name ?person_uid
            WHERE {
                ?vehicle rdf:type <%s> .
                ?vehicle ns:hasManufacturer ?brand .
                ?vehicle ns:hasModel ?model .
                ?person_uri ns:hasVehicle ?vehicle .
                ?person_uri ns:hasName ?person_name .
                ?person_uri ns:hasUserIdentifier ?person_uid
            }"""
            kp.load_query_sparql(query % (RDF, NS, VEHICLE_CLASS))
            results = kp.result_sparql_query           

        # return
        return results


if __name__ == "__main__":
    print path.dirname(path.abspath(__file__))

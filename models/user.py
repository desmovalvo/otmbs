#!/usr/bin/python

# system-wide requirements
import uuid
from os import sys, path
from smart_m3.m3_kp_api import *

# local requirements
from libs.otmbs_constants import *

# User class
class User:

    """This class is responsible for the mapping between the
    service and the SIB content for the Person class"""

    # constructor
    def __init__(self, settings):

        """Constructor for the User class"""

        # settings
        self.settings = settings

        # initialization of class attributes
        self.user_uri = None
        self.user_id = None
        self.name = None


    # create vehicles
    def create(self, user_id, name, vehicle_id = None):

        """Method used to create a NEW vehicle. Returns True for
        a successful creation, False otherwise"""

        # generating an UUID for the vehicle
        self.user_uri = str(uuid.uuid4())
        
        # creating the triples
        triples = []
        triples.append(Triple(URI(NS + self.user_uri), URI(RDF_TYPE), URI(PERSON_CLASS)))
        triples.append(Triple(URI(NS + self.user_uri), URI(NS + "hasUserIdentifier"), Literal(user_id)))
        triples.append(Triple(URI(NS + self.user_uri), URI(NS + "hasName"), Literal(name)))
        if vehicle_id:
            triples.append(Triple(URI(NS + self.user_uri), URI(NS + "hasVehicle"), URI(vehicle_id)))
        
        # putting triples
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
        kp.load_rdf_insert(triples)

    
    # find
    def find(self, user_id = None):
        
        """Method used to retrieve users from the SIB"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # query
        if user_id:

            # perform a SPARQL query
            query = """PREFIX rdf:<%s>
            PREFIX ns:<%s>
            SELECT ?person_name ?person_uid ?vehicle_id
            WHERE {
                ns:%s rdf:type ns:Person .
                ns:%s ns:hasUserIdentifier ?person_uid .
                ns:%s ns:hasName ?person_name .
                OPTIONAL { ns:%s ns:hasVehicle ?vehicle_id }
            }"""
            kp.load_query_sparql(query % (RDF, NS, user_id, user_id, user_id, user_id))
            results = kp.result_sparql_query           
            
        else:

            # perform a SPARQL query
            query = """PREFIX rdf:<%s>
            PREFIX ns:<%s>
            SELECT ?person_uri ?person_name ?person_uid ?vehicle_id
            WHERE {
                ?person_uri rdf:type ns:Person .
                ?person_uri ns:hasUserIdentifier ?person_uid .
                ?person_uri ns:hasName ?person_name .
                OPTIONAL { ?person_uri ns:hasVehicle ?vehicle_id }
            }"""
            kp.load_query_sparql(query % (RDF, NS))
            results = kp.result_sparql_query           

        # return
        return results


if __name__ == "__main__":
    print path.dirname(path.abspath(__file__))

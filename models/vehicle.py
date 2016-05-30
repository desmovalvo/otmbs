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
        self.vehicle_uri = None


    # create vehicles
    def create(self, brand, model, user_id = None):

        """Method used to create a NEW vehicle. Returns True for
        a successful creation, False otherwise"""

        # read attributes
        self.brand = brand
        self.model = model
        if user_id:
            self.user_id = user_id

        # generating an UUID for the vehicle
        vehicle_uuid = str(uuid.uuid4())
        self.vehicle_uri = NS + vehicle_uuid

        # generate the vehicle id
        self.vehicle_id = self.brand.replace(" ", "") + self.model.replace(" ", "") + "_" + vehicle_uuid[0:3]
        
        # creating the triples
        triples = []
        triples.append(Triple(URI(self.vehicle_uri), URI(RDF_TYPE), URI(VEHICLE_CLASS)))
        triples.append(Triple(URI(self.vehicle_uri), URI(NS + "hasVehicleIdentifier"), Literal(self.vehicle_id)))
        triples.append(Triple(URI(self.vehicle_uri), URI(NS + "hasManufacturer"), Literal(self.brand)))
        triples.append(Triple(URI(self.vehicle_uri), URI(NS + "hasModel"), Literal(self.model)))

        # TODO: in this case we must obtain the user UUID!
        if user_id:
            triples.append(Triple(URI(NS + user_id), URI(NS + "hasVehicle"), URI(self.vehicle_uri)))
        
        # putting triples
        try:
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
            kp.load_rdf_insert(triples)
            return True
        except Exception as e:
            return False
            
    
    # find
    def find(self, vehicle_id = None):
        
        """Method used to retrieve vehicles from the SIB"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # query
        if vehicle_id:
            
            query = """PREFIX rdf:<%s>
            PREFIX ns:<%s>
            SELECT ?brand ?model ?person_uri ?person_name ?person_uid
            WHERE {
                ?vehicle_uri rdf:type <%s> .
                ?vehicle_uri ns:hasManufacturer ?brand .
                ?vehicle_uri ns:hasModel ?model .
                ?vehicle_uri ns:hasVehicleIdentifier "%s" .
                OPTIONAL {
                    ?person_uri ns:hasVehicle ?vehicle_uri .
                    ?person_uri ns:hasName ?person_name .
                    ?person_uri ns:hasUserIdentifier ?person_uid
                }
            }"""
            print query % (RDF, NS, VEHICLE_CLASS, vehicle_id)
            kp.load_query_sparql(query % (RDF, NS, VEHICLE_CLASS, vehicle_id))
            results = kp.result_sparql_query
            
        else:

            # perform a SPARQL query
            query = """PREFIX rdf:<%s>
            PREFIX ns:<%s>
            SELECT ?vehicle ?vehicle_id ?brand ?model ?person_uri ?person_name ?person_uid
            WHERE {
                ?vehicle rdf:type <%s> .
                ?vehicle ns:hasVehicleIdentifier ?vehicle_id .
                ?vehicle ns:hasManufacturer ?brand .
                ?vehicle ns:hasModel ?model .
                OPTIONAL {
                    ?person_uri ns:hasVehicle ?vehicle .
                    ?person_uri ns:hasName ?person_name .
                    ?person_uri ns:hasUserIdentifier ?person_uid
                }
            }"""
            kp.load_query_sparql(query % (RDF, NS, VEHICLE_CLASS))
            results = kp.result_sparql_query           

        # return
        return results


if __name__ == "__main__":
    print path.dirname(path.abspath(__file__))

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
        self.user = None
        self.brand = None
        self.model = None
        self.user_uri = None # TODO: delete it!
        self.vehicle_id = None
        self.vehicle_uri = None


    # create vehicles
    def create(self, brand, model, user_uri):

        """Method used to create a NEW vehicle. Returns True for
        a successful creation, False otherwise"""

        # read attributes
        self.brand = brand
        self.model = model
        self.user_uri = user_uri

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
        triples.append(Triple(URI(self.user_uri), URI(NS + "hasVehicle"), URI(self.vehicle_uri)))
        
        # putting triples
        try:
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
            kp.load_rdf_insert(triples)
            return True
        except Exception as e:
            return False
            
    
    # show vehicles
    def find_vehicles(self):
        
        """Method used to retrieve vehicles from the SIB"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

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

        # build a list of vehicle models
        model_results = []
        for result in results:
            new_model = Vehicle(self.settings)
            new_model.vehicle_uri = result[0][2]
            new_model.vehicle_id = result[1][2]
            new_model.brand = result[2][2]
            new_model.model = result[3][2]
            new_model.user_uri = result[4][2]
            new_model.user_name = result[5][2]
            new_model.user_uid = result[6][2]
            model_results.append(new_model)

        # return
        return model_results


    # show vehicle
    def find_vehicle(self, vehicle_id):
        
        """Method used to retrieve a vehicle from the SIB"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # query
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        SELECT ?vehicle_uri ?brand ?model ?person_uri ?person_name ?person_uid
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

        # build the model to return
        model_result = Vehicle(self.settings)
        model_result.vehicle_uri = results[0][0][2]
        model_result.brand = results[0][1][2]
        model_result.model = results[0][2][2]
        model_result.user_uri = results[0][3][2]
        model_result.user_name = results[0][4][2]
        model_result.user_uid = results[0][5][2]
        model_result.vehicle_id = vehicle_id

        # return
        return model_result

        
    # find user's vehicles
    def find_by_user_id(self, user_id):

        """This method is used to retrieve all the vehicles
        of a user, given its user_id"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # query
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        SELECT ?vehicle_uri ?brand ?model ?vehicle_id
        WHERE {
            ?vehicle_uri rdf:type <%s> .
            ?vehicle_uri ns:hasManufacturer ?brand .
            ?vehicle_uri ns:hasModel ?model .
            ?vehicle_uri ns:hasVehicleIdentifier ?vehicle_id .
            ?user_uri ns:hasUserIdentifier "%s" .
            ?user_uri ns:hasVehicle ?vehicle_uri
        
        }"""
        
        print query % (RDF, NS, VEHICLE_CLASS, user_id)
        kp.load_query_sparql(query % (RDF, NS, VEHICLE_CLASS, user_id))
        results = kp.result_sparql_query

        # return
        return results
        

    # delete vehicle
    def delete(self, vehicle_id):

        # sparql query
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        DELETE {
            ?vehicle_uri rdf:type ns:Vehicle .
            ?vehicle_uri ns:hasVehicleIdentifier "%s" .
            ?vehicle_uri ns:hasManufacturer ?manufacturer .
            ?vehicle_uri ns:hasModel ?model .
            ?user_uri ns:hasVehicle ?vehicle_uri .
            ?reservation_uri rdf:type ns:Reservation .
            ?reservation_uri ns:reservedByVehicle ?vehicle_uri .
            ?reservation_uri ns:hasUser ?user_uri .
            ?reservation_uri ns:hasGS ?gs_uri .
            ?reservation_uri ns:hasReservationIdentifier ?reservation_id
        }
        WHERE {
            ?vehicle_uri ns:hasVehicleIdentifier "%s" .
        }"""

        # putting triples
        try:
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
            kp.load_query_sparql(query % (RDF, NS, vehicle_id, vehicle_id))
            return True
        except Exception as e:
            return False


    # to json
    def to_json(self):

        """This method return a JSON representation of the vehicle"""
        
        vdict = {} 
        vdict["vehicle_uri"] = self.vehicle_uri
        vdict["vehicle_id"] = self.vehicle_id
        vdict["vehicle_manufacturer"] = self.brand
        vdict["vehicle_model"] = self.model
        vdict["vehicle_user_uid"] = self.user_uid
        vdict["vehicle_user_uri"] = self.user_uri
        vdict["vehicle_user_name"] = self.user_name

        return vdict

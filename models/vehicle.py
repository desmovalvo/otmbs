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
        self.user_uid = None 
        self.vehicle_id = None
        self.vehicle_uri = None


    # create vehicles
    def create(self, brand, model, user_uid):

        """Method used to create a NEW vehicle. Returns True for
        a successful creation, False otherwise"""

        # read attributes
        self.brand = brand
        self.model = model
        self.user_uid = user_uid

        # generating an UUID for the vehicle
        vehicle_uuid = str(uuid.uuid4())
        self.vehicle_uri = NS + vehicle_uuid

        # generate the vehicle id
        self.vehicle_id = self.brand.replace(" ", "") + self.model.replace(" ", "") + "_" + vehicle_uuid[0:3]
        
        # SPARQL query
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        INSERT {
            ?user_uri ns:hasVehicle <%s> .
            <%s> rdf:type ns:Vehicle .
            <%s> ns:hasVehicleIdentifier "%s" .
            <%s> ns:hasManufacturer "%s" .
            <%s> ns:hasModel "%s" .
        }
        WHERE {
            ?user_uri rdf:type ns:Person .
            ?user_uri ns:hasUserIdentifier "%s" .
        }"""

        # putting triples
        try:
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
            kp.load_query_sparql(query % (RDF, NS, self.vehicle_uri,
                                          self.vehicle_uri, self.vehicle_uri, self.vehicle_id, 
                                          self.vehicle_uri, self.brand, self.vehicle_uri, 
                                          self.model, self.user_uid))

            # retrieve the user name in order to complete the model
            query = """PREFIX rdf:<%s>
            PREFIX ns:<%s>
            SELECT ?username
            WHERE { 
                ?useruri ns:hasUserIdentifier "%s" .
                ?useruri ns:hasName ?username
            }"""
            kp.load_query_sparql(query % (RDF, NS, self.user_uid))
            results = kp.result_sparql_query
            self.user_name = results[0][0][2]

            return True, self
        except Exception as e:
            print e
            return False, None
            
    
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
        print "POST WUERY"
        model_result = Vehicle(self.settings)
        model_result.vehicle_uri = results[0][0][2]
        print "POST WUERY"
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

    
    # update
    def update(self, manufacturer, model, user_id):

        """Method used to update the model of a vehicle"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # SPARQL query
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        INSERT {
            ?vehicle_uri ns:hasModel "%s" .
            ?vehicle_uri ns:hasManufacturer "%s" .
            ?user_uri ns:hasVehicle ?vehicle_uri .
            ?reservation_uri ns:hasUser ?user_uri
        }
        DELETE {
            ?vehicle_uri ns:hasModel ?old_model .
            ?vehicle_uri ns:hasManufacturer ?old_manufacturer .
            ?old_user_uri ns:hasVehicle ?vehicle_uri .
            ?reservation_uri ns:hasUser ?old_user_uri
        }
        WHERE {
            ?vehicle_uri rdf:type ns:Vehicle .
            ?vehicle_uri ns:hasModel ?old_model .
            ?vehicle_uri ns:hasManufacturer ?old_manufacturer .
            ?vehicle_uri ns:hasVehicleIdentifier "%s" .
            ?old_user_uri ns:hasVehicle ?vehicle_uri .
            ?old_user_uri ns:hasUserIdentifier ?old_user_id .
            ?user_uri ns:hasUserIdentifier "%s" .
            OPTIONAL {
                ?reservation_uri ns:hasUser ?old_user_uri
            }
        }"""

        try:
            print query % (RDF, NS, model, manufacturer, self.vehicle_id, user_id)
            kp.load_query_sparql(query % (RDF, NS, model, manufacturer, self.vehicle_id, user_id))
            results = kp.result_sparql_query    
            model = self.find_vehicle(self.vehicle_id)

            return True, model
        except:
            return False, None
        

    # to json
    def to_json(self):

        """This method return a JSON representation of the vehicle"""
        
        vdict = {} 
        vdict["vehicle_uri"] = self.vehicle_uri
        vdict["vehicle_id"] = self.vehicle_id
        vdict["vehicle_manufacturer"] = self.brand
        vdict["vehicle_model"] = self.model
        vdict["vehicle_user_uid"] = self.user_uid
        vdict["vehicle_user_name"] = self.user_name

        return vdict

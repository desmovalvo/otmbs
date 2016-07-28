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
    def __init__(self, settings, name = None, uid = None, password = None):

        """Constructor for the User class"""

        # settings
        self.settings = settings

        # initialization of class attributes
        self.user_uri = None
        self.user_uid = uid
        self.user_name = name
        self.user_password = password
        self.vehicles = []
        self.reservations = []


    # create users
    def create(self):

        """Method used to create a NEW user. Returns True for
        a successful creation, False otherwise"""

        # generating an UUID for the user
        uid = str(uuid.uuid4())
        self.user_uri = NS + uid        
        
        # creating the triples
        triples = []
        triples.append(Triple(URI(self.user_uri), URI(RDF_TYPE), URI(PERSON_CLASS)))
        triples.append(Triple(URI(self.user_uri), URI(NS + "hasUserIdentifier"), Literal(self.user_uid)))
        triples.append(Triple(URI(self.user_uri), URI(NS + "hasName"), Literal(self.user_name)))
        triples.append(Triple(URI(self.user_uri), URI(NS + "hasPassword"), Literal(self.user_password)))

        # putting triples
        try:
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
            kp.load_rdf_insert(triples)
            return True, self
        except:
            return False, None


    # update user
    def update(self, name, password):

        """Method used to update a User. Returns True for
        a successful creation, False otherwise"""
        
        # creating the triples to remove and to update
        atriples = []
        rtriples = []
        rtriples.append(Triple(URI(self.user_uri), URI(NS + "hasName"), Literal(self.user_name)))
        rtriples.append(Triple(URI(self.user_uri), URI(NS + "hasPassword"), Literal(self.user_password)))
        atriples.append(Triple(URI(self.user_uri), URI(NS + "hasName"), Literal(name)))
        atriples.append(Triple(URI(self.user_uri), URI(NS + "hasPassword"), Literal(password)))
        
        # putting triples
        try:
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
            kp.load_rdf_update(atriples, rtriples)
            self.user_name = name
            return True, self
        except:
            return False, None

    
    # find
    def find_users(self):
        
        """Method used to retrieve users from the SIB"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # perform a SPARQL query
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        SELECT ?person_uri ?person_name ?person_uid ?vehicle_uri ?vehicle_id ?vehicle_manufacturer ?vehicle_model ?reservation_uri ?reservation_id ?gs_uri ?gs_id ?person_password
        WHERE {
            ?person_uri rdf:type ns:Person .
            ?person_uri ns:hasUserIdentifier ?person_uid .
            ?person_uri ns:hasName ?person_name .
            ?person_uri ns:hasPassword ?person_password .
            OPTIONAL {
                ?vehicle_uri rdf:type ns:Vehicle .
                ?person_uri ns:hasVehicle ?vehicle_uri .
                ?vehicle_uri ns:hasVehicleIdentifier ?vehicle_id .
                ?vehicle_uri ns:hasManufacturer ?vehicle_manufacturer .
                ?vehicle_uri ns:hasModel ?vehicle_model .
                OPTIONAL { 
                    ?reservation_uri rdf:type ns:Reservation .
                    ?reservation_uri ns:hasReservationIdentifier ?reservation_id .
                    ?reservation_uri ns:hasUser ?person_uri .
                    ?reservation_uri ns:reservedByVehicle ?vehicle_uri .
                    ?reservation_uri ns:hasGS ?gs_uri .
                    ?gs_uri ns:hasGSIdentifier ?gs_id
                }
            }
        }
        ORDER BY ?user_uid"""
        kp.load_query_sparql(query % (RDF, NS))
        results = kp.result_sparql_query           

        # build a dict for every user
        user_dicts = {}
        for res in results:
            
            person_uri = res[0][2]
            person_name = res[1][2]
            person_uid = res[2][2]
            vehicle_uri = res[3][2]
            vehicle_id = res[4][2]
            vehicle_manu = res[5][2]
            vehicle_model = res[6][2]
            res_id = res[7][2]
            gs_id = res[8][2]
            person_password = res[11][2]

            if user_dicts.has_key(person_uri):

                # the dictionary already exists,
                # now we should add vehicles or reservations

                # add vehicles
                if vehicle_id:
                    if not user_dicts[person_uri]["vehicles"].has_key(vehicle_id):
                        user_dicts[person_uri]["vehicles"][vehicle_id] = { "vehicle_manu" : vehicle_manu, "vehicle_model" : vehicle_model }

                # add reservations
                if res_id:
                    if not user_dicts[person_uri]["reservations"].has_key(res_id):
                        user_dicts[person_uri]["reservations"][res_id] = { "reservation_id" : res_id, "gs_id" : gs_id, "vehicle_id" : vehicle_id}

            else:

                # creation of a dictionary
                user_dicts[person_uri] = {
                    "person_name" : person_name,
                    "person_password" : person_password,
                    "person_uid" : person_uid,
                    "vehicles" : {},
                    "reservations" : {}
                }
            
                # add vehicles
                if vehicle_id:
                    if not user_dicts[person_uri]["vehicles"].has_key(vehicle_id):
                        user_dicts[person_uri]["vehicles"][vehicle_id] = { "vehicle_manu" : vehicle_manu, "vehicle_model" : vehicle_model }

                # add reservations
                if res_id:
                    if not user_dicts[person_uri]["reservations"].has_key(res_id):
                        user_dicts[person_uri]["reservations"][res_id] = { "reservation_id" : res_id, "gs_id" : gs_id, "vehicle_id" : vehicle_id}


        # build the models and return them
        user_models = []
        for el in user_dicts:
            user_model = User(self.settings)
            user_model.user_uri = el
            user_model.user_uid = user_dicts[el]["person_uid"]
            user_model.user_name = user_dicts[el]["person_name"]
            user_model.user_password = user_dicts[el]["person_password"]
            for vehicle in user_dicts[el]["vehicles"]:
                user_model.vehicles.append(vehicle)
            for reservation in user_dicts[el]["reservations"]:
                user_model.reservations.append(reservation)
            user_models.append(user_model)
            
        # return
        return user_models


    # find
    def find_user(self, user_id):
        
        """Method used to retrieve a single user from the SIB"""

        print user_id

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # perform a SPARQL query
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        SELECT ?person_uri ?person_name ?vehicle_id ?vehicle_manufacturer ?vehicle_model ?reservation_uri ?reservation_id ?gs_uri ?gs_id ?person_password
        WHERE {
            ?person_uri rdf:type ns:Person .
            ?person_uri ns:hasUserIdentifier "%s" .
            ?person_uri ns:hasName ?person_name .
            ?person_uri ns:hasPassword ?person_password .
            OPTIONAL {
                ?vehicle_uri rdf:type ns:Vehicle .
                ?person_uri ns:hasVehicle ?vehicle_uri .
                OPTIONAL {
                    ?vehicle_uri ns:hasVehicleIdentifier ?vehicle_id .
                } .
                ?vehicle_uri ns:hasManufacturer ?vehicle_manufacturer .
                ?vehicle_uri ns:hasModel ?vehicle_model .
                OPTIONAL { 
                    ?reservation_uri rdf:type ns:Reservation .
                    ?reservation_uri ns:hasReservationIdentifier ?reservation_id .
                    ?reservation_uri ns:hasUser ?person_uri .
                    ?reservation_uri ns:reservedByVehicle ?vehicle_uri .
                    ?reservation_uri ns:hasGS ?gs_uri .
                    ?gs_uri ns:hasGSIdentifier ?gs_id
                }
            }
        }"""
        kp.load_query_sparql(query % (RDF, NS, user_id))
        results = kp.result_sparql_query           

        # check if there are results
        if len(results) > 0:

            # build the model for the user
            user_model = User(self.settings)
            print results
            user_model.user_uri = results[0][0][2]
            user_model.user_name = results[0][1][2]
            user_model.user_password = results[0][9][2]
            user_model.user_uid = user_id
            user_model.vehicles = []
            user_model.reservations = []
    
            # add vehicles to the user
            for res in results:
    
                if res[2][2]:
    
                    v = {"vehicle_id": res[2][2],
                         "vehicle_manufacturer": res[3][2],
                         "vehicle_model": res[4][2],
                    }
                    
                    if not v in user_model.vehicles:
                        user_model.vehicles.append(v)
                        
    
            # add reservations to the user
            for res in results:
                
                if res[6][2]:
    
                    r = {"reservation_id": res[6][2],
                         "reservation_gs": res[8][2],
                         "reservation_vehicle": res[2][2]
                     }
                
                    if not r in user_model.reservations:
                        user_model.reservations.append(r)
                    
        
            # return model
            return user_model
                
        else:
        
            # return model
            return self
        


    # delete
    def delete(self, user_id):

        """Method used to delete a user"""

        # sparql query
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        DELETE {
            ?user_uri rdf:type ns:Person .
            ?user_uri ns:hasVehicle ?vehicle_uri .
            ?user_uri ns:hasName ?name .
            ?user_uri ns:hasPassword ?user_password .
            ?user_uri ns:hasUserIdentifier "%s" .
            ?vehicle_uri rdf:type ns:Vehicle .
            ?vehicle_uri ns:hasVehicleIdentifier ?vehicle_id .
            ?vehicle_uri ns:hasManufacturer ?manufacturer .
            ?vehicle_uri ns:hasModel ?model .
            ?reservation_uri rdf:type ns:Reservation .
            ?reservation_uri ns:reservedByVehicle ?vehicle_uri .
            ?reservation_uri ns:hasUser ?user_uri .
            ?reservation_uri ns:hasGS ?gs_uri .
            ?reservation_uri ns:hasReservationIdentifier ?reservation_id
        }
        WHERE {
            ?user_uri rdf:type ns:Person .
            ?user_uri ns:hasName ?name .
            ?user_uri ns:hasPassword ?user_password .
            ?user_uri ns:hasUserIdentifier "%s" .
            OPTIONAL {
                ?user_uri ns:hasVehicle ?vehicle_uri .
                ?vehicle_uri rdf:type ns:Vehicle .
                ?vehicle_uri ns:hasVehicleIdentifier ?vehicle_id .
                ?vehicle_uri ns:hasManufacturer ?manufacturer .
                ?vehicle_uri ns:hasModel ?model .           
                OPTIONAL {
                    ?reservation_uri rdf:type ns:Reservation .
                    ?reservation_uri ns:reservedByVehicle ?vehicle_uri .
                    ?reservation_uri ns:hasUser ?user_uri .
                    ?reservation_uri ns:hasGS ?gs_uri .
                    ?reservation_uri ns:hasReservationIdentifier ?reservation_id
                }
            }
        }"""

        # deleting triples
        try:
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
            kp.load_query_sparql(query % (RDF, NS, user_id, user_id))
            return True
        except Exception as e:
            return False


    # to json
    def to_json(self):

        # return a json representation
        udict = {}
        udict["user_uid"] = self.user_uid
        print self.user_name
        udict["user_name"] = self.user_name.encode("utf-8").decode("unicode_escape")
        udict["user_password"] = self.user_password
        udict["user_uri"] = self.user_uri
        udict["user_vehicles"] = self.vehicles
        udict["user_reservations"] = self.reservations
        return udict

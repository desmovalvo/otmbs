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
    def __init__(self, settings, name = None, slatitude = None, slongitude = None, elatitude = None, elongitude = None):
        
        """Constructor for the GroundStation model"""

        # setting initial attributes
        self.gs_id = None
        self.gs_uri = None
        self.gs_name = name
        self.slatitude = slatitude
        self.slongitude = slongitude
        self.elatitude = elatitude
        self.elongitude = elongitude
        self.sgpsdata_uri = None
        self.egpsdata_uri = None

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
        self.gs_id = self.uuid.split("-")[0]

        # generate URIs for GPSdatas
        self.sgpsdata_uri = NS + str(uuid.uuid4())
        self.egpsdata_uri = NS + str(uuid.uuid4())

        # create the triples
        triples = []
        triples.append(Triple(URI(self.gs_uri), URI(RDF_TYPE), URI(GS_CLASS)))
        triples.append(Triple(URI(self.gs_uri), URI(NS + "hasGSIdentifier"), Literal(self.gs_id)))
        triples.append(Triple(URI(self.gs_uri), URI(NS + "hasName"), Literal(self.gs_name)))
        triples.append(Triple(URI(self.gs_uri), URI(NS + "hasStartGPSData"), URI(self.sgpsdata_uri)))
        triples.append(Triple(URI(self.gs_uri), URI(NS + "hasEndGPSData"), URI(self.egpsdata_uri)))
        triples.append(Triple(URI(self.sgpsdata_uri), URI(NS + "hasLatitude"), Literal(self.slatitude)))
        triples.append(Triple(URI(self.sgpsdata_uri), URI(NS + "hasLongitude"), Literal(self.slongitude)))
        triples.append(Triple(URI(self.egpsdata_uri), URI(NS + "hasLatitude"), Literal(self.elatitude)))
        triples.append(Triple(URI(self.egpsdata_uri), URI(NS + "hasLongitude"), Literal(self.elongitude)))

        # putting triples
        try:
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
            kp.load_rdf_insert(triples)
            return True, self
        except Exception as e:
            return False, None


    # get the list of the ground stations
    def find_gss(self):
        
        """Retrieves Ground Stations from the SIB"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # perform a SPARQL query
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        SELECT ?gs ?gsidentifier ?gsname ?slatitude ?slongitude ?elatitude ?elongitude
        WHERE {
            ?gs rdf:type <%s> .
            ?gs ns:hasGSIdentifier ?gsidentifier .
            ?gs ns:hasName ?gsname .
            ?gs ns:hasStartGPSData ?sgpsdata .
            ?gs ns:hasEndGPSData ?egpsdata .
            ?sgpsdata ns:hasLatitude ?slatitude .
            ?sgpsdata ns:hasLongitude ?slongitude .
            ?egpsdata ns:hasLatitude ?elatitude .
            ?egpsdata ns:hasLongitude ?elongitude .
        }"""
        print query % (RDF, NS, GS_CLASS)
        kp.load_query_sparql(query % (RDF, NS, GS_CLASS))
        results = kp.result_sparql_query           

        # build the models to return
        return_models = []
        for result in results:
            gs_model = GroundStation(self.settings, result[2][2], result[3][2], result[4][2], result[5][2], result[6][2])
            gs_model.gs_uri = result[0][2]
            gs_model.gs_id = result[1][2]
            return_models.append(gs_model)

        # return
        return return_models


    # get the list of the ground stations
    def find_gs(self, gsid):
        
        """Retrieves a single Ground Station from the SIB"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])

        # perform the SPARQL query
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        SELECT ?gs ?gsname ?slatitude ?slongitude ?elatitude ?elongitude
        WHERE {
            ?gs rdf:type <%s> .
            ?gs ns:hasGSIdentifier "%s" .
            ?gs ns:hasName ?gsname .
            ?gs ns:hasStartGPSData ?sgpsdata .
            ?gs ns:hasEndGPSData ?egpsdata .
            ?sgpsdata ns:hasLatitude ?slatitude .
            ?sgpsdata ns:hasLongitude ?slongitude .
            ?egpsdata ns:hasLatitude ?elatitude .
            ?egpsdata ns:hasLongitude ?elongitude .
        }"""
        print query % (RDF, NS, GS_CLASS, gsid)
        kp.load_query_sparql(query % (RDF, NS, GS_CLASS, gsid))
        results = kp.result_sparql_query       
        print results    

        # build the models to return
        gs_model = GroundStation(self.settings)
        for result in results:
            gs_model.gs_uri = result[0][2]
            gs_model.gs_name = result[1][2]
            gs_model.slatitude = result[2][2]
            gs_model.slongitude = result[3][2]
            gs_model.elatitude = result[4][2]
            gs_model.elongitude = result[5][2]
            gs_model.gs_id = gsid

        # return
        return gs_model


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
    def delete(self):

        """Delete the ground station"""

        # build the triple list
        query = """PREFIX rdf:<%s>
        PREFIX ns:<%s>
        DELETE {
            ?gs_uri rdf:type ns:GroundStation .
            ?gs_uri ns:hasGSIdentifier "%s" .
            ?gs_uri ns:hasName ?gsname .
            ?gs_uri ns:hasStartGPSData ?sgpsdata .
            ?gs_uri ns:hasEndGPSData ?egpsdata .
            ?sgpsdata ns:hasLatitude ?slatitude .
            ?sgpsdata ns:hasLongitude ?slongitude .
            ?egpsdata ns:hasLatitude ?elatitude .
            ?egpsdata ns:hasLongitude ?elongitude .
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
            print query % (RDF, NS, self.gs_id, self.gs_id)
            kp.load_query_sparql(query % (RDF, NS, self.gs_id, self.gs_id))
            return True
        except:
            return False

        
    # to json
    def to_json(self):

        """This method returns a JSON representation of the model"""
        
        gdict = {}        
        gdict["gs_uri"] = self.gs_uri
        gdict["gs_id"] = self.gs_id
        gdict["gs_name"] = self.gs_name
        gdict["start_gs_lat"] = self.slatitude
        gdict["start_gs_long"] = self.slongitude
        gdict["end_gs_lat"] = self.elatitude
        gdict["end_gs_long"] = self.elongitude
        return gdict

#!/usr/bin/python

# requirements
from uuid import uuid4
from smart_m3.m3_kp_api import *

def integrate(settings):

    """This function is used to insert new triples
    into the SIB that maintain the compatibility with
    the old dataset"""

    # connect to the SIB
    kp = m3_kp_api(False, settings["sib_host"], settings["sib_port"])    

    # add the triples
    user_ids = ["ovidiuv", 
                "FEEE7C9586CBD741", 
                "70D15A009731E0AF",
                "giuseppeb",
                "stefanob",
                "enriquer",
                "tullios"]

    for user_id in user_ids:

        # generate a vehicle id
        vid = str(uuid.uuid4())

        # perform the update
        print "updating user " + user_id
        kp.load_query_sparql("""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ns: <http://www.m3.com/2012/05/m3/ioe-ontology.owl#>
        INSERT {
            ?personuri ns:hasPassword "%s" .
        }
        WHERE {
            ?personuri rdf:type ns:Person .
            ?personuri ns:hasUserIdentifier "%s" .
        }""" % (user_id, user_id))

        print "updating his vehicle"
        kp.load_query_sparql("""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ns: <http://www.m3.com/2012/05/m3/ioe-ontology.owl#>
        INSERT {
            ?vehicleuri rdf:type ns:Vehicle .
            ?vehicleuri ns:hasVehicleIdentifier "%s"
        }
        WHERE {
            ?personuri ns:hasUserIdentifier "%s" .
            ?personuri ns:hasVehicle ?vehicleuri
        }""" % (vid, user_id))        

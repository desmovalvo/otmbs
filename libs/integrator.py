#!/usr/bin/python

def integrate(settings):

    """This function is used to insert new triples
    into the SIB that maintain the compatibility with
    the old dataset"""

    # connect to the SIB
    kp = m3_kp_api(False, settings["sib_host"], settings["sib_port"])    

    # add passwords to the users
    user_ids = ["ovidiuv", 
                "FEEE7C9586CBD741", 
                "70D15A009731E0AF",
                "giuseppeb",
                "stefanob",
                "enriquer",
                "tullios"]

    for user_id in user_ids:

        kp.load_query_sparql("""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ns: <http://www.m3.com/2012/05/m3/ioe-ontology.owl#>
        INSERT {
            ?personuri ns:hasPassword "%s"
        }
        WHERE {
            ?personuri rdf:type ns:Person .
            ?personuri ns:hasUserIdentifier "%s"
        }""" % (user_id, user_id))

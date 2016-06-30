#!/usr/bin/python

"""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ns: <http://www.m3.com/2012/05/m3/ioe-ontology.owl#>
ASK WHERE {
   ?v rdf:type ns:Vehicle .
   ?v ns:hasVechicleIdentifier "%s" .
   ?u rdf:type ns:Person .
   ?u ns:hasUserIdentifier "%s" .
   ?g rdf:type ns:GroundStation .
   ?g ns:hasGsIdentifier "%s" .
   ?r rdf:type ns:Reservation .
   ?r ns:hasUser ?u .
   ?r ns:hasVehicle ?v .
   ?r ns:hasGS ?g
}"""

#########################################################
#
# The following query is used to determine whether the 
# required user_uid is valid, or is already in use
#
######################################################### 

user_exists = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ns: <http://www.m3.com/2012/05/m3/ioe-ontology.owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
ASK WHERE { 
	?person_uri rdf:type ns:Person .
  	?person_uri ns:hasUserIdentifier "%s"
}"""

        

        

      

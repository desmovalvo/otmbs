#!/usr/bin/python

users_query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ns: <http://www.m3.com/2012/05/m3/ioe-ontology.owl#>
SELECT ?uri ?name ?id
WHERE {
   ?uri rdf:type ns:Person .
   ?uri ns:hasName ?name .
   ?uri ns:hasUserIdentifier ?id
}"""

vehicles_query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ns: <http://www.m3.com/2012/05/m3/ioe-ontology.owl#>
SELECT ?uri ?name ?manu ?model ?gps ?batt
WHERE {
   ?user_uri ns:hasUserIdentifier "%s" .
   ?user_uri ns:hasVehicle ?uri .
   ?uri ns:hasName ?name .
   ?uri ns:hasManufacturer ?manu .
   ?uri ns:hasModel ?model .
   ?uri ns:hasGPSData ?gps .
   ?uri ns:hasBatteryData ?batt .
}"""

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

gcps_query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ns: <http://www.m3.com/2012/05/m3/ioe-ontology.owl#>
SELECT ?gcp ?gcpName ?gps ?lat ?lon 
WHERE{
   ?gcp rdf:type ns:GridConnectionPoint .
   ?gcp ns:hasGPSData ?gps .
   ?gps ns:hasGPSLatitude ?lat .
   ?gps ns:hasGPSLongitude ?lon .
   ?gcp ns:hasName ?gcpName
}"""

reservations_query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ns: <http://www.m3.com/2012/05/m3/ioe-ontology.owl#>
SELECT ?res ?evse ?veh ?from ?to ?pri ?bid
WHERE {
   ?user_uri ns:hasUserIdentifier "%s" .
   ?res ns:reservationHasUser ?user_uri .
   ?res ns:reservedByVehicle ?veh .
   ?res ns:isBidirectional ?bid .
   ?res ns:hasEVSE ?evse .
   ?res ns:hasTimeInterval ?time .
   ?time ns:hasFromTimeMillisec ?from .
   ?res ns:hasPrice ?priu .
   ?priu ns:hasValue ?pri .
   ?time ns:hasToTimeMillisec ?to
}"""

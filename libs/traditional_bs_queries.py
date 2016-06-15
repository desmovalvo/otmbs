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
   OPTIONAL {
      ?uri ns:hasGPSData ?gps } .
   OPTIONAL {
      ?uri ns:hasBatteryData ?batt }
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

evses_query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ns: <http://www.m3.com/2012/05/m3/ioe-ontology.owl#>
SELECT ?id ?evse ?conn ?lst ?stat ?typ ?evseName ?prof ?price ?cin ?cout ?pow ?volt
WHERE {
   ?gcp ns:hasName "%s".
   ?gcp ns:hasEVSE ?evse .
   ?evse ns:hasConnector ?conn .
   ?evse ns:hasChargeProfile ?prof .
   ?evse ns:hasReservationList ?lst .
   ?evse ns:hasEVSEIdentifier ?id .
   ?conn ns:hasStatus ?stat .
   ?evse ns:hasName ?evseName .
   ?prof ns:hasPower ?powu .
   ?prof ns:hasVoltage ?voltu .
   ?prof ns:hasPrice ?priu .
   ?prof ns:hasMaxCurrentDensityOut ?coutu .
   ?prof ns:hasMaxCurrentDensityIn ?cinu .
   ?powu ns:hasValue ?pow .
   ?voltu ns:hasValue ?volt .
   ?priu ns:hasValue ?price .
   ?coutu ns:hasValue ?cout .
   ?cinu ns:hasValue ?cin .
   ?conn ns:hasConnectorType ?type
}"""

chargeresponse_query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ns: <http://www.m3.com/2012/05/m3/ioe-ontology.owl#>
SELECT ?req ?opt ?gcp ?gcpName ?evse ?evseName ?veh ?user ?price ?from ?to ?lat ?lon 
WHERE {
   <%s> ns:hasRelatedRequest ?req .
   <%s> ns:hasChargeOption ?opt .
   ?opt ns:optionHasEVSE ?evse .
   ?evse ns:hasName ?evseName .
   ?opt ns:hasGridConnectionPoint ?gcp .
   ?gcp ns:hasName ?gcpName .
   ?opt ns:hasRequestingVehicle ?veh .
   ?opt ns:hasRequestingUser ?user .
   ?opt ns:hasTotalPrice ?pri .
   ?pri ns:hasValue ?price .
   ?opt ns:hasTimeInterval ?tim .
   ?tim ns:hasFromTimeMillisec ?from .
   ?tim ns:hasToTimeMillisec ?to .
   ?opt ns:hasGCPPosition ?pos .
   ?pos ns:hasGPSLatitude ?lat .
   ?pos ns:hasGPSLongitude ?lon
}"""

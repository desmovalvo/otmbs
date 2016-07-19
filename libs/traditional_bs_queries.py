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
SELECT ?uri ?name ?manu ?model ?gps ?batt ?vehicle_id
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
   OPTIONAL {
      ?uri ns:hasVehicleIdentifier ?vehicle_id }
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

evses_query_all = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ns: <http://www.m3.com/2012/05/m3/ioe-ontology.owl#>
SELECT ?id ?evse ?conn ?lst ?stat ?typ ?evseName ?prof ?price ?cin ?cout ?pow ?volt ?evsename
WHERE {
   ?gcp ns:hasName ?evsename .
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

tra_reservation_exists_query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ns: <http://www.m3.com/2012/05/m3/ioe-ontology.owl#>
ASK
WHERE {
    ?user_uri ns:hasUserIdentifier "%s" .
    ?res ns:reservationHasUser ?user_uri .
    ?res ns:reservedByVehicle ?veh .
    ?veh ns:hasPlate "%s" .
    ?res ns:isBidirectional ?bid .
    ?res ns:hasEVSE ?evse .
    ?evse ns:hasEVSEIdentifier "%s" .
    ?res ns:hasTimeInterval ?time .
    ?time ns:hasFromTimeMillisec ?from .
    ?res ns:hasPrice ?priu .
    ?priu ns:hasValue ?pri .
    ?time ns:hasToTimeMillisec ?to
}"""

evse_status_query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ns: <http://www.m3.com/2012/05/m3/ioe-ontology.owl#>
SELECT ?r ?t ?timefrom ?timeto ?userid
WHERE { 
    ?r rdf:type ns:Reservation .
    ?r ns:hasEVSE ?evse .
    ?evse ns:hasEVSEIdentifier "%s" .
    ?r ns:hasTimeInterval ?t .
    ?t rdf:type ns:TimeInterval .
    ?t ns:hasFromTimeMillisec ?timefrom .
    ?t ns:hasToTimeMillisec ?timeto .
    ?r ns:reservationHasUser ?user .
    ?user ns:hasUserIdentifier ?userid
}"""

user_auth_query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://www.m3.com/2012/05/m3/ioe-ontology.owl#>
SELECT ?userid ?evseid ?timefrom ?timeto
WHERE { 
  ?r rdf:type ns:Reservation .
  ?r ns:hasTimeInterval ?t .
  ?t ns:hasToTimeMillisec ?timeto .
  ?t ns:hasFromTimeMillisec ?timefrom .
  ?r ns:hasEVSE ?evse .
  ?evse ns:hasEVSEIdentifier "%s" .
  ?r ns:reservationHasUser ?user .
  ?user ns:hasUserIdentifier "%s"
}"""

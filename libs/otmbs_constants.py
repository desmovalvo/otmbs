#!/usr/bin/python

# output format
JSON = 0
HTML = 1

# RDF Namespace
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

# OTMBS Namespace
NS = "http://www.m3.com/2012/05/m3/ioe-ontology.owl#"

# Common properties
RDF_TYPE = RDF + "type"

# Common classes
PERSON_CLASS = NS + "Person"
VEHICLE_CLASS = NS + "Vehicle"
GPSDATA_CLASS = NS + "GPSData"
GS_CLASS = NS + "GroundStation"
RESERVATION_CLASS = NS + "Reservation"

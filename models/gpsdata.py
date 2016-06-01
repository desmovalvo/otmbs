#!/usr/bin/python

# system-wide requirements
import uuid
from os import sys, path
from smart_m3.m3_kp_api import *

# local requirements
from libs.otmbs_constants import *

# GPSData class
class GPSData:

    """This class is responsible for the mapping between the
    service and the SIB content for the GPSData"""

    # constructor
    def __init__(self, settings, latitude = None, longitude = None):
        
        """Constructor for the GroundStation model"""

        # setting initial attributes
        self.gpsdata_uri = None
        self.latitude = None
        self.longitude = None

        # store settings
        self.settings = settings

        
    # create
    def create(self):

        """This method is used to create the gpsdana
        by storing its triples into the SIB"""

        # connect to the SIB
        kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])    

        # generate an uuid
        self.uuid = str(uuid.uuid4())
        self.gpsdata_uri = NS + self.uuid

        # create the triples
        triples = []
        triples.append(Triple(URI(self.gpsdata_uri), URI(RDF_TYPE), URI(GPSDATA_CLASS)))
        triples.append(Triple(URI(self.gpsdata_uri), URI(NS + "hasLatitude"), Literal(self.latitude)))
        triples.append(Triple(URI(self.gpsdata_uri), URI(NS + "hasLongitude"), Literal(self.longitude)))

        # putting triples
        try:
            kp = m3_kp_api(False, self.settings["sib_host"], self.settings["sib_port"])
            kp.load_rdf_insert(triples)
            return True
        except Exception as e:
            return False

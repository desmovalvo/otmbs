#!/usr/bin/python

# system-wide requirements
from rdflib import *
from rdflib.plugins.parsers.notation3 import N3Parser
from smart_m3.m3_kp import KP
from smart_m3.m3_kp import URI
from smart_m3.m3_kp_api import m3_kp_api
from smart_m3.m3_kp import Triple as KTriple
from smart_m3.m3_kp import Literal as KLiteral

# N3KBLoader
class N3KBLoaderException(Exception):

    # constructor
    def __init__(self, value):
        self.parameter = value

    # strify
    def __str__(self):
        return repr(self.parameter)


# the class
class N3KBLoader:

    """This class is used to load N3 files into the SIB.
    NOTE: this class will be modified to support different
    types of files."""

    # constructor
    def __init__(self, settings):
        
        """Constructor for the N3KBLoader class"""

        # setting 
        self.sib_host = settings["sib_host"]
        self.sib_port = settings["sib_port"]
        self.block_size = settings["block_size"]
        
    # loader
    def load_n3file(self, filename):
        
        """This method load the content of the N3 file into the SIB"""

        # parse the file
        res = None
        g = Graph()
        try:
            res = g.parse(filename, format="n3")
        except Exception as e:
            raise N3KBLoaderException(str(e))

        # build the triple list
        triple_list = []
        for triple in res:

            # getting fields
            s = []
            for field in triple:

                if type(field).__name__  == "URIRef":
                    s.append(URI(field))            
                elif type(field).__name__  == "Literal":
                    s.append(KLiteral(field))

            # add the triple to the list
            triple_list.append(KTriple(s[0], s[1], s[2]))

        # place data into the SIB
        block = []
        for triple in triple_list:
            
            # add the triple to the block
            block.append(triple)

            # check the block_size and in case insert triples
            if len(block) == self.block_size:
                
                # insert triples
                kp = m3_kp_api(False, self.sib_host, self.sib_port)           
                kp.load_rdf_insert(block)
                block = []

        # insert the remaining triples
        kp = m3_kp_api(False, self.sib_host, self.sib_port)        
        kp.load_rdf_insert(block)

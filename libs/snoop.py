#!/usr/bin/python

# system wide requirements
from smart_m3.m3_kp_api import *

# local requirements
from otm_bs_queries import *
from traditional_bs_queries import *

# check user uid
def user_uid_available(settings, user_uid):

    """This method is used to verify if a user uid
    is free or already in use. It returns False if 
    the user uid is free, True otherwise"""

    # connect to the sib
    kp = m3_kp_api(False, settings["sib_host"], settings["sib_port"])
    
    # perform the query
    kp.load_query_sparql(user_exists_query % user_uid)
    result = str(kp.result_sparql_query[0][0])

    # return True or False
    if result == "true":
        return False
    else:
        return True


# check reservation
def reservation_exists(settings, user_uid, vehicle_snoop, gs_id, res_type):

    """This method is used to check if a reservation
    with the given details exists. If affirmative returns
    True, False otherwise."""
    
    # connect to the sib
    kp = m3_kp_api(False, settings["sib_host"], settings["sib_port"])

    # check reservation type
    if res_type == "OTM":
    
        # perform the query
        kp.load_query_sparql(reservation_exists_query % (vehicle_id, user_uid, gs_id))
        print reservation_exists_query % (vehicle_id, user_uid, gs_id)
        result = str(kp.result_sparql_query[0][0])

    elif res_type == "TRA":

        # perform the query
        kp.load_query_sparql(tra_reservation_exists_query % (user_uid, vehicle_id, gs_id))
        print tra_reservation_exists_query % (user_uid, vehicle_id, gs_id)
        result = str(kp.result_sparql_query[0][0])

    # return True or False
    if result == "true":
        return True
    else:
        return False

#!/usr/bin/python

ALF_ACTIONS = {
    # index
    "showreservations":{"method":"GET", "name":"reservations_showall"},
    "showvehicles":{"method":"GET", "name":"vehicles_showall"},
    "showusers":{"method":"GET", "name":"users_showall"},
    "showgss":{"method":"GET", "name":"gss_showall"},
    # show
    "showreservation":{"method":"GET", "name":"reservations_show"},
    "showvehicle":{"method":"GET", "name":"vehicles_show"},
    "showuser":{"method":"GET", "name":"users_show"},
    "showgs":{"method":"GET", "name":"gss_show"},    
    # delete
    "deletereservation":{"method":"GET", "name":"reservations_delete"},
    "deletevehicle":{"method":"GET", "name":"vehicles_delete"},
    "deleteuser":{"method":"GET", "name":"users_delete"},
    "deletegs":{"method":"GET", "name":"gss_delete"},    
    # create
    "createreservation":{"method":"POST", "name":"reservations_create"},
    "createvehicle":{"method":"POST", "name":"vehicles_create"},
    "createuser":{"method":"POST", "name":"users_create"},
    "creategs":{"method":"POST", "name":"gss_create"},        
    # update
    "updatereservation":{"method":"POST", "name":"reservations_update"},
    "updatevehicle":{"method":"POST", "name":"vehicles_update"},
    "updateuser":{"method":"POST", "name":"users_update"},
    "updategs":{"method":"POST", "name":"gss_update"},    
}

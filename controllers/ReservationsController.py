#!/usr/bin/python

# import models
from models.reservation import *

class ReservationsController:

    """The controller for the Reservations"""

    # constructor
    def __init__(self, settings):
        
        """Constructor for the Reservation controller"""

        # store settings
        self.settings = settings


    # show reservations
    def show_reservations(self):

        """Show all the Reservations"""

        # create an instance of the model
        reserv_model = Reservation(self.settings)

        # query the model
        results = []
        results = reserv_model.find_reservations()

        # return the result in a json-ifiable form
        json_results = []
        for reservation in results:
            json_reservation = {}
            for field in reservation:
                json_reservation[field[0]] = field[2]
            json_results.append(json_reservation)

        # return
        print json_results
        return json_results


    # show reservation
    def show_reservation(self, reservation_id):

        """Show all the Reservations"""

        # create an instance of the model
        reserv_model = Reservation(self.settings)

        # query the model
        results = []
        results = reserv_model.find_reservation(reservation_id)

        # return the result in a json-ifiable form
        json_reservation = {}
        for reservation in results:
            for field in reservation:
                json_reservation[field[0]] = field[2]

        # add the id
        json_reservation["reservation_id"] = reservation_id

        # return
        print json_reservation
        return json_reservation


    # delete
    def delete_reservation(self, res_id):
        
        # create an instance of the model
        rm = Reservation(self.settings)
        
        # delete
        status = rm.delete(res_id)

        # return
        return status


    # create reservation
    def create_reservation(self, gs_id, vehicle_id):

        """Method to create a new Reservation"""

        print "CONTROLLER"

        # get the vehicle_id and user_uid
        vehicle_uid = vehicle_id.split("|")[0]
        user_uid = vehicle_id.split("|")[1]

        # create the reservation
        reservation = Reservation(self.settings, gs_id, vehicle_uid, user_uid)
        status = reservation.create()

        print "CREATED" 

        # return
        if status:
            return True

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
        results = reserv_model.find_reservations()

        # return the result in a json-ifiable form
        json_results = []
        for reservation in results:
            json_results.append(reservation.to_json())

        # return
        print json_results
        return json_results


    # show reservation
    def show_reservation(self, reservation_id):

        """Show all the Reservations"""

        # create an instance of the model
        reserv_model = Reservation(self.settings)

        # query the model
        r = reserv_model.find_reservation(reservation_id)

        # return the result in a json-ifiable form
        json_reservation = r.to_json()

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

        # get the vehicle_id and user_uid
        vehicle_uid = vehicle_id.split("|")[0]
        user_uid = vehicle_id.split("|")[1]

        # create the reservation
        reservation = Reservation(self.settings, gs_id, vehicle_uid, user_uid)
        status = reservation.create()

        # return
        if status:
            return True


    # edit reservation
    def update_reservation(self, reservation_id, gs_id, usercar):

        """Method to update a Reservation"""

        print "RCONTRO?AEOUAEUART"

        # split user and car
        user_id = usercar.split("|")[1]
        vehicle_id = usercar.split("|")[0]

        # find the reservation
        reserv_model = Reservation(self.settings)
        r = reserv_model.find_reservation(reservation_id)

        # update the reservation
        r.update(gs_id, vehicle_id, user_id)

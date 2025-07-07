from flask_restful import Resource, fields, reqparse, marshal_with
from flask import request
from sqlalchemy import or_
from models.models import db, User, ParkingLot, ParkingSpot, Reservation
from .exceptions import ValidationError, NotFoundError, MissingFieldsError
from datetime import datetime, timezone, timedelta
from decimal import Decimal

IST = timezone(timedelta(hours=5, minutes=30))

reservation_book_fields = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'lot_id': fields.Integer,
    'prime_location_name': fields.String
}

reservation_release_fields = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'lot_id': fields.Integer,
    'spot_id': fields.Integer,
    'vehicle_num': fields.String,
    'prime_location_name': fields.String,
    'formatted_parking_time': fields.String,
    'formatted_leaving_time': fields.String
}

user_reservation_history_fields = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'lot_id': fields.Integer,
    'prime_location_name': fields.String,
    'vehicle_num': fields.String,
    'formatted_parking_time': fields.String,
    'duration': fields.String,
    'parking_cost': fields.Float,
}

admin_reservation_view_fields = {
    'id': fields.Integer,
    'spot_id': fields.Integer,
    'username': fields.String,
    'prime_location_name': fields.String,
    'vehicle_num': fields.String,
    'formatted_parking_time': fields.String,
    'duration': fields.String,
    'parking_cost': fields.Float,
}

reservation_book_parser = reqparse.RequestParser()
reservation_book_parser.add_argument('vehicle_num')

class ReservationBookAPI(Resource):
    @marshal_with(reservation_book_fields)
    def get(self, user_id, lot_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("User not found.")
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            raise NotFoundError("Parking lot not found.")
        spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
        if not spot:
            raise NotFoundError("No available spot in this lot.")
        spot.user_id = user_id
        spot.prime_location_name = spot.lot.prime_location_name
        return spot
    
    def post(self, user_id, lot_id):
        args = reservation_book_parser.parse_args()
        if not args['vehicle_num']:
            raise MissingFieldsError("Vehicle Number is required.")
        if len(args['vehicle_num']) != 10:
            raise ValidationError("Vehicle Number must be exactly 10 characters long.")
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("User not found.")
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            raise NotFoundError("Parking lot not found.")
        spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
        if not spot:
            raise NotFoundError("No available spot in this lot.")
        if lot.filled_spots >= lot.max_spots:
            raise NotFoundError("No available spot in this lot.")
        existing_reservations = Reservation.query.filter_by(leaving_time=None).all()
        for reservation in existing_reservations:
            if reservation.vehicle_num == args['vehicle_num']:
                raise ValidationError("This vehicle already has an active reservation.")
        reservation = Reservation(spot_id=spot.id, user_id=user_id, vehicle_num=args["vehicle_num"])
        spot.status = 'O'
        lot.filled_spots += 1
        db.session.add(reservation)
        db.session.commit()
        return {"message": "Reservation created."}, 201

class ReservationReleaseAPI(Resource):
    @marshal_with(reservation_release_fields)
    def get(self, reservation_id):
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            raise NotFoundError("Reservation not found.")
        reservation.lot_id = reservation.spot.lot.id
        reservation.prime_location_name = reservation.spot.lot.prime_location_name
        reservation.formatted_parking_time = reservation.parking_time.replace(tzinfo=timezone.utc).astimezone(IST).strftime('%Y-%m-%d | %I:%M %p')
        reservation.formatted_leaving_time = datetime.now(timezone.utc).replace(tzinfo=timezone.utc).astimezone(IST).strftime('%Y-%m-%d | %I:%M %p')
        return reservation

    def put(self, reservation_id):
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            raise NotFoundError("Reservation not found.")
        if reservation.leaving_time != None:
            raise ValidationError("Reservation has already been released.")
        now = datetime.now(timezone.utc)
        reservation.leaving_time = now
        parking_time = reservation.parking_time.replace(tzinfo=timezone.utc).astimezone(IST)
        duration_hours = Decimal((now - parking_time).total_seconds()) / Decimal(3600)
        cost = Decimal(duration_hours) * reservation.spot.lot.price
        reservation.parking_cost = cost
        reservation.spot.status = 'A'
        reservation.spot.lot.filled_spots -= 1
        reservation.spot.lot.revenue_collected += cost
        db.session.commit()
        return {'user_id': reservation.user.id}

class UserReservationHistoryAPI(Resource):
    @marshal_with(user_reservation_history_fields)
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("User not found.")
        search = request.args.get("search", "").lower().strip()
        query = Reservation.query.filter(Reservation.user_id == user_id, Reservation.leaving_time != None)
        if search:
            keyword = f"%{search}%"
            query = query.join(ParkingSpot,Reservation.spot).join(ParkingLot,ParkingSpot.lot).filter(
                or_(ParkingLot.prime_location_name.ilike(keyword), Reservation.vehicle_num.ilike(keyword)))
        reservations = query.all()
        for reservation in reservations:
            reservation.parking_time = reservation.parking_time.replace(tzinfo=timezone.utc).astimezone(IST)
            reservation.leaving_time = reservation.leaving_time.replace(tzinfo=timezone.utc).astimezone(IST)
            duration_min = Decimal((reservation.leaving_time - reservation.parking_time).total_seconds()) / Decimal(60)
            mins = int(duration_min)
            if mins < 1:
                reservation.duration = "Less than a minute"
            elif mins >= 60:
                reservation.duration = f"{mins // 60}h {mins % 60}m"
            else:
                reservation.duration = f"{mins}m"
            reservation.user_id = reservation.user.id
            reservation.lot_id = reservation.spot.lot.id
            reservation.prime_location_name = reservation.spot.lot.prime_location_name
            reservation.formatted_parking_time = reservation.parking_time.astimezone(IST).strftime('%Y-%m-%d | %I:%M %p')
            reservation.formatted_leaving_time = reservation.leaving_time.astimezone(IST).strftime('%Y-%m-%d | %I:%M %p')
        return reservations

class AdminReservationViewAPI(Resource):
    @marshal_with(admin_reservation_view_fields)
    def get(self):
        search = request.args.get("search", "").lower().strip()
        query = Reservation.query.filter(Reservation.leaving_time != None)
        if search:
            keyword = f"%{search}%"
            query = query.join(ParkingSpot,Reservation.spot).join(User,Reservation.user).join(ParkingLot,ParkingSpot.lot).filter(
                or_(ParkingSpot.id.cast(db.String).ilike(keyword), User.user_name.ilike(keyword), ParkingLot.prime_location_name.ilike(keyword), Reservation.vehicle_num.ilike(keyword)))
        reservations = query.all()
        for reservation in reservations:
            reservation.parking_time = reservation.parking_time.replace(tzinfo=timezone.utc).astimezone(IST)
            reservation.leaving_time = reservation.leaving_time.replace(tzinfo=timezone.utc).astimezone(IST)
            duration_min = Decimal((reservation.leaving_time - reservation.parking_time).total_seconds()) / Decimal(60)
            mins = int(duration_min)
            if mins < 1:
                reservation.duration = "Less than a minute"
            elif mins >= 60:
                reservation.duration = f"{mins // 60}h {mins % 60}m"
            else:
                reservation.duration = f"{mins}m"
            reservation.spot_id = reservation.spot.id
            reservation.username = reservation.user.user_name
            reservation.prime_location_name = reservation.spot.lot.prime_location_name
            reservation.formatted_parking_time = reservation.parking_time.astimezone(IST).strftime('%Y-%m-%d | %I:%M %p')
        return reservations
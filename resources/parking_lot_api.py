from flask_restful import Resource, fields, reqparse, marshal_with, marshal
from flask import jsonify
from models.models import db, ParkingLot, ParkingSpot, Reservation
from .exceptions import ValidationError, NotFoundError, AlreadyExistError, MissingFieldsError
from datetime import timezone, timedelta
from decimal import Decimal

IST = timezone(timedelta(hours=5, minutes=30))

lot_fields = {
    'id': fields.Integer,
    'prime_location_name': fields.String,
    'address': fields.String,
    'pincode': fields.String,
    'price': fields.Float,
    'max_spots': fields.Integer,
}

spot_fields = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'user_name': fields.String,
    'vehicle_num': fields.String,
    'formatted_parking_time': fields.String
}

lot_parser = reqparse.RequestParser()
lot_parser.add_argument("prime_location_name")
lot_parser.add_argument("address")
lot_parser.add_argument("pincode")
lot_parser.add_argument("price")
lot_parser.add_argument("max_spots")

class ParkingLotAPI(Resource):
    @marshal_with(lot_fields)
    def get(self, lot_id):
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            raise NotFoundError("Parking lot not found.")
        return lot
    
    def post(self):
        args = lot_parser.parse_args()
        if not all([args['prime_location_name'], args['address'], args['pincode'], args['price'], args['max_spots']]):
            raise MissingFieldsError("All fields are required.")
        existing_lot = ParkingLot.query.filter_by(prime_location_name=args['prime_location_name']).first()
        if existing_lot:
            raise AlreadyExistError("Prime Location Name already exists.")
        if not args['pincode'].isdigit() or len(args['pincode']) != 6:
            raise ValidationError("Pincode must be a 6-digit number.")
        try:
            price = Decimal(args['price'])
        except:
            raise ValidationError("Price must be a valid number.")
        if price <= Decimal('0'):
                raise ValidationError("Price must be a positive number.")
        try:
            max_spots = int(args['max_spots'])
        except:
            raise ValidationError("Maximum Spots must be a valid integer.")
        if max_spots <= 0:
                raise ValidationError("Maximum Spots must be a positive integer.")
        lot = ParkingLot(prime_location_name=args['prime_location_name'], address=args['address'], pincode=args['pincode'], price=price, max_spots=max_spots)
        db.session.add(lot)
        db.session.commit()
        for _ in range(max_spots):
            db.session.add(ParkingSpot(lot_id=lot.id))
        db.session.commit()
        return jsonify({"message": "Parking lot and its spots created."}), 201

    def put(self, lot_id):
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            raise NotFoundError("Parking lot not found.")
        args = lot_parser.parse_args()
        if not all([args['prime_location_name'], args['address'], args['pincode'], args['price'], args['max_spots']]):
            raise MissingFieldsError("All fields are required.")
        if args['prime_location_name'] != lot.prime_location_name:
            existing_lot = ParkingLot.query.filter_by(prime_location_name=args['prime_location_name']).first()
            if existing_lot and existing_lot.id != lot_id:
                raise AlreadyExistError("Prime Location Name already exists.")
        if not args['pincode'].isdigit() or len(args['pincode']) != 6:
            raise ValidationError("Pincode must be a 6-digit number.")
        try:
            price = Decimal(args['price'])
        except:
            raise ValidationError("Price must be a valid number.")
        if price <= Decimal('0'):
                raise ValidationError("Price must be a positive number.")
        try:
            max_spots = int(args['max_spots'])
        except:
            raise ValidationError("Maximum Spots must be a valid integer.")
        if max_spots <= 0:
                raise ValidationError("Maximum Spots must be a positive integer.")
        lot.prime_location_name = args["prime_location_name"]
        lot.address = args["address"]
        lot.pincode = args["pincode"]
        lot.price = price
        lot.max_spots = max_spots
        db.session.commit()
        return jsonify({"message": "Parking lot updated."})

    def delete(self, lot_id):
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            raise NotFoundError("Parking lot not found.")
        if any(spot.status == 'O' for spot in lot.spots):
            raise ValidationError("Parking lot has active reservations.")
        db.session.delete(lot)
        db.session.commit()
        return jsonify({"message": "Parking lot deleted."})

class OccupiedParkingSpotsAPI(Resource):
    def get(self, lot_id):
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            raise NotFoundError("Parking lot not found.")
        spots = [spot for spot in lot.spots if spot.status == 'O']
        for spot in spots:
            active_reservation = Reservation.query.filter_by(spot_id=spot.id, leaving_time=None).first()
            spot.user_id = active_reservation.user.id
            spot.user_name = active_reservation.user.user_name
            spot.vehicle_num = active_reservation.vehicle_num
            spot.formatted_parking_time = active_reservation.parking_time.replace(tzinfo=timezone.utc).astimezone(IST).strftime('%Y-%m-%d | %I:%M %p')
        return jsonify({"prime_location_name": spot.lot.prime_location_name, "spots": marshal(spots, spot_fields)})
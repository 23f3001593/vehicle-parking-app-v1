from flask_restful import Resource, fields, reqparse, marshal_with
from flask import jsonify, request
from sqlalchemy import or_
from models.models import db, User, ParkingLot, Reservation
from resources.exceptions import ValidationError, NotFoundError, AlreadyExistError, MissingFieldsError
from datetime import timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

user_fields = {
    'user_id': fields.Integer,
    'user_name': fields.String,
    'password': fields.String,
    'full_name': fields.String,
    'address': fields.String,
    'pincode': fields.String,
    'role': fields.String
}

reservation_fields = {
    'id': fields.Integer,
    'lot_id': fields.Integer,
    'prime_location_name': fields.String,
    'vehicle_num': fields.String,
    'formatted_parking_time': fields.String
}

lot_fields = {
    'id': fields.Integer,
    'prime_location_name': fields.String,
    'address': fields.String,
    'price': fields.Float,
    'available_spots': fields.Integer
}

user_dashboard_fields = {
    'user_id': fields.Integer,
    'user': fields.Nested(user_fields),
    'ongoing_reservations': fields.List(fields.Nested(reservation_fields)),
    'lots': fields.List(fields.Nested(lot_fields))
}

admin_dashboard_fields = {
    'id': fields.Integer,
    'prime_location_name': fields.String,
    'filled_spots': fields.Integer,
    'max_spots': fields.Integer,
    'revenue_collected': fields.Float
}

registered_user_fields = {
    'id': fields.Integer,
    'user_name': fields.String,
    'full_name': fields.String,
    'address': fields.String,
    'pincode': fields.String
}

user_parser = reqparse.RequestParser()
user_parser.add_argument("user_name")
user_parser.add_argument("password")
user_parser.add_argument("full_name")
user_parser.add_argument("address")
user_parser.add_argument("pincode")

class UserAPI(Resource):
    @marshal_with(user_fields)
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("User not found.")
        user.user_id = user.id
        return user

    def put(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("User not found.")
        args = user_parser.parse_args()
        if not all([args['user_name'], args['password'], args['full_name'], args['address'], args['pincode']]):
            raise MissingFieldsError("All fields are required.")
        if args['user_name'] != user.user_name:
            existing_user = User.query.filter_by(user_name=args['user_name']).first()
            if existing_user and existing_user.id != user_id:
                raise AlreadyExistError("Username already exists.")
        if not args['pincode'].isdigit() or len(args['pincode']) != 6:
            raise ValidationError("Pincode must be a 6-digit number.")
        user.user_name = args["user_name"]
        user.password = args["password"]
        user.full_name = args["full_name"]
        user.address = args["address"]
        user.pincode = args["pincode"]
        db.session.commit()
        return jsonify({"message": "Profile updated."})

    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("User not found.")
        if user.role == 'admin':
            raise ValidationError("Admin account cannot be deleted.")
        ongoing_reservation = Reservation.query.filter_by(user_id=user_id, leaving_time=None).first()
        if ongoing_reservation:
            raise ValidationError("Cannot delete account due to ongoing reservation.")
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted."})

class UserDashboardAPI(Resource):
    @marshal_with(user_dashboard_fields)
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("User not found.")
        if user.role == "admin":
            raise ValidationError("This user is not a regular user.")
        ongoing_reservations = Reservation.query.filter_by(user_id=user_id, leaving_time=None).all()
        for reservation in ongoing_reservations:
            reservation.lot_id = reservation.spot.lot.id
            reservation.prime_location_name = reservation.spot.lot.prime_location_name
            reservation.formatted_parking_time = reservation.parking_time.replace(tzinfo=timezone.utc).astimezone(IST).strftime('%Y-%m-%d | %I:%M %p')
        lots = ParkingLot.query.filter(ParkingLot.filled_spots < ParkingLot.max_spots).all()
        for lot in lots:
            lot.available_spots = lot.max_spots - lot.filled_spots
        return {"user_id": user.id, "user": user, "ongoing_reservations": ongoing_reservations, "lots": lots}

class AdminDashboardAPI(Resource):
    @marshal_with(admin_dashboard_fields)
    def get(self):
        lots = ParkingLot.query.all()
        return lots

class RegisteredUsersAPI(Resource):
    @marshal_with(registered_user_fields)
    def get(self):
        search = request.args.get("search", "").lower().strip()
        query = User.query.filter_by(role='user')
        if search:
            keyword = f"%{search}%"
            query = query.filter(or_(User.user_name.ilike(keyword), User.full_name.ilike(keyword), User.address.ilike(keyword), User.pincode.ilike(keyword)))
        users = query.all()
        return users
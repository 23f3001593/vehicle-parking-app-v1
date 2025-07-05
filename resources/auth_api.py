from flask_restful import Resource, fields, reqparse, marshal_with
from models.models import db, User
from .exceptions import ValidationError, NotFoundError, AlreadyExistError, MissingFieldsError

user_fields = {
    'id': fields.Integer,
    'role': fields.String
}

login_parser = reqparse.RequestParser()
login_parser.add_argument('user_name')
login_parser.add_argument('password')

register_parser = reqparse.RequestParser()
register_parser.add_argument('user_name')
register_parser.add_argument('password')
register_parser.add_argument('fullname')
register_parser.add_argument('address')
register_parser.add_argument('pincode')

class LoginAPI(Resource):
    @marshal_with(user_fields)
    def post(self):
        args = login_parser.parse_args()
        if not all([args['user_name'], args['password']]):
            raise MissingFieldsError("All fields are required.")
        user = User.query.filter_by(user_name=args['user_name']).first()
        if not user or user.password != args['password']:
            raise NotFoundError("Invalid username or password.")
        return user

class RegisterAPI(Resource):
    @marshal_with(user_fields)
    def post(self):
        args = register_parser.parse_args()
        if not all([args['user_name'], args['password'], args['fullname'], args['address'], args['pincode']]):
            raise MissingFieldsError("All fields are required.")
        if not args['pincode'].isdigit() or len(args['pincode']) != 6:
            raise ValidationError("Pincode must be a 6-digit number.")
        existing_user = User.query.filter_by(user_name=args['user_name']).first()
        if existing_user:
            raise AlreadyExistError("Username already exists.")
        new_user = User(user_name=args['user_name'], password=args['password'], full_name=args['fullname'], address=args['address'], pincode=args['pincode'], role='user')
        db.session.add(new_user)
        db.session.commit()
        return new_user, 201
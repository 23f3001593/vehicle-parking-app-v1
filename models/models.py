from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    full_name = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False)
    __table_args__ = (
        db.CheckConstraint("length(pincode)=6", name="pincode_length_check"),
        db.CheckConstraint("role IN ('user','admin')", name="role_check"),
    )
    reservations = db.relationship("Reservation", backref="user", cascade="all, delete-orphan")

class ParkingLot(db.Model):
    __tablename__ = "ParkingLot"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prime_location_name = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    filled_spots = db.Column(db.Integer, nullable=False, default=0)
    revenue_collected = db.Column(db.Numeric, nullable=False, default=0.0)
    __table_args__ = (
        db.CheckConstraint("length(pincode)=6", name="pincode_length_check"),
    )
    spots = db.relationship("ParkingSpot", backref="lot", cascade="all, delete-orphan")

class ParkingSpot(db.Model):
    __tablename__ = "ParkingSpot"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("ParkingLot.id"), nullable=False)
    status = db.Column(db.Text, nullable=False, default='A')
    __table_args__ = (
        db.CheckConstraint("status IN ('A','O')", name="status_check"),
    )
    reservations = db.relationship("Reservation", backref="spot", cascade="all, delete-orphan")

class Reservation(db.Model):
    __tablename__ = "Reservation"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    
    spot_id = db.Column(db.Integer, db.ForeignKey("ParkingSpot.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    vehicle_num = db.Column(db.Text, nullable=False)
    parking_time = db.Column(db.DateTime, nullable=False, default=lambda:datetime.now(timezone.utc))
    leaving_time = db.Column(db.DateTime, default=None)
    parking_cost = db.Column(db.Numeric, default=None)
    __table_args__ = (
        db.CheckConstraint("length(vehicle_num)=10", name="vehicle_num_length_check"),
    )

admin_data = ("ramkumar", "RamKumar9", "Ram Kumar", "12 MG Road, Bengaluru", "560001", "admin")
if not User.query.filter_by(user_name=admin_data[0]).first():
    new_admin = User(
        user_name=admin_data[0],
        password=admin_data[1],
        full_name=admin_data[2],
        address=admin_data[3],
        pincode=admin_data[4],
        role=admin_data[5]
    )
    db.session.add(new_admin)
    db.session.commit()
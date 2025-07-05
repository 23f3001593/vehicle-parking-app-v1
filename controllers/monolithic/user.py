from app import app
from models.models import db, User, ParkingLot, ParkingSpot, Reservation
from flask import render_template, request, redirect
from datetime import datetime, timezone, timedelta
from decimal import Decimal

@app.route("/user/dashboard/<int:user_id>", methods=["GET"])
def user_dashboard(user_id):
    user = User.query.get(user_id)
    ongoing_reservations = Reservation.query.filter_by(user_id=user_id, leaving_time=None).all()
    IST = timezone(timedelta(hours=5, minutes=30))
    for reservation in ongoing_reservations:
        reservation.parking_time = reservation.parking_time.replace(tzinfo=timezone.utc).astimezone(IST)
    lots = ParkingLot.query.filter(ParkingLot.filled_spots < ParkingLot.max_spots).all()
    lot_availability = {lot.id: lot.max_spots-lot.filled_spots for lot in lots}
    return render_template("/user/user_dashboard.html", user=user, ongoing_reservations=ongoing_reservations, lots=lots, lot_availability=lot_availability)

@app.route("/user/parking-spot/book/<int:user_id>/<int:lot_id>", methods=["GET","POST"])
def book_parking_spot(user_id, lot_id):
    user = User.query.get(user_id)
    lot = ParkingLot.query.get(lot_id)
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
    if request.method == "POST":
        vehicle_num = request.form['vehicle_num']
        new_reservation = Reservation(spot_id=spot.id, user_id=user.id, vehicle_num=vehicle_num)
        spot.status = 'O'
        lot.filled_spots += 1
        db.session.add(new_reservation)
        db.session.commit()
        return redirect(f"/user/dashboard/{user.id}")
    return render_template("/user/parking_spot_book.html", user=user, lot=lot, spot=spot)

@app.route("/user/parking-spot/release/<int:reservation_id>", methods=["GET","POST"])
def release_parking_spot(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    user = reservation.user
    spot = reservation.spot
    lot = spot.lot
    if request.method == "POST":
        reservation.leaving_time = datetime.now(timezone.utc)
        db.session.commit()
        duration_hours = Decimal((reservation.leaving_time - reservation.parking_time).total_seconds()) / Decimal(3600)
        cost = Decimal(duration_hours) * lot.price
        reservation.parking_cost = cost
        spot.status = 'A'
        lot.filled_spots -= 1
        lot.revenue_collected += cost
        db.session.commit()
        return redirect(f"/user/dashboard/{user.id}")
    IST = timezone(timedelta(hours=5, minutes=30))
    parking_time_ist = reservation.parking_time.replace(tzinfo=timezone.utc).astimezone(IST)
    leaving_time_ist = datetime.now(timezone.utc).replace(tzinfo=timezone.utc).astimezone(IST)
    return render_template("/user/parking_spot_release.html", reservation=reservation, user=user, parking_time=parking_time_ist, leaving_time=leaving_time_ist)

@app.route("/user/parking-history/<int:user_id>", methods=["GET"])
def parking_history(user_id):
    user = User.query.get(user_id)
    reservations = Reservation.query.filter(Reservation.user_id == user_id, Reservation.leaving_time != None).all()
    durations = {}
    IST = timezone(timedelta(hours=5, minutes=30))
    def format_duration(minutes):
        if minutes < 1:
            return "Less than a minute"
        hours = minutes // 60
        mins = minutes % 60
        if hours > 0:
            if mins > 0:
                return f"{hours}h {mins}m"
            else:
                return f"{hours}h"
        else:
            return f"{mins}m"
    for reservation in reservations:
        parking_time_ist = reservation.parking_time.replace(tzinfo=timezone.utc).astimezone(IST)
        leaving_time_ist = reservation.leaving_time.replace(tzinfo=timezone.utc).astimezone(IST)
        reservation.parking_time = parking_time_ist
        duration_minutes = Decimal((leaving_time_ist - parking_time_ist).total_seconds()) / Decimal(60)
        durations[reservation.id] = format_duration(int(duration_minutes))
    return render_template("/user/parking_history.html", user=user, reservations=reservations, durations=durations)

@app.route("/user/edit/<int:user_id>", methods=["GET","POST"])
def user_profile_edit(user_id):
    user = User.query.get(user_id)
    if request.method=="POST":
        user_name = request.form['user_name']
        password = request.form['password']
        full_name = request.form['full_name']
        address = request.form['address']
        pincode = request.form['pincode']
        user.user_name = user_name
        user.password = password
        user.full_name = full_name
        user.address = address
        user.pincode = pincode
        db.session.commit()
        return redirect(f"/user/dashboard/{user_id}")
    return render_template("/user/user_profile_edit.html", user=user)

@app.route("/user/delete/<int:user_id>", methods=["GET"])
def user_account_delete(user_id):
    user = User.query.get(user_id)
    ongoing_reservations = Reservation.query.filter_by(user_id=user_id, leaving_time=None).all()
    if ongoing_reservations:
        return redirect(f"/user/dashboard/{user_id}")
    db.session.delete(user)
    db.session.commit()
    return redirect("/")
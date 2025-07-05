from app import app
from models.models import db, User, ParkingLot, ParkingSpot, Reservation
from flask import render_template, request, redirect
from datetime import timezone, timedelta
from decimal import Decimal

@app.route("/admin/dashboard", methods=["GET"])
def admin_dashboard():
    lots = ParkingLot.query.all()
    return render_template("/admin/admin_dashboard.html", lots=lots)

@app.route("/admin/parking-lot/new", methods=["GET","POST"])
def new_parking_lot():
    if request.method=="POST":
        prime_location_name = request.form['prime_location_name']
        address = request.form['address']
        pincode = request.form['pincode']
        price = Decimal(request.form['price'])
        max_spots = int(request.form['max_spots'])
        new_lot = ParkingLot(prime_location_name=prime_location_name, address=address, pincode=pincode, price=price, max_spots=max_spots)
        db.session.add(new_lot)
        db.session.commit()
        for _ in range(max_spots):
            new_spot = ParkingSpot(lot_id=new_lot.id)
            db.session.add(new_spot)
            db.session.commit()
        return redirect("/admin/dashboard")
    return render_template("/admin/parking_lot_new.html")

@app.route("/admin/parking-lot/edit/<int:lot_id>", methods=["GET","POST"])
def edit_parking_lot(lot_id):
    lot = ParkingLot.query.get(lot_id)
    if request.method=="POST":
        prime_location_name = request.form['prime_location_name']
        address = request.form['address']
        pincode = request.form['pincode']
        price = Decimal(request.form['price'])
        max_spots = int(request.form['max_spots'])
        lot.prime_location_name = prime_location_name
        lot.address = address
        lot.pincode = pincode
        lot.price = price
        lot.max_spots = max_spots
        db.session.commit()
        return redirect("/admin/dashboard")
    return render_template("/admin/parking_lot_edit.html", lot=lot)

@app.route("/admin/parking-lot/delete/<int:lot_id>", methods=["GET"])
def delete_parking_lot(lot_id):
    lot = ParkingLot.query.get(lot_id)
    occupied_spot = any(spot.status == 'O' for spot in lot.spots)
    if occupied_spot:
        return redirect("/admin/dashboard")
    db.session.delete(lot)
    db.session.commit()
    return redirect("/admin/dashboard")

@app.route("/admin/parking-spot/occupied/<int:lot_id>", methods=["GET"])
def occupied_parking_spots(lot_id):
    lot = ParkingLot.query.get(lot_id)
    spots = [spot for spot in lot.spots if spot.status == 'O']
    reservations = {}
    IST = timezone(timedelta(hours=5, minutes=30))
    for spot in spots:
        active_reservation = Reservation.query.filter_by(spot_id=spot.id, leaving_time=None).first()
        parking_time_ist = active_reservation.parking_time.replace(tzinfo=timezone.utc).astimezone(IST)
        active_reservation.parking_time = parking_time_ist
        reservations[spot.id] = active_reservation
    return render_template("/admin/parking_spot_occupied.html", lot=lot, spots=spots, reservations=reservations)

@app.route("/admin/registered-users", methods=["GET"])
def registered_users():
    users = User.query.filter_by(role='user').all()
    return render_template("/admin/registered_users.html", users=users)

@app.route("/admin/parking-reservations", methods=["GET"])
def parking_reservations():
    reservations = Reservation.query.filter(Reservation.leaving_time != None).all()
    usernames = {}
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
        usernames[reservation.id] = reservation.user.user_name
    return render_template("/admin/parking_reservations.html", reservations=reservations, durations=durations, usernames=usernames)

@app.route("/admin/edit", methods=["GET","POST"])
def admin_profile_edit():
    admin = User.query.filter_by(role="admin").first()
    if request.method=="POST":
        user_name = request.form['user_name']
        password = request.form['password']
        full_name = request.form['full_name']
        address = request.form['address']
        pincode = request.form['pincode']
        admin.user_name = user_name
        admin.password = password
        admin.full_name = full_name
        admin.address = address
        admin.pincode = pincode
        db.session.commit()
        return redirect(f"/admin/dashboard")
    return render_template("/admin/admin_profile_edit.html", admin=admin)
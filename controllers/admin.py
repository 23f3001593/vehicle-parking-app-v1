from app import app
from models.models import db, User, ParkingLot, ParkingSpot, Reservation
from flask import render_template, request, redirect
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

@app.route("/admin/parking-spot/view/<int:lot_id>", methods=["GET"])
def view_parking_spots(lot_id):
    lot = ParkingLot.query.get(lot_id)
    spots = [spot for spot in lot.spots if spot.status == 'O']
    return render_template("/admin/parking_spot_view.html", spots=spots)

@app.route("/admin/parking-spot/details/<int:spot_id>", methods=["GET"])
def parking_spot_details(spot_id):
    reservation = Reservation.query.filter_by(spot_id=spot_id, leaving_time=None).first()
    return render_template("/admin/parking_spot_details.html", reservation=reservation)

@app.route("/admin/registered-users", methods=["GET"])
def registered_users():
    users = User.query.filter_by(role='user').all()
    return render_template("/admin/registered_users.html", users=users)

@app.route("/admin/parking-reservations", methods=["GET"])
def parking_reservations():
    reservations = Reservation.query.filter(Reservation.leaving_time != None).all()
    
    durations = {}
    usernames = {}
    for reservation in reservations:
        duration = Decimal((reservation.leaving_time - reservation.parking_time).total_seconds()) / Decimal(60)
        durations[reservation.id] = int(duration)
        usernames[reservation.id] = reservation.user.user_name

    return render_template("/admin/parking_reservations.html", reservations=reservations, durations=durations, usernames=usernames)
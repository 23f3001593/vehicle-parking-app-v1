from app import app
from models.models import db, User, ParkingLot, ParkingSpot, Reservation
from flask import render_template, request, redirect
from datetime import datetime, timezone
from decimal import Decimal

@app.route("/user/dashboard/<int:user_id>", methods=["GET"])
def user_dashboard(user_id):
    user = User.query.get(user_id)
    ongoing_reservations = Reservation.query.filter_by(user_id=user_id, leaving_time=None).all()
    lots = ParkingLot.query.filter(ParkingLot.filled_spots < ParkingLot.max_spots).all()
    lot_availability = {lot.id: lot.max_spots-lot.filled_spots for lot in lots}
    return render_template("/user/user_dashboard.html", user=user, reservations=ongoing_reservations, lots=lots, lot_availability=lot_availability)

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
    leaving_time = datetime.now(timezone.utc)

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
    return render_template("/user/parking_spot_release.html", reservation=reservation, user=user, leaving_time=leaving_time.strftime('%Y-%m-%d %H:%M:%S'))

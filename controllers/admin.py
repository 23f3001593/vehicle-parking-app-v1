from app import app
from flask import render_template, request, redirect
from flask_login import current_user, logout_user, login_required
from functools import wraps
import requests

API_BASE = "http://127.0.0.1:5000/api"

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            logout_user()
            return render_template("main/index.html", message="Access forbidden. You have been logged out.")
        return f(*args, **kwargs)
    return wrapper

@app.route("/admin/dashboard", methods=["GET"])
@login_required
@admin_required
def admin_dashboard():
    try:
        res = requests.get(f"{API_BASE}/admin/dashboard")
        data = res.json()
    except (requests.exceptions.RequestException, ValueError):
        return "Something went wrong. Try again later.", 500
    return render_template("admin/admin_dashboard.html", data=data)

@app.route("/admin/parking-lot/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_parking_lot():
    if request.method == "POST":
        input_data = {"prime_location_name": request.form["prime_location_name"], "address": request.form["address"], "pincode": request.form["pincode"], "price": request.form["price"], "max_spots": request.form["max_spots"]}
        try:
            res = requests.post(f"{API_BASE}/parking-lot/new", json=input_data)
            if res.status_code != 201:
                return render_template("admin/parking_lot_new.html", message=res.json()["message"])
        except (requests.exceptions.RequestException, ValueError):
            return "Something went wrong. Try again later.", 500
        return redirect("/admin/dashboard")
    return render_template("admin/parking_lot_new.html")

@app.route("/admin/parking-lot/edit/<int:lot_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_parking_lot(lot_id):
    if request.method == "POST":
        input_data = {"prime_location_name": request.form["prime_location_name"], "address": request.form["address"], "pincode": request.form["pincode"], "price": request.form["price"], "max_spots": request.form["max_spots"]}
        try:
            res = requests.put(f"{API_BASE}/parking-lot/{lot_id}", json=input_data)
            if res.status_code != 200:
                input_data["id"] = lot_id
                return render_template("admin/parking_lot_edit.html", data=input_data, message=res.json()["message"])
        except (requests.exceptions.RequestException, ValueError):
            return "Something went wrong. Try again later.", 500
        return redirect("/admin/dashboard")
    try:
        res = requests.get(f"{API_BASE}/parking-lot/{lot_id}")
        data = res.json()
        if res.status_code != 200:
            data = requests.get(f"{API_BASE}/admin/dashboard").json()
            return render_template("admin/admin_dashboard.html", data=data, message=res.json()["message"])
    except (requests.exceptions.RequestException, ValueError):
        return "Something went wrong. Try again later.", 500
    return render_template("admin/parking_lot_edit.html", data=data)

@app.route("/admin/parking-lot/delete/<int:lot_id>", methods=["GET"])
@login_required
@admin_required
def delete_parking_lot(lot_id):
    try:
        res = requests.delete(f"{API_BASE}/parking-lot/{lot_id}")
        if res.status_code != 200:
            data = requests.get(f"{API_BASE}/admin/dashboard").json()
            return render_template("admin/admin_dashboard.html", data=data, message=res.json()["message"])
    except (requests.exceptions.RequestException, ValueError):
        return "Something went wrong. Try again later.", 500
    return redirect("/admin/dashboard")

@app.route("/admin/parking-spot/occupied/<int:lot_id>", methods=["GET"])
@login_required
@admin_required
def occupied_parking_spots(lot_id):
    try:
        res = requests.get(f"{API_BASE}/parking-spot/occupied/{lot_id}")
        data = res.json()
        if res.status_code != 200:
            data = requests.get(f"{API_BASE}/admin/dashboard").json()
            return render_template("admin/admin_dashboard.html", data=data, message=res.json()["message"])
    except (requests.exceptions.RequestException, ValueError):
        return "Something went wrong. Try again later.", 500
    return render_template("admin/parking_spot_occupied.html", data=data)

@app.route("/admin/registered-users", methods=["GET"])
@login_required
@admin_required
def registered_users():
    search_query = request.args.get("search", "").strip()
    try:
        params = {"search": search_query} if search_query else {}
        res = requests.get(f"{API_BASE}/admin/registered-users", params=params)
        data = res.json()
    except (requests.exceptions.RequestException, ValueError):
        return "Something went wrong. Try again later.", 500
    return render_template("admin/registered_users.html", data=data)

@app.route("/admin/parking-reservations", methods=["GET"])
@login_required
@admin_required
def parking_reservations():
    search_query = request.args.get("search", "").strip()
    try:
        params = {"search": search_query} if search_query else {}
        res = requests.get(f"{API_BASE}/admin/reservations", params=params)
        data = res.json()
    except (requests.exceptions.RequestException, ValueError):
        return "Something went wrong. Try again later.", 500
    return render_template("admin/parking_reservations.html", data=data)

@app.route("/admin/edit", methods=["GET", "POST"])
@login_required
@admin_required
def admin_profile_edit():
    if request.method == "POST":
        input_data = {"user_name": request.form["user_name"], "password": request.form["password"], "full_name": request.form["full_name"], "address": request.form["address"], "pincode": request.form["pincode"]}
        try:
            res = requests.put(f"{API_BASE}/user/profile/1", json=input_data)
            if res.status_code != 200:
                input_data["user_id"] = 1
                return render_template("admin/admin_profile_edit.html", data=input_data, message=res.json()["message"])
        except (requests.exceptions.RequestException, ValueError):
            return "Something went wrong. Try again later.", 500
        return redirect("/admin/dashboard")
    try:
        res = requests.get(f"{API_BASE}/user/profile/1")
        data = res.json()
        if res.status_code != 200:
            data = requests.get(f"{API_BASE}/admin/dashboard").json()
            return render_template("admin/admin_dashboard.html", data=data, message=res.json()["message"])
    except (requests.exceptions.RequestException, ValueError):
        return "Something went wrong. Try again later.", 500
    return render_template("admin/admin_profile_edit.html", data=data)
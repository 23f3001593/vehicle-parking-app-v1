from app import app
from flask import render_template, request, redirect
from flask_login import current_user, logout_user, login_required
from functools import wraps
import requests

API_BASE = "http://127.0.0.1:5000/api"

def user_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "user":
            logout_user()
            return render_template("main/index.html", message="Access forbidden. You have been logged out.")
        user_id = kwargs.get('user_id')
        if user_id is not None and current_user.id != user_id:
            logout_user()
            return render_template("main/index.html", message="Access forbidden. You have been logged out.")
        return f(*args, **kwargs)
    return wrapper

@app.route("/user/dashboard/<int:user_id>", methods=["GET"])
@login_required
@user_required
def user_dashboard(user_id):
    try:
        res = requests.get(f"{API_BASE}/user/dashboard/{user_id}")
        data = res.json()
        if res.status_code != 200:
            return render_template("main/index.html", message=data["message"])
    except (requests.exceptions.RequestException, ValueError):
        return "Something went wrong. Try again later.", 500
    return render_template("user/user_dashboard.html", data=data, lot_availability={lot["id"]: lot["available_spots"] for lot in data["lots"]})

@app.route("/user/parking-spot/book/<int:user_id>/<int:lot_id>", methods=["GET", "POST"])
@login_required
@user_required
def book_parking_spot(user_id, lot_id):
    if request.method == "POST":
        input_data = {"vehicle_num": request.form['vehicle_num']}
        try:
            res = requests.post(f"{API_BASE}/reservation/book/{user_id}/{lot_id}", json=input_data)
            if res.status_code != 201:
                data = requests.get(f"{API_BASE}/reservation/book/{user_id}/{lot_id}").json()
                return render_template("user/parking_spot_book.html", data=data, message=res.json()["message"])
        except (requests.exceptions.RequestException, ValueError):
            return "Something went wrong. Try again later.", 500
        return redirect(f"/user/dashboard/{user_id}")
    try:
        res = requests.get(f"{API_BASE}/reservation/book/{user_id}/{lot_id}")
        data = res.json()
        if res.status_code != 200:
            return render_template("main/index.html", message=data["message"])
    except (requests.exceptions.RequestException, ValueError):
        return "Something went wrong. Try again later.", 500
    return render_template("user/parking_spot_book.html", data=data)

@app.route("/user/parking-spot/release/<int:reservation_id>", methods=["GET", "POST"])
@login_required
@user_required
def release_parking_spot(reservation_id):
    try:
        res = requests.get(f"{API_BASE}/reservation/release/{reservation_id}")
        data = res.json()
        if res.status_code != 200:
            return render_template("main/index.html", message=data["message"])
        if data["user_id"] != current_user.id:
                logout_user()
                return render_template("main/index.html", message="Access forbidden. You have been logged out.")
        if request.method == "POST":
            res = requests.put(f"{API_BASE}/reservation/release/{reservation_id}")
            if res.status_code != 200:
                return render_template("main/index.html", message=res.json()["message"])
            return redirect(f"/user/dashboard/{res.json()["user_id"]}")
    except (requests.exceptions.RequestException, ValueError):
        return "Something went wrong. Try again later.", 500
    return render_template("user/parking_spot_release.html", data=data)

@app.route("/user/parking-history/<int:user_id>", methods=["GET"])
@login_required
@user_required
def parking_history(user_id):
    search_query = request.args.get("search", "").strip()
    try:
        params = {"search": search_query} if search_query else {}
        res = requests.get(f"{API_BASE}/user/history/{user_id}", params=params)
        data = res.json()
        if res.status_code != 200:
            return render_template("main/index.html", message=data["message"])
        durations = {reservation["id"]: reservation["duration"] for reservation in data}
    except (requests.exceptions.RequestException, ValueError):
        return "Something went wrong. Try again later.", 500
    return render_template("user/parking_history.html", data={"user_id": user_id, "reservations": data}, durations=durations)

@app.route("/user/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
@user_required
def user_profile_edit(user_id):
    if request.method == "POST":
        input_data = {"user_name": request.form["user_name"], "password": request.form["password"], "full_name": request.form["full_name"], "address": request.form["address"], "pincode": request.form["pincode"]}
        try:
            res = requests.put(f"{API_BASE}/user/profile/{user_id}", json=input_data)
            if res.status_code != 200:
                input_data["user_id"] = user_id
                return render_template("user/user_profile_edit.html", data=input_data, message=res.json()["message"])
        except (requests.exceptions.RequestException, ValueError):
            return "Something went wrong. Try again later.", 500
        return redirect(f"/user/dashboard/{user_id}")
    try:
        res = requests.get(f"{API_BASE}/user/profile/{user_id}")
        data = res.json()
        if res.status_code != 200:
            return render_template("main/index.html", message=data["message"])
    except (requests.exceptions.RequestException, ValueError):
        return "Something went wrong. Try again later.", 500
    return render_template("user/user_profile_edit.html", data=data)

@app.route("/user/delete/<int:user_id>", methods=["GET"])
@login_required
@user_required
def user_account_delete(user_id):
    try:
        res = requests.delete(f"{API_BASE}/user/profile/{user_id}")
        if res.status_code != 200:
            if user_id == 1:
                return render_template("main/index.html", message=res.json()["message"])
            data = requests.get(f"{API_BASE}/user/dashboard/{user_id}").json()
            return render_template("user/user_dashboard.html", data=data, lot_availability={lot["id"]: lot["available_spots"] for lot in data["lots"]}, message=res.json()["message"])
    except (requests.exceptions.RequestException, ValueError, KeyError):
        return "Something went wrong. Try again later.", 500
    return redirect("/")
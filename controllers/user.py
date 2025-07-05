from app import app
from flask import render_template, request, redirect
import requests

API_BASE = "http://127.0.0.1:5000/api"

@app.route("/user/dashboard/<int:user_id>", methods=["GET"])
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
def release_parking_spot(reservation_id):
    if request.method == "POST":
        try:
            res = requests.put(f"{API_BASE}/reservation/release/{reservation_id}")
            if res.status_code != 200:
                return render_template("main/index.html", message=res.json()["message"])
        except (requests.exceptions.RequestException, ValueError):
            return "Something went wrong. Try again later.", 500
        return redirect(f"/user/dashboard/{res.json()["user_id"]}")
    try:
        res = requests.get(f"{API_BASE}/reservation/release/{reservation_id}")
        data = res.json()
        if res.status_code != 200:
            return render_template("main/index.html", message=data["message"])
    except (requests.exceptions.RequestException, ValueError):
        return "Something went wrong. Try again later.", 500
    return render_template("user/parking_spot_release.html", data=data)

@app.route("/user/parking-history/<int:user_id>", methods=["GET"])
def parking_history(user_id):
    try:
        res = requests.get(f"{API_BASE}/user/history/{user_id}")
        data = res.json()
        if res.status_code != 200:
            return render_template("main/index.html", message=data["message"])
        durations = {reservation["id"]: reservation["duration"] for reservation in data}
    except (requests.exceptions.RequestException, ValueError):
        return "Something went wrong. Try again later.", 500
    return render_template("user/parking_history.html", data={"user_id": user_id, "reservations": data}, durations=durations)

@app.route("/user/edit/<int:user_id>", methods=["GET", "POST"])
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
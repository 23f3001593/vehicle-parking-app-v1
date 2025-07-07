from app import app
from flask import render_template, request, redirect
from flask_login import login_user, logout_user, login_required
from models.models import User
import requests

API_BASE = "http://127.0.0.1:5000/api"

@app.route("/", methods=["GET"])
def home():
    return render_template("main/index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        input_data = {"user_name": request.form['username'], "password": request.form['password']}
        try:
            res = requests.post(f"{API_BASE}/login", json=input_data)
            data = res.json()
            if res.status_code != 200:
                return render_template("/main/login.html", message=data["message"])
        except (requests.exceptions.RequestException, ValueError):
            return "Something went wrong. Try again later.", 500
        user = User.query.get(data["id"])
        if not user:
            return render_template("/main/login.html", message="User not found.")
        login_user(user)
        if (data["role"] == "admin"):
            return redirect("/admin/dashboard")
        else:
            return redirect(f"/user/dashboard/{data["id"]}")
    return render_template("/main/login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        input_data = {"user_name": request.form['username'], "password": request.form["password"], "fullname": request.form["fullname"], "address": request.form["address"], "pincode":request.form["pincode"]}
        try:
            res = requests.post(f"{API_BASE}/register", json=input_data)
            data = res.json()
            if res.status_code != 201:
                return render_template("/main/register.html", message=data["message"])
        except (requests.exceptions.RequestException, ValueError):
            return "Something went wrong. Try again later.", 500
        user = User.query.get(data["id"])
        if not user:
            return render_template("/main/login.html", message="User not found.")
        login_user(user)
        return redirect(f"/user/dashboard/{data["id"]}")
    return render_template("/main/register.html")

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect("/")
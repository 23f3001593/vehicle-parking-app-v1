from app import app
from models.models import db, User
from flask import render_template, request, redirect

@app.route("/", methods=["GET"])
def home():
    return render_template("main/index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(user_name=username).first()
        if (not user) or (user.password!=password):
            return render_template("/main/login.html")
        
        return redirect('/')
    return render_template("/main/login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        address = request.form["address"]
        pincode = request.form["pincode"]

        existing_user = User.query.filter_by(user_name=username).first()
        if existing_user:
            return render_template("/main/register.html")
        
        new_user = User(user_name=username, password=password, full_name=fullname, address=address, pincode=pincode, role="user")
        db.session.add(new_user)
        db.session.commit()

        return redirect('/')
    return render_template("/main/register.html")
import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
import config, users

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        email = request.form["email"]
        bio = request.form["bio"]

        if password1 != password2:
            return "ERROR: salasanat eivät ole samat"

        try:
            users.create_user(username, email, bio, password1)
            return "Account created"
        except sqlite3.IntegrityError:
            return "ERROR: Username already exists"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "ERROR: Wrong username or password"

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")
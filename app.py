import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
import config, users, projects

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/project/<int:project_id>")
def show_project(project_id):
    project = projects.get_project(project_id)
    #tasks = projects.get_tasks(thread_id)
    return render_template("project.html", project=project)

@app.route("/new_project", methods=["GET", "POST"])
def new_project():

    if request.method == "GET":
        return render_template("new_project.html")

    if request.method == "POST":
       title = request.form["name"]
       parameter_one = request.form["power"]
       parameter_two = request.form["left_terms"]
       max_tasks = request.form["max_range"]
       description = request.form["description"]
       user_id = session["user_id"]

    project_id = projects.add_project(title, parameter_one, parameter_two, max_tasks, description, user_id)
    return redirect("/project/" + str(project_id))

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
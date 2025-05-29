import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
import config, users, projects

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    project_list = projects.get_projects()
    return render_template("index.html", projects=project_list)

@app.route("/project/<int:project_id>")
def show_project(project_id):
    project = projects.get_project(project_id)
    #tasks = projects.get_tasks(thread_id)

    project_parameters= projects.get_project_parameters(project_id)

    print(project_parameters[0][0],project_parameters[0][1])

    return render_template("project.html", project=project, project_parameters = project_parameters)

@app.route("/remove/<int:project_id>", methods=["GET", "POST"])
def remove_project(project_id):
    project = projects.get_project(project_id)

    if request.method == "GET":
        return render_template("remove.html", project=project)

    if request.method == "POST":
        if "continue" in request.form:
            projects.update_project_status(project["id"], 4)
        return redirect("/project/" + str(project["id"]))

@app.route("/hold/<int:project_id>", methods=["GET", "POST"])
def set_project_on_hold(project_id):
    project = projects.get_project(project_id)

    if request.method == "GET":
        return render_template("hold.html", project=project)

    if request.method == "POST":
        if "continue" in request.form:
            projects.update_project_status(project["id"], 3)
        return redirect("/project/" + str(project["id"]))

@app.route("/reactivate/<int:project_id>", methods=["GET", "POST"])
def reactivate_project(project_id):
    project = projects.get_project(project_id)

    if request.method == "GET":
        return render_template("reactivate.html", project=project)

    if request.method == "POST":
        if "continue" in request.form:
            projects.update_project_status(project["id"], 1)
        return redirect("/project/" + str(project["id"]))


@app.route("/new_project", methods=["GET", "POST"])
def new_project():

    if request.method == "GET":
        return render_template("new_project.html")

    if request.method == "POST":
        name = request.form["name"]
        range_min = request.form["range_min"]
        range_max = request.form["range_max"]
        description = request.form["description"]
        user_id = session["user_id"]

        parameter_names = request.form.getlist('parameter_names[]')
        parameter_values = request.form.getlist('parameter_values[]')

    project_id = projects.add_project(name, range_min, range_max, description, user_id)

    for name, value in zip(parameter_names, parameter_values):
        if name and value:
            projects.add_parameter(name, value, project_id)


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
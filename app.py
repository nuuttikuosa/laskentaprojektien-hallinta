import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, abort
import config
import users
import projects
import constants

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    project_list = projects.get_projects()
    return render_template("index.html", projects=project_list)

@app.route("/project/<int:project_id>")
def show_project(project_id):
    project = projects.get_project(project_id)
    tasks = projects.get_tasks(project_id)

    project_parameters= projects.get_project_parameters(project_id)

    return render_template("project.html", project=project, project_parameters = project_parameters, tasks=tasks)

@app.route("/remove/<int:project_id>", methods=["GET", "POST"])
def remove_project(project_id):
    project = projects.get_project(project_id)

    if request.method == "GET":
        return render_template("remove.html", project=project)

    if request.method == "POST":
        if "continue" in request.form:
            projects.update_project_status(project["id"], constants.PROJECT_STATUS_DELETED)
        return redirect("/project/" + str(project["id"]))

@app.route("/hold/<int:project_id>", methods=["GET", "POST"])
def set_project_on_hold(project_id):
    project = projects.get_project(project_id)

    if request.method == "GET":
        return render_template("hold.html", project=project)

    if request.method == "POST":
        if "continue" in request.form:
            projects.update_project_status(project["id"], constants.PROJECT_STATUS_ON_HOLD)
        return redirect("/project/" + str(project["id"]))

@app.route("/reactivate/<int:project_id>", methods=["GET", "POST"])
def reactivate_project(project_id):
    project = projects.get_project(project_id)

    if request.method == "GET":
        return render_template("reactivate.html", project=project)

    if request.method == "POST":
        if "continue" in request.form:
            projects.update_project_status(project["id"], constants.PROJECT_STATUS_ONGOING)
        return redirect("/project/" + str(project["id"]))

@app.route("/projects/search", methods=['GET'])
def search_projects():
    keyword = request.args.get("keyword")
    results = projects.search(keyword) if keyword else []
    return render_template("search.html", keyword=keyword, results=results)


@app.route("/edit/<int:project_id>", methods=["GET", "POST"])
def edit(project_id):

    project = projects.get_project(project_id)
    if session["user_id"] != project["user_id"]:
        abort(403)

    if request.method == "GET":

        project_parameters = projects.get_project_parameters(project_id)

        return render_template("edit.html", project=project, project_parameters=project_parameters)

    if request.method == "POST":
        name = request.form["name"]
        range_min = request.form["range_min"]
        range_max = request.form["range_max"]
        description = request.form["description"]

        projects.update_project(name, range_min, range_max, description, project_id)

        return redirect("/project/" + str(project_id))

@app.route("/edit/<int:project_id>/generate_tasks", methods=["GET", "POST"])
def generate_tasks(project_id):

    project = projects.get_project(project_id)
    if session["user_id"] != project["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("generate_tasks.html", project=project)

    if request.method == "POST":
        min = int(request.form["min"])
        max = int(request.form["max"])
        if min < project["range_min"] or max > project["range_max"]:
            return render_template("generate_tasks.html", project=project, error="Task numbers must be within the project range.")
        if min > max:
            return render_template("generate_tasks.html", project=project, error="Smallest task number cannot be larger than largest task number.")
        if project["status"] != "Not Started":
            return render_template("generate_tasks.html", project=project, error="Project must not be started to generate tasks.")
        if min == max:
            return render_template("generate_tasks.html", project=project, error="Smallest task number cannot be equal to largest task number.")

        projects.generate_tasks(min, max, project_id)
        projects.update_project_status(project_id, constants.PROJECT_STATUS_ONGOING)

        return redirect("/project/" + str(project_id))

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
        if not user_id:
            return render_template("login.html", error="Wrong username or password")

        session["user_id"] = user_id
        session["username"] = username
        return redirect("/")



@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect("/")

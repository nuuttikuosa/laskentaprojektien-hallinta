import sqlite3
from flask import Flask
from flask import make_response, redirect, render_template, request, session, abort
import config
import users
import projects
import constants
import powersum

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

@app.route("/")
def index():
    project_list = projects.get_projects()
    return render_template("index.html", projects=project_list)

@app.route("/project/<int:project_id>")
def show_project(project_id):
    project = projects.get_project(project_id)
    if not project:
        abort(404)

    tasks = projects.get_tasks(project_id)
    classes = projects.get_classes(project_id)
    project_parameters= projects.get_project_parameters(project_id)

    return render_template("project.html", project=project, project_parameters = project_parameters,
                           tasks=tasks, classes=classes)

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

@app.route("/projects/search", methods=["GET"])
def search_projects():
    keyword = request.args.get("keyword")
    results = projects.search(keyword) if keyword else []
    return render_template("search.html", keyword=keyword, results=results)


@app.route("/edit/<int:project_id>", methods=["GET", "POST"])
def edit(project_id):
    require_login()

    project = projects.get_project(project_id)
    if not project:
        abort(404)
    if session["user_id"] != project["user_id"]:
        abort(403)

    if request.method == "GET":

        project_parameters = projects.get_project_parameters(project_id)

        all_classes = projects.get_all_classes()
        classes = {}
        for my_class in all_classes:
            classes[my_class] = ""
        for entry in projects.get_classes(project_id):
            classes[entry["title"]] = entry["value"]

        return render_template("edit.html", project=project, project_parameters=project_parameters,
                               classes=classes, all_classes=all_classes)

    if request.method == "POST":
        name = request.form["name"]
        if not name or len(name) > 50:
            abort(403)
        range_min = request.form["range_min"]
        if not range_min:
            abort(403)
        range_max = request.form["range_max"]
        if not range_max:
            abort(403)
        description = request.form["description"]
        if not description or len(description) > 1000:
            abort(403)

        all_classes = projects.get_all_classes()

        classes = []
        for entry in request.form.getlist("classes"):
            if entry:
                class_title, class_value = entry.split(":")
                if class_title not in all_classes:
                    abort(403)
                if class_value not in all_classes[class_title]:
                    abort(403)
                classes.append((class_title, class_value))

        projects.update_project(name, range_min, range_max, description, project_id, classes)

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
            return render_template("generate_tasks.html", project=project,
                                   error="Task numbers must be within the project range.")
        if max - min < 1:
            return render_template("generate_tasks.html", project=project,
                                   error="Smallest task number cannot be larger than largest task number.")
        if project["status"] != "Not Started":
            return render_template("generate_tasks.html", project=project,
                                   error="Project must not be started to generate tasks.")
        if min < 0 or max < 0:
            return render_template("generate_tasks.html", project=project,
                                   error="Task numbers must be non-negative.")

        projects.generate_tasks(min, max, project_id)
        projects.update_project_status(project_id, constants.PROJECT_STATUS_ONGOING)

        return redirect("/project/" + str(project_id))

@app.route("/project/<int:project_id>/reserve_tasks", methods=["GET","POST"])
def reserve_tasks(project_id):
    project = projects.get_project(project_id)


    if request.method == "GET":
        number_of_free_tasks = projects.get_number_of_tasks(project_id, constants.TASK_STATUS_FREE)
        return render_template("reserve_tasks.html", project = project,
                               number_of_free_tasks=number_of_free_tasks)

    if request.method == "POST":
        user_id = session["user_id"]
        requested_number_of_tasks=int(request.form["requested_number_of_tasks"])
        projects.reserve_tasks(project_id, user_id, requested_number_of_tasks)

        return redirect(f"/project/{project_id}")

@app.route("/return", methods=["GET", "POST"])
def return_tasks():
    project_list = projects.get_projects()

    if request.method == "GET":
        return render_template("return_tasks.html", projects=project_list)


    if request.method == "POST":

        log_file = request.files["log_file"]

        if not log_file or log_file.filename == "":
            return render_template("return_tasks.html", projects=project_list,
                                   error="No file selected.")

        content = log_file.read().decode("utf-8")
        rows = content.splitlines()
        results = []

        for row in rows:
            is_valid = powersum.validate_powersum(row)
            result = {
                "row": row,
                "status": "OK : " if is_valid else "Validation failed : "
            }
            results.append(result)

    return render_template("return_tasks.html", projects=project_list, results=results)


@app.route("/new_project", methods=["GET", "POST"])
def new_project():
    require_login()

    if request.method == "GET":

        classes = projects.get_all_classes()
        return render_template("new_project.html", classes=classes)

    if request.method == "POST":
        name = request.form["name"]
        if not name or len(name) > 50:
            abort(403)
        range_min = request.form["range_min"]
        if not range_min:
            abort(403)
        range_max = request.form["range_max"]
        if not range_max:
            abort(403)
        description = request.form["description"]
        if not description or len(description) > 1000:
            abort(403)
        user_id = session["user_id"]

        all_classes = projects.get_all_classes()
        classes = []
        for entry in request.form.getlist("classes"):
            if entry:
                class_title, class_value = entry.split(":")
                if class_title not in all_classes:
                    abort(403)
                if class_value not in all_classes[class_title]:
                    abort(403)
                classes.append((class_title, class_value))

        parameter_names = request.form.getlist("parameter_names[]")
        parameter_values = request.form.getlist("parameter_values[]")

        project_id = projects.add_project(name, range_min, range_max, description, user_id, classes)

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

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    tasks = users.get_tasks(user_id)
    return render_template("user.html", user=user, tasks=tasks)

@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    require_login()

    if request.method == "GET":
        return render_template("add_image.html")

    if request.method == "POST":
        file = request.files["image"]
        if not file.filename.endswith(".png"):
            return "VIRHE: väärä tiedostomuoto"

        image = file.read()
        if len(image) > 100 * 1024:
            return "VIRHE: liian suuri kuva"

        user_id = session["user_id"]
        users.update_image(user_id, image)
        return redirect("/user/" + str(user_id))

@app.route("/image/<int:user_id>")
def show_image(user_id):
    image = users.get_image(user_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/png")
    return response

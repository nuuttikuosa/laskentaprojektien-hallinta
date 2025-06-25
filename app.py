import sqlite3
import secrets
import markupsafe
import time
from flask import Flask
from flask import g, make_response, flash, redirect, render_template, request, session, abort
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

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.before_request
def before_request():
    if config.DEBUGGING:
        g.start_time = time.time()

@app.after_request
def after_request(response):
    if config.DEBUGGING and hasattr(g, 'start_time'):
        elapsed_time = round(time.time() - g.start_time, 2)
        print(f"[PERF] {request.method} {request.path} - {elapsed_time}s")
    return response

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
    require_login()
    project = projects.get_project(project_id)
    if not project:
        abort(404)
    if session["user_id"] != project["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove.html", project=project)

    if request.method == "POST":
        check_csrf()
        if "continue" in request.form:
            projects.update_project_status(project["id"], constants.PROJECT_STATUS_DELETED)
            flash("Project has been removed.", "info")
        return redirect("/project/" + str(project["id"]))

@app.route("/hold/<int:project_id>", methods=["GET", "POST"])
def set_project_on_hold(project_id):
    require_login()

    project = projects.get_project(project_id)
    if not project:
        abort(404)
    if session["user_id"] != project["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("hold.html", project=project)

    if request.method == "POST":
        check_csrf()
        if "continue" in request.form:
            projects.update_project_status(project["id"], constants.PROJECT_STATUS_ON_HOLD)
            flash("Project has been put on hold.", "info")
        return redirect("/project/" + str(project["id"]))

@app.route("/reactivate/<int:project_id>", methods=["GET", "POST"])
def reactivate_project(project_id):
    require_login()
    project = projects.get_project(project_id)
    if not project:
        abort(404)
    if session["user_id"] != project["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("reactivate.html", project=project)

    if request.method == "POST":
        check_csrf()
        if "continue" in request.form:
            projects.update_project_status(project["id"], constants.PROJECT_STATUS_ONGOING)
            flash("Project has been reactivated.", "info")
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
        check_csrf()
        name = request.form["name"]
        range_min = request.form["range_min"]
        range_max = request.form["range_max"]
        description = request.form["description"]

        if not name or len(name) > 50:
            flash("Project name is required and must be under 50 characters.", "error")
            return redirect("/edit/" + str(project_id))

        if not range_min.isdigit():
            flash("Range min must be a positive integer.", "error")
            return redirect("/edit/" + str(project_id))

        if not range_max.isdigit():
            flash("Range max must be a positive integer.", "error")
            return redirect("/edit/" + str(project_id))

        if int(range_min) <= 0 or int(range_max) <= 0:
            flash("Range min and max must be positive integers.", "error")
            return redirect("/edit/" + str(project_id))

        if int(range_min) >= int(range_max):
            flash("Range min must be less than range max.", "error")
            return redirect("/edit/" + str(project_id))

        if not description or len(description) > 1000:
            flash("Description is required and must be under 1000 characters.", "error")
            return redirect("/edit/" + str(project_id))

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
    require_login()

    project = projects.get_project(project_id)
    if not project:
        abort(404)
    if session["user_id"] != project["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("generate_tasks.html", project=project)

    if request.method == "POST":
        check_csrf()
        task_min = request.form["task_min"]
        task_max = request.form["task_max"]

        if not task_min.isdigit() or not task_max.isdigit():
            flash("ERROR: Both task numbers must be positive integers", "error")
            return render_template("generate_tasks.html", project=project)

        task_min = int(task_min)
        task_max = int(task_max)

        if task_min < project["range_min"] or task_max > project["range_max"]:
            flash("ERROR: Task numbers must be within the project range", "error")
            return render_template("generate_tasks.html", project=project)
        if task_max - task_min < 1:
            flash("ERROR: Smallest task number cannot be larger than largest task number", "error")
            return render_template("generate_tasks.html", project=project)
        if project["status"] != "Not Started":
            flash("ERROR: Project must not be started to generate tasks", "error")
            return redirect("/project/" + str(project_id))

        projects.generate_tasks(task_min, task_max, project_id)
        projects.update_project_status(project_id, constants.PROJECT_STATUS_ONGOING)

        return redirect("/project/" + str(project_id))

@app.route("/project/<int:project_id>/reserve_tasks", methods=["GET","POST"])
def reserve_tasks(project_id):
    require_login()
    project = projects.get_project(project_id)
    if not project:
        abort(404)

    if project["status"] != "Ongoing":
            flash("Cannot reserve tasks: project is not ongoing.", "error")
            return redirect(f"/project/{project_id}")

    number_of_free_tasks = projects.get_number_of_tasks(project_id, constants.TASK_STATUS_FREE)

    if request.method == "GET":

        return render_template("reserve_tasks.html", project = project,
                               number_of_free_tasks=number_of_free_tasks)
    if request.method == "POST":
        check_csrf()

        requested_number_of_tasks=request.form["requested_number_of_tasks"]
        if not requested_number_of_tasks or not requested_number_of_tasks.isdigit():
            flash("ERROR: Invalid number of tasks requested", "error")
            return redirect(f"/project/{project_id}/reserve_tasks")

        requested_number_of_tasks = int(requested_number_of_tasks)

        if requested_number_of_tasks < 1:
            flash("ERROR: Number of tasks requested must be at least 1", "error")
            return redirect(f"/project/{project_id}/reserve_tasks")

        if requested_number_of_tasks > number_of_free_tasks:
            flash(f"ERROR: Cannot reserve {requested_number_of_tasks} tasks, only {number_of_free_tasks} available", "error")
            return redirect(f"/project/{project_id}/reserve_tasks")


        user_id = session["user_id"]
        projects.reserve_tasks(project_id, user_id, requested_number_of_tasks)

        return redirect(f"/project/{project_id}")

@app.route("/return", methods=["GET", "POST"])
def return_tasks():
    require_login()
    project_list = projects.get_projects()

    if request.method == "GET":
        return render_template("return_tasks.html", projects=project_list,
                               max_log_file_size=config.MAX_LOG_FILE_SIZE)


    if request.method == "POST":
        check_csrf()
        project_id = request.form.get("project_id")
        if not project_id:
            flash("ERROR: No project selected", "error")
            return render_template("return_tasks.html", projects=project_list,
                       max_log_file_size=config.MAX_LOG_FILE_SIZE)

        log_file = request.files["log_file"]

        if not log_file or log_file.filename == "":
            flash("ERROR: No file selected", "error")
            return render_template("return_tasks.html", projects=project_list,
                       max_log_file_size=config.MAX_LOG_FILE_SIZE)

        raw = log_file.read()
        if len(raw) > config.MAX_LOG_FILE_SIZE:
            flash("ERROR: Log file size exceeds the limit", "error")
            return render_template("return_tasks.html", projects=project_list,
                           max_log_file_size=config.MAX_LOG_FILE_SIZE)
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            flash("ERROR: File must be UTF-8 encoded text", "error")
            return render_template("return_tasks.html", projects=project_list,
                           max_log_file_size=config.MAX_LOG_FILE_SIZE)

        project = projects.get_project(int(project_id))
        if not project:
            flash("ERROR: Invalid project selected", "error")
            return render_template("return_tasks.html", projects=project_list,
                           max_log_file_size=config.MAX_LOG_FILE_SIZE)



        user_id = session["user_id"]
        users.save_log_file(user_id, content)

        project_type = projects.get_project_class_value(project_id, "Type")
        if project_type != "Powersum":
            flash("ERROR: Only Powersum projects can be returned", "error")
            return render_template("return_tasks.html", projects=project_list,
                           max_log_file_size=config.MAX_LOG_FILE_SIZE)

        rows = [line for line in content.splitlines() if line.strip()]
        results = []

        for row in rows:
            is_valid = powersum.process_powersum_log_row(row, project_id)
            result = {
                "row": row,
                "status": "OK : " if is_valid else "Validation failed : "
            }
            results.append(result)

        success_count = sum(1 for r in results if "OK" in r["status"])
        fail_count = len(results) - success_count
        flash(f"Validation complete: {success_count} passed, {fail_count} failed.", "info")

        return render_template("return_tasks.html", projects=project_list,
                            max_log_file_size=config.MAX_LOG_FILE_SIZE,
                            results=results)


@app.route("/new_project", methods=["GET", "POST"])
def new_project():
    require_login()

    if request.method == "GET":

        classes = projects.get_all_classes()
        return render_template("new_project.html", classes=classes,
                               max_project_parameters=config.PROJECT_MAX_PARAMETRS)

    if request.method == "POST":
        check_csrf()

        name = request.form["name"]
        range_min = request.form["range_min"]
        range_max = request.form["range_max"]
        description = request.form["description"]

        if not name or len(name) > 50:
            flash("Project name is required and must be under 50 characters.", "error")
            return redirect("/new_project")

        if not range_min.isdigit():
            flash("Range min must be a non-negative integer.", "error")
            return redirect("/new_project")

        if not range_max.isdigit():
            flash("Range max must be a non-negative integer.", "error")
            return redirect("/new_project")

        if int(range_min) < 0 or int(range_max) < 0:
            flash("Range min and max must be non-negative integers.", "error")
            return redirect("/new_project")

        if int(range_min) >= int(range_max):
            flash("Range min must be less than range max.", "error")
            return redirect("/new_project")

        if not description or len(description) > 1000:
            flash("Description is required and must be under 1000 characters.", "error")
            return redirect("/new_project")

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

        try:
            project_id = projects.add_project(name, range_min, range_max, description, user_id, classes)
        except sqlite3.IntegrityError:
            flash("ERROR: Project name already exists", "error")
            return redirect("/new_project")

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
        if not username or len(username) > 20:
            flash("ERROR: Invalid username", "error")
            return redirect("/register")
        password1 = request.form["password1"]
        if not password1 or len(password1) > 50:
            flash("ERROR: Invalid password", "error")
            return redirect("/register")
        password2 = request.form["password2"]
        if not password2 or len(password2) > 50:
            flash("ERROR: Invalid password", "error")
            return redirect("/register")
        email = request.form["email"]
        if not email or len(email) > 50:
            flash("ERROR: Invalid email", "error")
            return redirect("/register")
        bio = request.form.get("bio", "")
        if len(bio) > 1000:
            flash("ERROR: Invalid bio", "error")
            return redirect("/register")

        if password1 != password2:
            flash("ERROR: The passwords are not the same", "error")
            return redirect("/register")

        try:
            user_id = users.create_user(username, email, bio, password1)
            flash("INFO: Account created successfully", "info")
            return redirect("/user/" + str(user_id))
        except sqlite3.IntegrityError:
            flash("ERROR: Username already exists", "error")
            return redirect("/register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if not user_id:
            flash("ERROR: Wrong username or password", "error")
            return render_template("login.html")

        session["csrf_token"] = secrets.token_hex(16)
        session["user_id"] = user_id
        session["username"] = username
        return redirect("/")

@app.route("/logout", methods=["GET"])
def logout():
    require_login()
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("csrf_token", None)
    flash("You have been logged out.", "info")
    return redirect("/")

@app.route("/solutions", methods=["GET"])
def show_solutions():
    solutions = projects.get_solutions()
    return render_template("solutions.html", solutions=solutions)

@app.route("/user/<int:user_id>", methods=["GET"])
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
        return render_template("add_image.html",
                               max_profile_picture_size=config.MAX_PROFILE_PICTURE_SIZE)

    if request.method == "POST":
        check_csrf()
        file = request.files["image"]

        if not file or file.filename == "":
            flash("Error: No file uploaded", "error")
            return render_template("add_image.html",
                                   max_profile_picture_size=config.MAX_PROFILE_PICTURE_SIZE)

        if not file.filename.lower().endswith(".png") or file.mimetype != "image/png":
            flash("Error: Only PNG files are allowed", "error")
            return render_template("add_image.html",
                                   max_profile_picture_size=config.MAX_PROFILE_PICTURE_SIZE)


        image = file.read()
        if len(image) > config.MAX_PROFILE_PICTURE_SIZE:
            flash("Error: Image size exceeds the limit", "error")
            return render_template("add_image.html",
                                    max_profile_picture_size=config.MAX_PROFILE_PICTURE_SIZE)

        user_id = session["user_id"]
        users.update_image(user_id, image)
        return redirect("/user/" + str(user_id))

@app.route("/image/<int:user_id>", methods=["GET"])
def show_image(user_id):
    image = users.get_image(user_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/png")
    return response

import db

def get_project(project_id):
    sql = "SELECT id, title, description FROM projects WHERE id = ?"
    return db.query(sql, [project_id])[0]

def add_project(title, parameter_one, parameter_two, max_tasks, description, user_id):
    sql = "INSERT INTO projects (title, parameter_one, parameter_two, max_tasks, description, user_id) VALUES (?, ?, ?, ?, ?, ?)"
    db.execute(sql, [title, parameter_one, parameter_two, max_tasks, description, user_id])
    project_id = db.last_insert_id()

    return project_id
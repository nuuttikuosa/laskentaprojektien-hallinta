import db

def get_project(project_id):
    sql = "SELECT id, name, range_min, range_max, description FROM projects WHERE id = ?"
    return db.query(sql, [project_id])[0]

def add_project(name, range_min, range_max, description, user_id):
    sql = "INSERT INTO projects (name, range_min, range_max, description, user_id) VALUES (?, ?, ?, ?, ?)"
    db.execute(sql, [name, range_min, range_max, description, user_id])
    project_id = db.last_insert_id()

    return project_id
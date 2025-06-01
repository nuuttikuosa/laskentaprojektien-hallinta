import db

def search(keyword):
    sql = """SELECT p.id, p.name, s.name as status
             FROM projects p, project_statuses s
             WHERE p.status_id = s.id
             AND s.name <> 'Deleted'
             AND (p.name LIKE ? OR p.description LIKE ?)
             ORDER BY p.id DESC"""
    keyword = f"%{keyword}%"
    return db.query(sql, [keyword, keyword])


def get_project(project_id):
    sql = """SELECT p.id, p.name, p.range_min, p.range_max, p.description, p.user_id, s.name as status
              FROM projects p, project_statuses s
              WHERE p.status_id = s.id AND
              p.id = ? """
    return db.query(sql, [project_id])[0]

def get_projects():
    sql = """SELECT p.id, p.name
             FROM projects p, project_statuses s
             WHERE p.status_id = s.id AND
             s.name <> 'Deleted'
             ORDER BY p.id DESC"""
    return db.query(sql)

def add_project(name, range_min, range_max, description, user_id):
    sql = "INSERT INTO projects (name, range_min, range_max, description, user_id, status_id) VALUES (?, ?, ?, ?, ?, ?)"
    db.execute(sql, [name, range_min, range_max, description, user_id, 0])
    project_id = db.last_insert_id()

    return project_id

def update_project(name, range_min, range_max, description, project_id):
    sql = """UPDATE projects
             SET name = ?, range_min = ?, range_max = ?, description = ?
             WHERE id = ?"""
    db.execute(sql, [name, range_min, range_max, description, project_id])

def update_project_status(project_id, new_status):
    sql = "UPDATE projects SET status_id = ? WHERE id = ?"
    db.execute(sql, (new_status, project_id))

def get_project_parameters(project_id):
    sql = "SELECT id, name, value FROM project_parameters WHERE project_id = ?"
    return db.query(sql, [project_id])

def add_parameter(name, value, project_id):
    sql = "INSERT INTO project_parameters (name, value, project_id) VALUES (?, ?, ?)"
    db.execute(sql, [name, value, project_id])
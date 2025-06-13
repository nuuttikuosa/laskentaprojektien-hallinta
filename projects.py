import db
import constants

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
    db.execute(sql, [name, range_min, range_max, description, user_id, constants.PROJECT_STATUS_NOT_STARTED])
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

def generate_tasks(min, max, project_id):
    sql = "INSERT INTO tasks (content, updated_at, project_id, status) VALUES (?, datetime('now'),?, ?)"
    for i in range(min, max + 1):
        db.execute(sql, [i, project_id, constants.TASK_STATUS_FREE])

def get_tasks(project_id):
    sql = """SELECT t.id, t.content, t.updated_at, t.user_id, s.name as status
             FROM tasks t, task_statuses s
             WHERE t.status = s.id AND
             t.project_id = ?
             AND s.name <> 'Deleted'
             ORDER BY t.id ASC"""
    return db.query(sql, [project_id])

def get_number_of_tasks(project_id, status):
    sql = """SELECT COUNT(*)
             FROM tasks t
             WHERE t.project_id = ?
             AND t.status = ?"""
    return db.query(sql, [project_id, status])[0][0]

def reserve_tasks(project_id, user_id, number_of_tasks):
    sql = """SELECT id FROM tasks
             WHERE project_id = ? AND status = ?
             ORDER BY content ASC
             LIMIT ?"""
    free_tasks = db.query(sql, [project_id, constants.TASK_STATUS_FREE, number_of_tasks])

    if not free_tasks:
        return 0

    sql = "UPDATE tasks SET user_id = ?, status = ?, updated_at = datetime('now') WHERE id = ?"
    for task in free_tasks:
        task_id = task["id"]
        db.execute(sql, [user_id, constants.TASK_STATUS_ASSIGNED, task_id])



    return len(free_tasks)

def get_user_tasks(user_id):
    sql = """SELECT t.id, t.content, t.updated_at, p.name as project_name, s.name as status
             FROM tasks t, projects p, task_statuses s
             WHERE t.project_id = p.id AND
             t.status = s.id AND
             t.user_id = ?
             AND s.name <> 'Deleted'
             ORDER BY t.id ASC"""
    return db.query(sql, [user_id])
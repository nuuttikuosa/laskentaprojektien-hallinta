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
    sql = """SELECT p.id, p.name, p.range_min, p.range_max,
                    p.description, p.user_id, s.name as status, u.username as username
             FROM projects p, project_statuses s, users u
             WHERE p.status_id = s.id AND
                   p.user_id = u.id AND
                   p.id = ? """
    result = db.query(sql, [project_id])
    return result[0] if result else None

def get_projects():
    sql = """SELECT p.id, p.name
             FROM projects p, project_statuses s
             WHERE p.status_id = s.id AND
             s.name <> 'Deleted'
             ORDER BY p.id DESC"""
    return db.query(sql)

def add_project(name, range_min, range_max, description, user_id, classes):
    sql = """INSERT INTO projects
             (name, range_min, range_max, description, user_id, status_id)
             VALUES (?, ?, ?, ?, ?, ?)"""
    try:
        db.execute(sql, [name, range_min, range_max, description, user_id,
                     constants.PROJECT_STATUS_NOT_STARTED])
    except db.IntegrityError:
        return None
    project_id = db.last_insert_id()

    sql = "INSERT INTO project_classes (project_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [project_id, class_title, class_value])

    return project_id

def update_project(name, range_min, range_max, description, project_id, classes):
    sql = """UPDATE projects
             SET name = ?, range_min = ?, range_max = ?, description = ?
             WHERE id = ?"""
    db.execute(sql, [name, range_min, range_max, description, project_id])

    sql = "DELETE FROM project_classes WHERE project_id = ?"
    db.execute(sql, [project_id])

    sql = "INSERT INTO project_classes (project_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [project_id, class_title, class_value])

def update_project_status(project_id, new_status):
    sql = "UPDATE projects SET status_id = ? WHERE id = ?"
    db.execute(sql, (new_status, project_id))

def get_project_parameters(project_id):
    sql = "SELECT id, name, value FROM project_parameters WHERE project_id = ?"
    return db.query(sql, [project_id])

def add_parameter(name, value, project_id):
    sql = "INSERT INTO project_parameters (name, value, project_id) VALUES (?, ?, ?)"
    db.execute(sql, [name, value, project_id])

def generate_tasks(task_min, task_max, project_id):
    sql = """INSERT INTO tasks
          (content, updated_at, project_id, status_id)
          VALUES (?, datetime('now'),?, ?)"""
    for i in range(task_min, task_max + 1):
        db.execute(sql, [i, project_id, constants.TASK_STATUS_FREE])

def get_tasks(project_id):
    sql = """SELECT t.id, t.content, t.updated_at, t.user_id,
                    u.username as username, s.name as status
             FROM tasks t
             JOIN task_statuses s ON t.status_id = s.id
             LEFT JOIN users u ON t.user_id = u.id
             WHERE t.project_id = ?
             AND s.name <> 'Deleted'
             ORDER BY t.id ASC;"""
    return db.query(sql, [project_id])

def get_number_of_tasks(project_id, status):
    sql = """SELECT COUNT(*)
             FROM tasks t
             WHERE t.project_id = ?
             AND t.status_id = ?"""

    result = db.query(sql, [project_id, status])
    return result[0][0] if result else 0

def reserve_tasks(project_id, user_id, number_of_tasks):
    sql = """SELECT t.id FROM tasks t
             WHERE project_id = ? AND status_id = ?
             ORDER BY CAST(content AS INTEGER) ASC
             LIMIT ?"""
    free_tasks = db.query(sql, [project_id, constants.TASK_STATUS_FREE, number_of_tasks])

    if not free_tasks:
        return 0

    sql = "UPDATE tasks SET user_id = ?, status_id = ?, updated_at = datetime('now') WHERE id = ?"
    for task in free_tasks:
        task_id = task["id"]
        db.execute(sql, [user_id, constants.TASK_STATUS_ASSIGNED, task_id])



    return len(free_tasks)

def get_user_tasks(user_id):
    sql = """SELECT t.id, t.content, t.updated_at, p.name as project_name, s.name as status
             FROM tasks t, projects p, task_statuses s
             WHERE t.project_id = p.id AND
             t.status_id = s.id AND
             t.user_id = ?
             AND s.name <> 'Deleted'
             ORDER BY t.id ASC"""
    return db.query(sql, [user_id])

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes

def get_classes(project_id):
    sql = "SELECT title, value FROM project_classes WHERE project_id = ?"
    return db.query(sql, [project_id])

def mark_task_done(content, user_id, project_id):
    sql = """UPDATE tasks
             SET status_id = ?, updated_at = datetime('now'), user_id = ?
             WHERE content = ? AND project_id = ?"""
    db.execute(sql, [constants.TASK_STATUS_DONE, user_id, content, project_id])

def add_solution(row, user_id, project_id):
    sql = """INSERT INTO solutions (content, user_id, project_id, created_at)
             VALUES (?, ?, ?, datetime('now'))"""
    db.execute(sql, [row, user_id, project_id])

def get_solutions():
    sql = """SELECT s.id, s.content, s.created_at, s.user_id, s.project_id, u.username as username, p.name as project_name
             FROM solutions s, users u, projects p
             WHERE s.user_id = u.id AND
                   s.project_id = p.id
             ORDER BY s.created_at DESC"""
    return db.query(sql)

def get_project_class_value(project_id, title):
    sql = "SELECT value FROM project_classes WHERE project_id = ? AND title = ?"
    result = db.query(sql, [project_id, title])
    return result[0][0] if result else None

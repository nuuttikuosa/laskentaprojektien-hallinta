from werkzeug.security import check_password_hash, generate_password_hash
import db

def create_user(username, email, bio, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, email, bio, password_hash) VALUES (?, ?, ?, ?)"
    db.execute(sql, [username, email, bio, password_hash ])

    return db.last_insert_id()

def check_login(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])

    if len(result) == 1:
        user_id, password_hash = result[0]
        if check_password_hash(password_hash, password):
            return user_id

    return None
def get_user(user_id):
    sql = """SELECT id, username, email, bio, image IS NOT NULL has_image
             FROM users
             WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None

def update_image(user_id, image):
    sql = "UPDATE users SET image = ? WHERE id = ?"
    db.execute(sql, [image, user_id])

def get_image(user_id):
    sql = "SELECT image FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0][0] if result else None

def get_tasks(user_id):
    sql = """SELECT t.id,
                    t.content,
                    t.project_id,
                    p.name AS project_name,
                    t.updated_at,
                    ts.name AS status
             FROM tasks t, projects p, task_statuses ts
             WHERE t.project_id = p.id AND
                   t.status_id = ts.id AND
                   t.user_id = ?
             ORDER BY t.updated_at DESC"""
    return db.query(sql, [user_id])

def save_log_file(user_id, log_file):

    sql = """INSERT INTO user_logs (user_id, content, uploaded_at)
             VALUES (?, ?, datetime('now'))"""
    db.execute(sql, [user_id, log_file])

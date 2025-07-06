# hash import
from werkzeug.security import check_password_hash, generate_password_hash
import db
import datetime


def create_user(username, email, bio, password):
    # FLAW # 3: Passwords are stored in plain text
    # This is a security risk, as it allows anyone with access to the database to see
    # the passwords of all users.
    # To fix this, we should store passwords as hashes using a secure hashing algorithm.
    # The following line is commented out to avoid using the insecure password storage.
    password_hash = generate_password_hash(password)

    # password_hash = password  # Insecure storage, for demonstration purposes only
    sql = "INSERT INTO users (username, email, bio, password_hash) VALUES (?, ?, ?, ?)"
    db.execute(sql, [username, email, bio, password_hash])

    return db.last_insert_id()


def check_login(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])

    if len(result) == 1:
        # FLAW # 3: Passwords are stored in plain text
        # This is a security risk, as it allows anyone with access to the database to see
        # the passwords of all users.
        # To fix this, we should store passwords as hashes using a secure hashing algorithm.
        # The following line is commented out to avoid using the insecure password check.

        # user_id, password_hash = result[0]
        # if check_password_hash(password_hash, password):

        # Insecure storage, for demonstration purposes only
        user_id, stored_password = result[0]
        if stored_password == password:
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


def get_user_by_username(username):
    sql = "SELECT id, password_hash, failed_logins, lockout_until FROM users WHERE username = ?"
    result = db.query(sql, [username])
    return result[0] if result else None


def update_failed_logins(user_id, failed_logins, lockout_until):
    sql = "UPDATE users SET failed_logins = ?, lockout_until = ? WHERE id = ?"
    db.execute(sql, [failed_logins, lockout_until, user_id])


def log_login_attempt(username: str, user_id: int | None, success: bool):
    sql = """
      INSERT INTO login_audit (username, user_id, success, attempted_at)
      VALUES (?, ?, ?, ?)
    """
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    db.execute(sql, [username, user_id, int(success), timestamp])

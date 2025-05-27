from werkzeug.security import check_password_hash, generate_password_hash
import db

def create_user(username, password, email):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)"
    db.execute(sql, [username, password_hash, email])

def check_login(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])

    if len(result) == 1:
        user_id, password_hash = result[0]
        if check_password_hash(password_hash, password):
            return user_id

    return None

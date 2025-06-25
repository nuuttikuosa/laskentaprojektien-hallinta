import random
import sqlite3

import constants
# This script seeds the database with test data.
db = sqlite3.connect("database.db")


db.execute("DELETE FROM user_logs")
db.execute("DELETE FROM users")
db.execute("DELETE FROM solutions")
db.execute("DELETE FROM project_classes")
db.execute("DELETE FROM project_parameters")
db.execute("DELETE FROM projects")
db.execute("DELETE FROM tasks")

user_count = 1000
project_count = 1000
task_count = 10**8

for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
               ["user" + str(i), "user" + str(i) + "@example.com", "fake_hash"])

for i in range(1, project_count + 1):
    user_id = random.randint(1, user_count)
    db.execute("INSERT INTO projects (name, user_id, status_id) VALUES (?, ?, ?)",
               ["project" + str(i), user_id, constants.PROJECT_STATUS_ONGOING])

for i in range(1, task_count + 1):
    user_id = random.randint(1, user_count)
    project_id = random.randint(1, project_count)
    db.execute("""INSERT INTO tasks (content, updated_at, user_id, project_id, status_id)
                  VALUES (?, datetime('now'), ?, ?, ?)""",
               ["task" + str(i), user_id, project_id, constants.TASK_STATUS_FREE])

db.commit()
db.close()
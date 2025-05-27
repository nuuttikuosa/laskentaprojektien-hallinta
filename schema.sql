CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    email TEXT,
    bio TEXT
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    title TEXT,
    parameter_one INTEGER,
    parameter_two INTEGER,
    description TEXT,
    max_tasks INTEGER,
    user_id INTEGER REFERENCES users
);

CREATE TABLE statuses (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

INSERT INTO statuses (id, name) VALUES
    (0, 'Free'),
    (1, 'Assigned'),
    (2, 'In Progress'),
    (3, 'Done'),
    (4, 'Deleted');

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    task INTEGER,
    content TEXT,
    updated_at TEXT,
    user_id INTEGER REFERENCES users,
    project_id INTEGER REFERENCES projects,
    status INTEGER REFERENCES statuses
);

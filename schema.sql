PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS solutions;
DROP TABLE IF EXISTS user_logs;
DROP TABLE IF EXISTS project_classes;
DROP TABLE IF EXISTS project_parameters;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS project_statuses;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS classes;

PRAGMA foreign_keys = ON;


CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    email TEXT,
    bio TEXT,
    image BLOB
);

CREATE TABLE project_statuses (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    range_min INTEGER,
    range_max INTEGER,
    user_id INTEGER REFERENCES users,
    status_id INTEGER REFERENCES project_statuses
);

CREATE TABLE project_parameters (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects,
    name TEXT,
    value INTEGER
);

CREATE TABLE task_statuses (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,
    updated_at TEXT,
    user_id INTEGER REFERENCES users,
    project_id INTEGER REFERENCES projects,
    status_id INTEGER REFERENCES task_statuses
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE project_classes (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects,
    title TEXT,
    value TEXT
);

CREATE TABLE user_logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    content TEXT,
    uploaded_at TEXT
);

CREATE TABLE solutions (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects,
    user_id INTEGER REFERENCES users,
    content TEXT,
    created_at TEXT
);

CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status_id ON tasks(status_id);
CREATE INDEX idx_tasks_user_updated ON tasks(user_id, updated_at DESC);

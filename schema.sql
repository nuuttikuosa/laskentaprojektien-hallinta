CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    email TEXT,
    bio TEXT
);

CREATE TABLE project_statuses (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

INSERT INTO project_statuses (id, name) VALUES
    (0, 'Not Started'),
    (1, 'Ongoing'),
    (2, 'Completed'),
    (3, 'On Hold'),
    (4, 'Deleted');

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT,
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

INSERT INTO task_statuses (id, name) VALUES
    (0, 'Free'),
    (1, 'Assigned'),
    (2, 'In Progress'),
    (3, 'Done'),
    (4, 'Deleted');

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    content TEXT,
    updated_at TEXT,
    user_id INTEGER REFERENCES users,
    project_id INTEGER REFERENCES projects,
    status INTEGER REFERENCES task_statuses
);

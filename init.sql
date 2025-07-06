DELETE FROM classes;
DELETE FROM project_statuses;
DELETE FROM task_statuses;
DELETE FROM users;

-- FLAW # 4: default user credentials
-- This is a security risk, as it allows anyone to log in with the default credentials.
-- To fix this, we should remove the default user credentials and require users to create their own accounts.


INSERT INTO users (id, username, password_hash) VALUES
    (0, 'admin', 'admin'),
    (1, 'user1', 'user1'),
    (2, 'user2', 'user2');

INSERT INTO project_statuses (id, name) VALUES
    (0, 'Not Started'),
    (1, 'Ongoing'),
    (2, 'Completed'),
    (3, 'On Hold'),
    (4, 'Deleted');

INSERT INTO task_statuses (id, name) VALUES
    (0, 'Free'),
    (1, 'Assigned'),
    (2, 'In Progress'),
    (3, 'Done'),
    (4, 'Deleted');

INSERT INTO classes (title, value) VALUES
    ('Size', 'S - 1 hour'),
    ('Size', 'M - 6 hours'),
    ('Size', 'L - 1 day'),
    ('Size', 'XL - 2 days');

INSERT INTO classes (title, value) VALUES
    ('Type', 'Powersum'),
    ('Type', 'Primes');

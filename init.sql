DELETE FROM classes;
DELETE FROM project_statuses;
DELETE FROM task_statuses;

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

-- DROP SCHEMA public CASCADE;
-- CREATE SCHEMA public;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =========================
-- subscriptions
-- =========================

INSERT INTO subscription (id, type, price, description)
VALUES
    (uuid_generate_v4(), 'free', 0, 'Бесплатный тариф'),
    (uuid_generate_v4(), 'mininal', 100, 'Минимальный тариф'),
    (uuid_generate_v4(), 'medium', 300, 'Средний тариф'),
    (uuid_generate_v4(), 'max', 500, 'Максимальный тариф');

-- =========================
-- users
-- =========================

-- teachers
INSERT INTO "user" (id, email, first_name, middle_name, last_name, role, password_hash)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'teacher1@mail.com', 'Ivan', 'I', 'Ivanov', 'teacher', 'hash1'),
    ('22222222-2222-2222-2222-222222222222', 'teacher2@mail.com', 'Petr', 'P', 'Petrov', 'teacher', 'hash2');

-- students
INSERT INTO "user" (id, email, first_name, middle_name, last_name, role, password_hash)
VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'student1@mail.com', 'Student', 'S', 'Test', 'student', 'hash3'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'student2@mail.com', 'Masha', 'M', 'Ivanova', 'student', 'hash4');

-- =========================
-- teacher_students
-- =========================

INSERT INTO teacher_students VALUES
    ('11111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
    ('11111111-1111-1111-1111-111111111111', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
    ('22222222-2222-2222-2222-222222222222', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa');

-- =========================
-- classroom
-- =========================

INSERT INTO classroom (id, name, teacher_id)
VALUES
    ('33333333-3333-3333-3333-333333333333', 'Class A', '11111111-1111-1111-1111-111111111111'),
    ('44444444-4444-4444-4444-444444444444', 'Class B', '22222222-2222-2222-2222-222222222222');

-- =========================
-- classroom_students
-- =========================

INSERT INTO classroom_students VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '33333333-3333-3333-3333-333333333333'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '33333333-3333-3333-3333-333333333333');

-- =========================
-- task
-- =========================

INSERT INTO task (id, name, type, max_point, teacher_id, deadline)
VALUES
    ('55555555-5555-5555-5555-555555555555', 'Task 101', 'dictation', 10, '11111111-1111-1111-1111-111111111111', now() + interval '7 day'),
    ('66666666-6666-6666-6666-666666666666', 'Task 102', 'composition', 15, '22222222-2222-2222-2222-222222222222', now() - interval '3 day'); -- просрочен

-- =========================
-- work
-- =========================

INSERT INTO work (id, status, files_url, task_id, student_id, finish_date)
VALUES
    ('77777777-7777-7777-7777-777777777777', 'executing', 'url1', '55555555-5555-5555-5555-555555555555', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', now()),
    ('88888888-8888-8888-8888-888888888888', 'draft', 'url2', '55555555-5555-5555-5555-555555555555', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', null),
    ('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee', 'archived', 'url4', '66666666-6666-6666-6666-666666666666', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', now() - interval '10 day'), -- edge-case
    ('99999999-9999-9999-9999-999999999999', 'checking', 'url3', '66666666-6666-6666-6666-666666666666', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', now() - interval '2 day');


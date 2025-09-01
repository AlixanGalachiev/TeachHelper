-- DROP SCHEMA public CASCADE;
-- CREATE SCHEMA public;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =========================
-- subscriptions
-- =========================
CREATE TABLE subscription (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(50) NOT NULL,
    price INT NOT NULL,
    description VARCHAR(250) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO subscription (id, type, price, description)
VALUES
    (uuid_generate_v4(), 'free', 0, 'Бесплатный тариф'),
    (uuid_generate_v4(), 'mininal', 100, 'Минимальный тариф'),
    (uuid_generate_v4(), 'medium', 300, 'Средний тариф'),
    (uuid_generate_v4(), 'max', 500, 'Максимальный тариф');

-- =========================
-- users
-- =========================
CREATE TABLE "user" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50),
    role VARCHAR(50) NOT NULL DEFAULT 'student',
    password_hash VARCHAR(255) NOT NULL,
    subscription_id UUID REFERENCES subscription(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

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
-- teacher_students (связь many-to-many)
-- =========================
CREATE TABLE teacher_students (
    teacher_id UUID REFERENCES "user"(id),
    student_id UUID REFERENCES "user"(id),
    PRIMARY KEY (teacher_id, student_id)
);

INSERT INTO teacher_students VALUES
    ('11111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
    ('11111111-1111-1111-1111-111111111111', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
    ('22222222-2222-2222-2222-222222222222', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa');

-- =========================
-- classroom
-- =========================
CREATE TABLE classroom (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL,
    teacher_id UUID REFERENCES "user"(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO classroom (id, name, teacher_id)
VALUES
    ('33333333-3333-3333-3333-333333333333', 'Class A', '11111111-1111-1111-1111-111111111111'),
    ('44444444-4444-4444-4444-444444444444', 'Class B', '22222222-2222-2222-2222-222222222222');

-- =========================
-- classroom_students
-- =========================
CREATE TABLE classroom_students (
    student_id UUID REFERENCES "user"(id),
    classroom_id UUID REFERENCES classroom(id),
    PRIMARY KEY (student_id, classroom_id)
);

INSERT INTO classroom_students VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '33333333-3333-3333-3333-333333333333'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '33333333-3333-3333-3333-333333333333');

-- =========================
-- task
-- =========================
CREATE TABLE task (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    files VARCHAR(250),
    max_point INT NOT NULL,
    description VARCHAR(150),
    created_at TIMESTAMPTZ DEFAULT now(),
    deadline TIMESTAMPTZ,
    teacher_id UUID REFERENCES "user"(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO task (id, name, type, max_point, teacher_id)
VALUES
    ('55555555-5555-5555-5555-555555555555', 'Task 101', 'dictation', 10, '11111111-1111-1111-1111-111111111111'),
    ('66666666-6666-6666-6666-666666666666', 'Task 102', 'composition', 15, '22222222-2222-2222-2222-222222222222');

-- =========================
-- work
-- =========================
CREATE TABLE work (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    files VARCHAR(100) NOT NULL,
    points INT,
    finish_date TIMESTAMPTZ,
    task_id UUID REFERENCES task(id),
    student_id UUID REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO work (id, status, files, task_id, student_id)
VALUES
    ('77777777-7777-7777-7777-777777777777', 'executing', 'url1', '55555555-5555-5555-5555-555555555555', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
    ('88888888-8888-8888-8888-888888888888', 'draft', 'url2', '55555555-5555-5555-5555-555555555555', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
    ('99999999-9999-9999-9999-999999999999', 'checking', 'url3', '66666666-6666-6666-6666-666666666666', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa');

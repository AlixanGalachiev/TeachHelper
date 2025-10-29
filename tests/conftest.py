import os
import uuid

import pytest_asyncio

from app.models.model_classroom import Classrooms
from app.models.model_tasks import ExerciseCriterions, Exercises, Subjects, Tasks
from app.models.model_users import Users
from app.schemas.schema_classroom import SchemaClassroom
from app.utils.oAuth import create_access_token

os.environ["ENV_FILE"] = ".env_test" #важно, если оно будет после импорта app переменная не подбросится и тесты снесут бой :)
from app.schemas.schema_auth import UserRegister

from httpx import ASGITransport, AsyncClient
import pytest
from app.models.base import Base
from main import app
from app.db import AsyncSessionLocal, engine_async
from app.config.config_app import settings

@pytest_asyncio.fixture(scope="function", autouse=False)
async def async_session():
    async with AsyncSessionLocal() as session:
        yield session

@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_db():
    print("setup_db")
    async with engine_async.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        admin = Users(
            first_name="Admin",
            last_name="Test",
            email="admin_test@example.com",
            password="123456",
            role="admin",
            is_verificated=True
        )

        teacher = Users(
            first_name="Teacher",
            last_name="Test",
            email="teacher_test@example.com",
            password="123456",
            role="teacher",
            is_verificated=True
        )

        student = Users(
            first_name="Student",
            last_name="Test",
            email="student_test@example.com",
            password="123456",
            role="student",
            is_verificated=True
        )

        subject = Subjects(name="Math")

        session.add_all([admin, subject, teacher, student,])
        await session.commit() 
        await session.refresh(admin)
        await session.refresh(teacher)
        await session.refresh(student)
        await session.refresh(subject)

        classroom = Classrooms(
            name="test room",
            teacher_id = teacher.id
        )

        task = Tasks(
            subject_id= subject.id,
            teacher_id= teacher.id,
            name= "Задача conftest",
            description= "Тестовая задача созданная в conftest",

            exercises = [
                Exercises(
                    name="Посчитай 10",
                    description="Очень важно",
                    order_index=1,
                    criterions=[
                        ExerciseCriterions(
                            name="Посчитал до 10",
                            score=1
                        )
                    ]
                )
            ]
        )
        session.add_all([task, classroom])
        await session.commit()
        await session.aclose()

        yield {
            "teacher_id": teacher.id,
            "student_id": student.id,
            "subject_id": subject.id,
            "task_id": task.id,
            "classroom_id": classroom.id,
        }


@pytest.fixture(scope="function")
def teacher_id(setup_db) -> uuid.UUID:
    return setup_db["teacher_id"]

@pytest.fixture(scope="function")
def student_id(setup_db) -> uuid.UUID:
    return setup_db["student_id"]

@pytest.fixture(scope="function")
def subject_id(setup_db) -> uuid.UUID:
    return setup_db["subject_id"]

@pytest.fixture(scope="function")
def task_id(setup_db) -> uuid.UUID:
    return setup_db["task_id"]

@pytest.fixture(scope="function")
def classroom_id(setup_db) -> uuid.UUID:
    return setup_db["classroom_id"]

@pytest.fixture(scope="function")
def session_token_admin():
    token = create_access_token({"email": "admin_test@example.com"}, settings.SECRET)
    return f"Bearer {token}"

@pytest.fixture(scope="function")
def session_token_teacher():
    token = create_access_token({"email": "teacher_test@example.com"}, settings.SECRET)
    return f"Bearer {token}"

@pytest.fixture(scope="function")
def session_token_student():
    token = create_access_token({"email": "student_test@example.com"}, settings.SECRET)
    return f"Bearer {token}"


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client   


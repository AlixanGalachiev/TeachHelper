import asyncio
import os

import pytest_asyncio

from app.schemas.schema_classroom import SchemaClassroom
from app.utils.oAuth import create_access_token

os.environ["ENV_FILE"] = ".env_test" #важно, если оно будет после импорта app переменная не подбросится и тесты снесут бой :)
from app.schemas.schema_auth import UserRegister

from httpx import ASGITransport, AsyncClient
import pytest
from app.models.base import Base
from main import app
from app.db import AsyncSessionLocal, engine, engine_async, get_async_session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


from app.config.config_app import settings

@pytest.fixture(scope="session")
def session_teacher_data() -> UserRegister:
    return UserRegister(
        first_name="Teacher",
        last_name="Test",
        email="teacher_test@example.com",
        password="123456",
        role="teacher"
    )

@pytest.fixture(scope="session")
def session_student_data() -> UserRegister:
    return UserRegister(
        first_name="Student",
        last_name="Test",
        email="student_test@example.com",
        password="123456",
        role="student"
    )


@pytest.fixture(scope="function")
def session_token_teacher(session_teacher_data):
    token = create_access_token({"email": session_teacher_data.email}, settings.SECRET)
    return f"Bearer {token}"

@pytest_asyncio.fixture(loop_scope="session", scope="module", autouse=True)
async def setup_db():
    print("setup_db")
    async with engine_async.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("setup_db ready")
    yield

@pytest_asyncio.fixture(loop_scope="session", scope="module", autouse=True)
async def prepare_db(setup_db, session_teacher_data, session_student_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        teacher_response = await client.post("/auth/register", json=session_teacher_data.model_dump())
        teacher_db = teacher_response.json()
        print(teacher_db)
        confirm_token_teacher = create_access_token({"email": session_teacher_data.email}, settings.SECRET_CONFIRM_KEY)
        await client.post("/auth/confirm_email", params={'token': f"Bearer {confirm_token_teacher}"})

        token_teacher = create_access_token({"email": session_teacher_data.email}, settings.SECRET)
        await client.post("/classrooms", headers={"Authorization": f"Bearer {token_teacher}"}, params={'name': f"room1"})


        student_response = await client.post("/auth/register", json=session_student_data.model_dump())
        student_db = student_response.json()
        
        confirm_token_student = create_access_token({"email": session_student_data.email}, settings.SECRET_CONFIRM_KEY)
        token_student = create_access_token({"email": session_student_data.email}, settings.SECRET)
        await client.post("/auth/confirm_email", params={'token': f"Bearer {confirm_token_student}"})
        await client.post(f"teachers/{teacher_db['id']}",  headers={"Authorization": f"Bearer {token_student}"})


@pytest_asyncio.fixture(scope="function")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client   


# tests/test_config.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from app.db import get_async_session
from app.models.base import Base
from app.models.model_user import User, RoleUser
from app.utils.password import get_password_hash
from main import app

from app.settings import settings

# Создаём движок и одно соединение
sync_engine = create_engine(settings.sync_url, future=True)
async_engine = create_async_engine(settings.test_async_url, echo=False, future=True)


@pytest.fixture(scope="session", autouse=True)
def prepare_db():
	Base.metadata.drop_all(sync_engine)
	Base.metadata.create_all(sync_engine)
	sync_engine.dispose()

@pytest_asyncio.fixture(scope="session")
async def connection():
    yield async_engine
    await async_engine.dispose()

@pytest_asyncio.fixture
async def session(connection):
	async_session = async_sessionmaker(bind=connection, expire_on_commit=False, class_=AsyncSession)
	async with async_session() as session:
		yield session



# Подменяем зависимостьp
@pytest_asyncio.fixture(autouse=True)
async def override_get_async_session_fixture(session):
	async def _get_session_override():
		yield session
	app.dependency_overrides[get_async_session] = _get_session_override

@pytest_asyncio.fixture
async def async_client():
	async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
		yield ac


@pytest_asyncio.fixture
async def repo_user(session):
	repo = UserRepo(session)
	return repo


@pytest_asyncio.fixture
async def users(session):
	"""
	Создаёт двух пользователей: студента и учителя.
	Возвращает словарь: {'student': User, 'teacher': User}
	"""
	student = User(
		email="student@test.com",
		password_hash=get_password_hash("student123"),
		first_name="Student",
		middle_name="S",
		last_name="Test",
		role=RoleUser.student
	)

	teacher = User(
		email="teacher@test.com",
		password_hash=get_password_hash("teacher123"),
		first_name="Teacher",
		middle_name="T",
		last_name="Test",
		role=RoleUser.teacher,
		students = [student]
	)

	session.add_all([student, teacher])
	await session.commit()  # чтобы появились id
	await session.refresh(student)
	await session.refresh(teacher)
	

	# student = await session.execute(select(User).where(User.id == student.id).options(selectinload(User.works))).scalar_one_or_none()
	# teacher = await session.execute(select(User).where(User.id == teacher.id).options(selectinload(User.tasks))).scalar_one_or_none()
	# # await session.commit()

	return {"student": student, "teacher": teacher}
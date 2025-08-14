# tests/test_config.py
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db import get_async_session
from app.models.base import Base
from main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Создаём движок и одно соединение
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)

@pytest_asyncio.fixture(scope="session")
async def connection():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()

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

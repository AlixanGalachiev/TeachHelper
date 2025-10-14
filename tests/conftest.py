# tests/test_config.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine, text
from app.db import get_async_session
from app.models.base import Base

from main import app
import re
from pathlib import Path
from pprint import pprint

from app.config.config_app import settings
from dotenv import load_dotenv

load_dotenv()

# Создаём движок и одно соединение
sync_engine = create_engine(settings.sync_url, future=True)
async_engine = create_async_engine(settings.test_async_url, echo=False, future=True)

@pytest.fixture(scope="session", autouse=True)
def prepare_db():
	# дропаем и создаём заново
	Base.metadata.drop_all(sync_engine)
	Base.metadata.create_all(sync_engine)

	# загружаем дамп
	sql_file = Path(__file__).parent / "dumps" / "updated.sql"
	with open(sql_file, "r", encoding="utf-8") as f:
		sql_text = f.read()

	sql_text = re.sub(r"/\*.*?\*/", "", sql_text, flags=re.S)
	sql_text = re.sub(r"--.*?$", "", sql_text, flags=re.M)
	sql_lines = [line for line in sql_text.splitlines() if not line.strip().startswith("--")]
	clean_sql = "\n".join(sql_lines)

	# исполняем сразу весь дамп
	with sync_engine.connect() as conn:
		for statement in clean_sql.split(";"):
			stmt = statement.strip()
			print('<pre')
			pprint(stmt)
			print('pre>')
			if not stmt or stmt.startswith("--") or stmt.startswith("/*"):
				continue
			conn.execute(text(stmt))
		conn.commit()

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


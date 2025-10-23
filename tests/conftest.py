import asyncio
import os
os.environ["ENV_FILE"] = ".env_test" #важно, если оно будет после импорта app переменная не подбросится и тесты снесут бой :)

from httpx import ASGITransport, AsyncClient
import pytest
from app.models.base import Base
from main import app
from app.db import engine, engine_async

from app.config.config_app import settings



@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)



@pytest.fixture(scope="function")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client



from app.config.config_app import settings
from contextlib import contextmanager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker


from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine


engine = create_engine(settings.sync_url, future=True)
engine_async = create_async_engine(settings.async_url, future=True)

# Create async engine & session maker
AsyncSessionLocal = async_sessionmaker(bind=engine_async, expire_on_commit=False, class_=AsyncSession)
SyncSessionLocal = sessionmaker(bind=engine)

async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session


@contextmanager
def get_sync_session():
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()
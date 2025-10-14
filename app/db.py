from contextlib import asynccontextmanager, contextmanager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from app.config.config_app import get_async_engine, get_sync_engine

# Create async engine & session maker
_async_engine = get_async_engine()
AsyncSessionLocal = async_sessionmaker(bind=_async_engine, expire_on_commit=False, class_=AsyncSession)
SyncSessionLocal = sessionmaker(bind=get_sync_engine())

async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@contextmanager
def get_sync_session() -> Session:
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()
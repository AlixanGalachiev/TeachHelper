from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.settings import get_async_engine

# Create async engine & session maker
_async_engine = get_async_engine()
AsyncSessionLocal = async_sessionmaker(bind=_async_engine, expire_on_commit=False, class_=AsyncSession)


async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
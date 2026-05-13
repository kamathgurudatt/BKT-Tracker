from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()
engine = None
AsyncSessionLocal = None
try:
    if settings.database_url:
        engine = create_async_engine(settings.database_url, pool_pre_ping=True, future=True)
        AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
except Exception:
    engine = None
    AsyncSessionLocal = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if AsyncSessionLocal is None:
        raise RuntimeError("Database session factory unavailable")
    async with AsyncSessionLocal() as session:
        yield session

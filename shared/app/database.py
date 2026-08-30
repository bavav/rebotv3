# shared/app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from shared.app.config import BaseAppSettings

engine = None
AsyncSessionLocal = None

async def init_database(settings: BaseAppSettings):
    global engine, AsyncSessionLocal
    engine = create_async_engine(settings.postgres_dsn, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    # Создание таблиц (для MVP можно так, потом перейдём на Alembic)
    from shared.app.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not initialized")
    async with AsyncSessionLocal() as session:
        yield session
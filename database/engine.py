from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from database.models import Base
from config_data.config import ExpectedEnvs, MAIN_ENV


engine = create_async_engine(MAIN_ENV.get(ExpectedEnvs.database.value), echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_db():
    """Функция создания и подключения к базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """Функция очистки, создания и подключения к базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

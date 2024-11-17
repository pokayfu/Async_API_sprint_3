from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from file_api.src.core.config import pg_settings

Base = declarative_base()
engine = create_async_engine(pg_settings.url, future=True)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            print(e)
            await session.rollback()
            raise
        finally:
            await session.close()

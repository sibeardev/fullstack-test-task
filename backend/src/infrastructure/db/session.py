from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.config import DATABASE_URL, DEBUG

engine = create_async_engine(DATABASE_URL, echo=DEBUG)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

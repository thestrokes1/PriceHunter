import ssl as ssl_lib

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from backend.config import settings


# Render's managed Postgres requires SSL/TLS, but asyncpg does not negotiate it
# by default, so startup fails with
# "InvalidAuthorizationSpecificationError: SSL/TLS required".
# Pass an explicit SSLContext (the form asyncpg always honors) for Postgres URLs
# while leaving sqlite (local dev) untouched.
connect_args = {}
if "postgres" in settings.database_url:
    ssl_ctx = ssl_lib.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl_lib.CERT_NONE
    connect_args["ssl"] = ssl_ctx

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    connect_args=connect_args,
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

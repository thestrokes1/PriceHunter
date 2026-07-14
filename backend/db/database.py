from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from backend.config import settings


# Render's managed Postgres requires SSL/TLS on external connections. asyncpg
# does not enable it by default, so the connection is rejected with
# "InvalidAuthorizationSpecificationError: SSL/TLS required". Request SSL for
# Postgres URLs while leaving sqlite (local dev) untouched.
connect_args = {}
if settings.database_url.startswith("postgresql"):
    connect_args["ssl"] = "require"

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

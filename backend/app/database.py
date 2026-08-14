from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()

_connect_args: dict = {}
if "ssl=require" in settings.database_url or "neon.tech" in settings.database_url:
    # Neon / managed Postgres require TLS
    _connect_args["ssl"] = True

engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args=_connect_args,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text(
                "ALTER TABLE users "
                "ADD COLUMN IF NOT EXISTS full_name VARCHAR(120) NOT NULL DEFAULT ''"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE opportunities "
                "ADD COLUMN IF NOT EXISTS position VARCHAR(255) NOT NULL DEFAULT ''"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE opportunities "
                "ADD COLUMN IF NOT EXISTS governorate VARCHAR(64) NOT NULL DEFAULT ''"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE opportunities "
                "ADD COLUMN IF NOT EXISTS category VARCHAR(32) NOT NULL DEFAULT 'job'"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE opportunities "
                "ADD COLUMN IF NOT EXISTS ai_classified BOOLEAN NOT NULL DEFAULT FALSE"
            )
        )

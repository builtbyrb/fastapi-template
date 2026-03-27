import contextlib
from collections.abc import AsyncIterator
from typing import Any

import redis.asyncio as redis
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import src.users.models  # noqa: F401
from src.core.config.env import APP_ENV
from src.core.models import Base


class DatabaseSessionManager:
    def __init__(
        self, url: str | URL, engine_kwargs: dict[str, Any] | None = None
    ) -> None:
        if engine_kwargs is None:
            engine_kwargs = {}
        self._engine = create_async_engine(url, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(bind=self._engine)

    async def close(self) -> None:
        await self._engine.dispose()

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class RedisManager:
    def __init__(self, url: str) -> None:
        self.url = url
        self.client: redis.Redis | None = None

    async def init(self) -> None:
        self.client = redis.Redis.from_url(
            self.url,
            protocol=3,
            socket_timeout=5,
            socket_connect_timeout=2,
            health_check_interval=30,
            retry_on_timeout=True,
        )

    async def close(self) -> None:
        if self.client:
            await self.client.aclose()
            self.client = None


session_manager = DatabaseSessionManager(
    URL.create(
        drivername=APP_ENV.POSTGRES_DRIVER_NAME,
        username=APP_ENV.POSTGRES_USER,
        password=APP_ENV.POSTGRES_PASSWORD,
        host=APP_ENV.PG_BOUNCER_HOST,
        port=APP_ENV.PG_BOUNCER_PORT,
        database=APP_ENV.POSTGRES_DB,
    ),
    engine_kwargs={
        "pool_size": 50,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    },
)

redis_manager = RedisManager(
    f"redis://{APP_ENV.REDIS_HOST}:{APP_ENV.REDIS_PORT}/{APP_ENV.REDIS_DB}"
)


async def create_db_and_tables() -> None:
    async with session_manager.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)

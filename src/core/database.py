import contextlib
from typing import TYPE_CHECKING, Any

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import src.refresh_token.models
import src.users.models  # noqa: F401
from src.core.domain.exceptions import ResourceNotInitialized
from src.core.settings import APP_ENV_SETTINGS


if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from sqlalchemy import URL


class SqlDatabaseManager:
    def __init__(
        self, url: str | URL, engine_kwargs: dict[str, Any] | None = None
    ) -> None:
        self.url = url
        self.engine_kwargs = engine_kwargs or {}
        self._engine: AsyncEngine | None = None
        self._sql_session_maker: async_sessionmaker[AsyncSession] | None = None

    @property
    def engine(self) -> AsyncEngine:
        if not self._engine:
            raise ResourceNotInitialized(self.__class__.__name__)
        return self._engine

    @property
    def sql_session_maker(self) -> async_sessionmaker[AsyncSession]:
        if not self._sql_session_maker:
            raise ResourceNotInitialized(self.__class__.__name__)
        return self._sql_session_maker

    async def init(self) -> None:
        self._engine = create_async_engine(self.url, **self.engine_kwargs)
        self._sql_session_maker = async_sessionmaker(bind=self._engine)

    async def close(self) -> None:
        await self.engine.dispose()
        self._engine = None
        self._sql_session_maker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        async with self.engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def sql_session(self) -> AsyncIterator[AsyncSession]:
        sql_session = self.sql_session_maker()
        try:
            yield sql_session
        except Exception:
            await sql_session.rollback()
            raise
        finally:
            await sql_session.close()


class RedisManager:
    def __init__(self, url: str) -> None:
        self.url = url
        self._client: redis.Redis | None = None
        self.exc_msg = "RedisManager is not initialized. Call init() first."

    @property
    def client(self) -> redis.Redis:
        if not self._client:
            raise ResourceNotInitialized(self.__class__.__name__)
        return self._client

    async def init(self) -> None:
        self._client = redis.Redis.from_url(
            self.url,
            protocol=3,
            socket_timeout=5,
            socket_connect_timeout=2,
            health_check_interval=30,
            retry_on_timeout=True,
        )

    async def close(self) -> None:
        await self.client.aclose()
        self._client = None


SQL_DATABASE_MANGER = SqlDatabaseManager(
    APP_ENV_SETTINGS.pgbouncer_database_url,
    engine_kwargs={
        "pool_size": 50,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    },
)

REDIS_MANGER = RedisManager(
    f"redis://{APP_ENV_SETTINGS.REDIS_HOST}:{APP_ENV_SETTINGS.REDIS_PORT}/{APP_ENV_SETTINGS.REDIS_DB}"
)

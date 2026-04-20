import contextlib
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, Any

import redis.asyncio as redis
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.config.settings import APP_ENV_SETTINGS
from src.shared.exceptions import AppException


class Base(DeclarativeBase):
    pass


class ResourceNotInitializedContext(BaseModel):
    resource_name: str


class ResourceNotInitializedException(AppException):
    def __init__(self, context: ResourceNotInitializedContext) -> None:
        super().__init__(
            message=f"Resource {context.resource_name} was not initialized",
            context=context,
        )


@dataclass(kw_only=True, frozen=True)
class DatabaseProviders:
    sql_session: AsyncSession
    redis_client: redis.Redis


async def get_sql_db_session() -> AsyncIterator[AsyncSession]:
    async with SQL_DATABASE_MANGER.sql_session() as sql_session:
        yield sql_session


async def get_redis_client() -> redis.Redis:
    return REDIS_MANGER.client


async def get_database_providers(
    sql_session: SqlSessionDep,
    redis_client: RedisClientDep,
) -> DatabaseProviders:
    return DatabaseProviders(sql_session=sql_session, redis_client=redis_client)


DatabaseProvidersDep = Annotated[DatabaseProviders, Depends(get_database_providers)]
RedisClientDep = Annotated[redis.Redis, Depends(get_redis_client)]
SqlSessionDep = Annotated[AsyncSession, Depends(get_sql_db_session)]


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
            raise ResourceNotInitializedException(
                ResourceNotInitializedContext(resource_name=self.__class__.__name__)
            )
        return self._engine

    @property
    def sql_session_maker(self) -> async_sessionmaker[AsyncSession]:
        if not self._sql_session_maker:
            raise ResourceNotInitializedException(
                ResourceNotInitializedContext(resource_name=self.__class__.__name__)
            )
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
            raise ResourceNotInitializedException(
                ResourceNotInitializedContext(resource_name=self.__class__.__name__)
            )
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

import pytest
import redis.asyncio as redis
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.database.database import (
    REDIS_MANGER,
    SQL_DATABASE_MANGER,
    CreateRedisUrlParams,
    CreateSqlalchemyUrlParams,
    ResourceNotInitializedException,
    create_redis_url,
    create_sqlalchemy_url,
    get_redis_client,
    get_sql_db_session,
)


def test_create_redis_url_returns_str() -> None:
    assert isinstance(create_redis_url(CreateRedisUrlParams()), str)


def test_create_sqlalchemy_url_returns_url() -> None:
    assert isinstance(create_sqlalchemy_url(CreateSqlalchemyUrlParams()), URL)


def test_redis_manager_raises_resource_not_initialized_exception_when_not_init() -> (
    None
):
    with pytest.raises(ResourceNotInitializedException):
        _client = REDIS_MANGER.client


@pytest.mark.asyncio
async def test_redis_manager_returns_client_when_init() -> None:
    await REDIS_MANGER.init()
    assert isinstance(REDIS_MANGER.client, redis.Redis)
    await REDIS_MANGER.close()


@pytest.mark.asyncio
async def test_redis_manager_returns_none_when_close() -> None:
    await REDIS_MANGER.init()
    await REDIS_MANGER.close()
    assert not REDIS_MANGER._client


def test_sql_manager_raises_resource_not_initialized_exception_when_not_init() -> (
    None
):
    with pytest.raises(ResourceNotInitializedException):
        _engine = SQL_DATABASE_MANGER.engine

    with pytest.raises(ResourceNotInitializedException):
        _sql_session_maker = SQL_DATABASE_MANGER.sql_session_maker


@pytest.mark.asyncio
async def test_sql_manager_returns_engine_and_session_maker_when_init() -> None:
    await SQL_DATABASE_MANGER.init()
    assert isinstance(SQL_DATABASE_MANGER.engine, AsyncEngine)
    assert isinstance(SQL_DATABASE_MANGER.sql_session_maker, async_sessionmaker)
    await SQL_DATABASE_MANGER.close()


@pytest.mark.asyncio
async def test_sql_manager_returns_none_when_close() -> None:
    await SQL_DATABASE_MANGER.init()
    await SQL_DATABASE_MANGER.close()
    assert not SQL_DATABASE_MANGER._engine
    assert not SQL_DATABASE_MANGER._sql_session_maker


@pytest.mark.asyncio
async def test_sql_manager_session_returns_inactive_session_when_close() -> None:
    await SQL_DATABASE_MANGER.init()
    captured_session = None
    async with SQL_DATABASE_MANGER.sql_session() as session:
        captured_session = session

    assert captured_session
    assert not captured_session.in_transaction()
    await SQL_DATABASE_MANGER.close()


@pytest.mark.asyncio
async def test_sql_manager_session_rollback_when_exception() -> None:
    await SQL_DATABASE_MANGER.init()
    with pytest.raises(RuntimeError):
        async with SQL_DATABASE_MANGER.sql_session() as _session:
            raise RuntimeError

    await SQL_DATABASE_MANGER.close()


@pytest.mark.asyncio
async def test_get_sql_db_session_returns_async_session() -> None:
    await SQL_DATABASE_MANGER.init()
    it = get_sql_db_session()
    async for session in it:
        assert isinstance(session, AsyncSession)
    await SQL_DATABASE_MANGER.close()


@pytest.mark.asyncio
async def test_get_redis_client_returns_redis_client() -> None:
    await REDIS_MANGER.init()
    assert isinstance(await get_redis_client(), redis.Redis)
    await REDIS_MANGER.close()

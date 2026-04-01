from collections.abc import AsyncIterator
from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.constants import Environment
from src.core.config.env import APP_ENV
from src.core.database import redis_manager, session_manager
from src.core.exceptions import AppClientIpNotFound
from src.core.types.internal import DatabaseProviders
from src.core.types.typings import ANY_IP_ADAPTER, IpAnyAddress


async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_manager.session() as session:
        yield session


async def get_redis() -> redis.Redis:
    client = redis_manager.client
    if not client:
        err_msg = "Redis client is not initialized"
        raise RuntimeError(err_msg)
    return client


async def get_database_providers(
    session: SessionDep,
    client: RedisDep,
) -> DatabaseProviders:
    return DatabaseProviders(session=session, client=client)


async def get_client_ip(request: Request) -> IpAnyAddress:
    if APP_ENV.ENVIRONMENT == Environment.DEV:
        return ANY_IP_ADAPTER.validate_python("123.1.1.1")

    ip = request.headers.get("X-Real-Ip")

    if not ip and request.client:
        return ANY_IP_ADAPTER.validate_python(request.client.host)

    if not ip:
        raise AppClientIpNotFound

    return ANY_IP_ADAPTER.validate_python(ip)


IpDep = Annotated[IpAnyAddress, Depends(get_client_ip)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
RedisDep = Annotated[redis.Redis, Depends(get_redis)]
DataBaseProvidersDep = Annotated[
    DatabaseProviders,
    Depends(get_database_providers),
]

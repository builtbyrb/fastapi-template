from collections.abc import AsyncIterator
from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import redis_manager, session_manager
from src.core.domain import resolve_ip_form_data
from src.core.settings import APP_ENV_SETTINGS
from src.core.types.alias import Environment, IpAnyAddress
from src.core.types.internal import DatabaseProviders, ResolveIpFromDataParams


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with session_manager.session() as session:
        yield session


async def get_redis() -> redis.Redis:
    client = redis_manager.client
    if not client:
        err_msg = "Redis client is not initialized"
        raise RuntimeError(err_msg)
    return client


async def get_client_ip(
    request: Request,
    environment: Environment = APP_ENV_SETTINGS.ENVIRONMENT,
    default_dev_ip: str = APP_ENV_SETTINGS.DEFAULT_DEV_IP,
    resolve_ip_header: str = APP_ENV_SETTINGS.RESOLVE_IP_HEADER,
) -> IpAnyAddress:
    return resolve_ip_form_data(
        ResolveIpFromDataParams(
            environment=environment,
            default_dev_ip=default_dev_ip,
            client_host=request.client.host if request.client else None,
            headers=request.headers,
            resolve_ip_header=resolve_ip_header,
        )
    )


async def get_database_providers(
    session: SessionDep,
    client: RedisDep,
) -> DatabaseProviders:
    return DatabaseProviders(session=session, client=client)


IpDep = Annotated[IpAnyAddress, Depends(get_client_ip)]
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
RedisDep = Annotated[redis.Redis, Depends(get_redis)]
DataBaseProvidersDep = Annotated[
    DatabaseProviders,
    Depends(get_database_providers),
]

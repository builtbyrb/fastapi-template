from collections.abc import AsyncIterator
from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import redis_manager, session_manager
from src.core.domain import get_client_ip
from src.core.types.internal import DatabaseProviders
from src.core.types.typings import IpAnyAddress


async def get_db_session() -> AsyncIterator[AsyncSession]:
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


IpDep = Annotated[IpAnyAddress, Depends(get_client_ip)]
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
RedisDep = Annotated[redis.Redis, Depends(get_redis)]
DataBaseProvidersDep = Annotated[
    DatabaseProviders,
    Depends(get_database_providers),
]

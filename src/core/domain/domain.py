from typing import TYPE_CHECKING

import redis.asyncio as redis
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.core.domain.exceptions import (
    ClientIpNotFound,
)
from src.core.types.alias import Environment, IpAnyAddress
from src.core.types.typings import ANY_IP_ADAPTER


if TYPE_CHECKING:
    from src.core.database import SqlDatabaseManager
    from src.core.types.internal import (
        ResolveIpFromDataParams,
    )


def resolve_ip_form_data(params: ResolveIpFromDataParams) -> IpAnyAddress:
    if params.environment == Environment.DEV:
        return ANY_IP_ADAPTER.validate_python(params.default_dev_ip)

    try:
        ip = ANY_IP_ADAPTER.validate_python(
            params.headers.get(params.resolve_ip_header) or params.client_host
        )
    except ValidationError:
        ip = None

    if not ip:
        raise ClientIpNotFound

    return ip


async def check_redis_connectivity(client: redis.Redis) -> bool:
    try:
        ping = client.ping()
        if not isinstance(ping, bool):
            ping = await ping
    except redis.RedisError:
        return False
    else:
        return ping


async def check_sql_db_connectivity(manager: SqlDatabaseManager) -> bool:
    try:
        async with manager.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return False
    else:
        return True

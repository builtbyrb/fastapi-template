import socket
from typing import Annotated, Literal

import redis
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, BeforeValidator
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.database.database import (
    REDIS_MANGER,
    SQL_DATABASE_MANGER,
    RedisManager,
    ResourceNotInitializedException,
    SqlDatabaseManager,
)
from src.shared.web import OpenApiResponse


type Healthy = Literal["healthy"]
type Unhealthy = Literal["unhealthy"]
type HealthValues = Healthy | Unhealthy


def bool_to_health(*, status: bool) -> HealthValues:
    if not status:
        return "unhealthy"
    return "healthy"


type Health = Annotated[
    HealthValues,
    BeforeValidator(
        lambda v: bool_to_health(status=v) if isinstance(v, bool) else v
    ),
]


class DatabaseHealthStatus(BaseModel):
    sql_db_health: Health
    redis_health: Health


class HealthStatus(DatabaseHealthStatus):
    health: Health


class UnhealthyStatus(DatabaseHealthStatus):
    health: Unhealthy


DB_CONNECTIVITY_EXCEPTION = (
    ConnectionError,
    ResourceNotInitializedException,
    socket.error,
)


async def check_redis_connectivity(manager: RedisManager) -> bool:
    try:
        ping = manager.client.ping()
        if not isinstance(ping, bool):
            ping = await ping
    except (redis.RedisError, *DB_CONNECTIVITY_EXCEPTION):
        return False
    else:
        return ping


async def check_sql_db_connectivity(manager: SqlDatabaseManager) -> bool:
    try:
        async with manager.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except (SQLAlchemyError, *DB_CONNECTIVITY_EXCEPTION):
        return False
    else:
        return True


router = APIRouter()

BAD_HEALTH_CHECK_OPENAPI_RESPONSE = OpenApiResponse(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    description="Service unhealthy",
    response_model=UnhealthyStatus,
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Perform a Health Check",
    response_description="Return HTTP 200 if the service is healthy.",
    response_model=HealthStatus,
    responses={**BAD_HEALTH_CHECK_OPENAPI_RESPONSE.openapi_response},
)
async def health() -> HealthStatus | JSONResponse:
    redis_status = await check_redis_connectivity(REDIS_MANGER)
    sql_db_status = await check_sql_db_connectivity(SQL_DATABASE_MANGER)
    app_status = redis_status and sql_db_status

    health_status = HealthStatus.model_validate(
        {
            "health": app_status,
            "redis_health": redis_status,
            "sql_db_health": sql_db_status,
        }
    )

    if not app_status:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=health_status.model_dump(),
        )

    return health_status

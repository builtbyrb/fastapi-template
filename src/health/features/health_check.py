from typing import Annotated, Literal

import redis.asyncio as redis
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, BeforeValidator
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.database.database import (
    REDIS_MANGER,
    SQL_DATABASE_MANGER,
    ResourceNotInitializedException,
    SqlDatabaseManager,
)


type HealthValues = Literal["healthy", "unhealthy"]


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


class HealthStatus(BaseModel):
    redis_health: Health
    sql_db_health: Health
    health: Health


async def check_redis_connectivity(client: redis.Redis) -> bool:
    try:
        ping = client.ping()
        if not isinstance(ping, bool):
            ping = await ping
    except redis.RedisError, ConnectionError, ResourceNotInitializedException:
        return False
    else:
        return ping


async def check_sql_db_connectivity(manager: SqlDatabaseManager) -> bool:
    try:
        async with manager.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except SQLAlchemyError, ConnectionError, ResourceNotInitializedException:
        return False
    else:
        return True


router = APIRouter()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Perform a Health Check",
    response_description="Return HTTP 200 if the service is healthy.",
    response_model=HealthStatus,
    responses={
        500: {
            "description": "Service unhealthy",
            "model": HealthStatus,
        }
    },
)
async def health() -> HealthStatus | JSONResponse:
    redis_status = await check_redis_connectivity(REDIS_MANGER.client)
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

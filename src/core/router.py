from fastapi import APIRouter, status

from src.core.database import REDIS_MANGER, SQL_DATABASE_MANGER
from src.core.domain.domain import (
    check_redis_connectivity,
    check_sql_db_connectivity,
)
from src.core.types.schemas import HealthStatus


health_router = APIRouter(prefix="/health", tags=["Health"])


@health_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Perform a Health Check",
    response_description="Return HTTP 200 if the service is healthy.",
    response_model=HealthStatus,
)
async def health() -> dict[str, bool]:
    redis_status = await check_redis_connectivity(REDIS_MANGER.client)
    sql_db_status = await check_sql_db_connectivity(SQL_DATABASE_MANGER)
    status = redis_status and sql_db_status

    return {
        "health": status,
        "redis_health": redis_status,
        "sql_db_health": sql_db_status,
    }

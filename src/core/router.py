from fastapi import APIRouter, status

from src.core.database import redis_manager, sql_database_manager
from src.core.domain import check_redis_connectivity, check_sql_db_connectivity
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
    redis_status = await check_redis_connectivity(redis_manager.client)
    sql_db_status = await check_sql_db_connectivity(sql_database_manager)
    status = redis_status and sql_db_status

    return {
        "health": status,
        "redis_health": redis_status,
        "sql_db_health": sql_db_status,
    }

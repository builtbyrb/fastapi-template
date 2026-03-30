from fastapi import APIRouter, status

from src.core.types.schemas import HealthStatus


health_router = APIRouter(prefix="/health", tags=["Health"])


@health_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Perform a Health Check",
    response_description="Return HTTP 200 if the service is healthy.",
    response_model=HealthStatus,
)
async def health() -> dict[str, str]:
    return {"status": "healthy"}

from fastapi import APIRouter

from src.health.features.health_check import router as health_check_router


health_router = APIRouter(prefix="/health", tags=["Health"])

health_router.include_router(health_check_router)

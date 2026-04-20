from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from src.app.exceptions_handler import app_http_exception_handler
from src.app.lifespan import lifespan
from src.health.router import health_router
from src.shared.exceptions import AppException
from src.telemetry.middleware import (
    AccessLoggingMiddleware,
)
from src.users.router import user_router


app = FastAPI(lifespan=lifespan)
app.include_router(health_router)
app.include_router(user_router)

app.add_middleware(AccessLoggingMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_exception_handler(AppException, app_http_exception_handler)

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from src.auth.router import token_router
from src.core.exceptions import (
    WithHttpException,
    setup_sync_uncaught_exception_handler,
    with_http_exception_handler,
)
from src.core.lifespan import lifespan
from src.core.logging.logging import setup_logging
from src.core.middleware import (
    AccessLoggingMiddleware,
)
from src.core.router import health_router
from src.users.router import user_router


setup_sync_uncaught_exception_handler()
setup_logging()

app = FastAPI(lifespan=lifespan)
app.include_router(health_router)
app.include_router(user_router)
app.include_router(token_router)

app.add_exception_handler(WithHttpException, with_http_exception_handler)
app.add_middleware(AccessLoggingMiddleware)
app.add_middleware(CorrelationIdMiddleware)

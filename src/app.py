from fastapi import FastAPI

from src.auth.router import token_router
from src.core.domain import start_setup
from src.core.exceptions import (
    WithHttpException,
    with_http_exception_handler,
)
from src.core.lifespan import lifespan
from src.core.router import health_router
from src.users.router import user_router


start_setup()

app = FastAPI(lifespan=lifespan)
app.include_router(health_router)
app.include_router(user_router)
app.include_router(token_router)

app.add_exception_handler(WithHttpException, with_http_exception_handler)

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from src.core.database import (
    redis_manager,
    sql_database_manager,
)
from src.core.exceptions import setup_async_uncaught_exception_handler


if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    setup_async_uncaught_exception_handler()
    await sql_database_manager.init()
    await redis_manager.init()
    yield
    await sql_database_manager.close()
    await redis_manager.close()

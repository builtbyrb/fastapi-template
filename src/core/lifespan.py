from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.database import (
    create_db_and_tables,
    redis_manager,
    session_manager,
)
from src.core.exceptions import setup_async_uncaught_exception_handler


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    setup_async_uncaught_exception_handler()
    await create_db_and_tables()
    await redis_manager.init()
    yield
    await session_manager.close()
    await redis_manager.close()

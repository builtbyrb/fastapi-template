from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.database import (
    create_db_and_tables,
    redis_manager,
    session_manager,
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    await create_db_and_tables()
    await redis_manager.init()
    yield
    await session_manager.close()
    await redis_manager.close()

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database.database import (
    REDIS_MANGER,
    SQL_DATABASE_MANGER,
)
from src.telemetry.logging import (
    setup_logging,
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    await SQL_DATABASE_MANGER.init()
    await REDIS_MANGER.init()
    yield
    await SQL_DATABASE_MANGER.close()
    await REDIS_MANGER.close()

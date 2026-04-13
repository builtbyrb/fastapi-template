from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from src.core.database import (
    REDIS_MANGER,
    SQL_DATABASE_MANGER,
)
from src.core.exceptions import setup_async_uncaught_exception_handler


if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    setup_async_uncaught_exception_handler()
    await SQL_DATABASE_MANGER.init()
    await REDIS_MANGER.init()
    yield
    await SQL_DATABASE_MANGER.close()
    await REDIS_MANGER.close()

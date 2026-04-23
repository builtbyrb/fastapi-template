from collections.abc import AsyncGenerator

import pytest
from sqlalchemy import text

from src.database.database import SQL_DATABASE_MANGER


@pytest.fixture
async def setup_test_table() -> AsyncGenerator:
    await SQL_DATABASE_MANGER.init()

    async with SQL_DATABASE_MANGER.engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS test_items"))
        await conn.execute(
            text("CREATE TABLE test_items (id SERIAL PRIMARY KEY, name TEXT)")
        )

    yield

    async with SQL_DATABASE_MANGER.engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS test_items"))

    await SQL_DATABASE_MANGER.close()

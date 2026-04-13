from collections.abc import AsyncIterator

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import app as actual_app
from src.core.database import sql_database_manager
from src.core.dependencies import get_sql_db_session


@pytest.fixture
def app() -> FastAPI:
    return actual_app


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with (
        LifespanManager(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac,
    ):
        yield ac


@pytest.fixture
async def transactional_sql_session() -> AsyncIterator[AsyncSession]:
    async with sql_database_manager.connect() as connection:
        try:
            async with AsyncSession(
                bind=connection,
                join_transaction_mode="create_savepoint",
            ) as sql_session:
                yield sql_session
        finally:
            await connection.rollback()


@pytest.fixture
async def db_session(
    transactional_sql_session: AsyncSession,
) -> AsyncSession:
    return transactional_sql_session


@pytest.fixture
async def session_override(app: FastAPI, db_session: AsyncSession) -> None:
    app.dependency_overrides[get_sql_db_session] = lambda: db_session

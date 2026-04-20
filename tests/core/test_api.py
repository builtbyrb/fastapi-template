import pytest
from httpx import AsyncClient

from src.core.types.schemas import HealthStatus


@pytest.mark.usefixtures("client", "db_session", "session_override")
@pytest.mark.asyncio
async def test_health_route_return_health_status(client: AsyncClient) -> None:
    response = await client.get("health/")
    assert response.status_code == 200
    assert HealthStatus.model_validate(response.json())


@pytest.mark.usefixtures("client", "db_session", "session_override")
@pytest.mark.asyncio
async def test_health_route_with_invalid_method(client: AsyncClient) -> None:
    response = await client.patch("health/")
    assert response.status_code == 405

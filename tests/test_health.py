import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_simple_request(client: AsyncClient) -> None:
    response = await client.get("health/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_with_bad_method(client: AsyncClient) -> None:
    response = await client.patch("health/")
    assert response.status_code == 405

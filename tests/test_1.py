import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_1(client: AsyncClient):
    json = {
        "first_name": "string",
        "last_name": "string",
        "username": "string",
        "email": "user@example.com",
        "password": "barook74741A@",
    }
    response = await client.post("users/register", json=json)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_2(client: AsyncClient):
    json = {
        "first_name": "string",
        "last_name": "string",
        "username": "string",
        "email": "user@example.com",
        "password": "barook74741A@",
    }
    response = await client.post("users/register", json=json)
    assert response.status_code == 201

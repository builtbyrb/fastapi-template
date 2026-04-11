from typing import Any

import pytest
from httpx import AsyncClient, Response

from tests.users.interfaces import CreateUserRequest


@pytest.fixture
def user_register() -> dict[str, str]:
    return {
        "first_name": "Jeann",
        "last_name": "Brun",
        "username": "jeanbrun_du_76",
        "email": "user@gmail.com",
        "password": "Password123!!",
    }.copy()


@pytest.fixture
def user_register_path() -> str:
    return "users/register"


@pytest.fixture
def create_user_request(
    client: AsyncClient, user_register_path: str
) -> CreateUserRequest:
    async def _create(data: dict[str, Any]) -> Response:
        return await client.post(user_register_path, json=data)

    return _create

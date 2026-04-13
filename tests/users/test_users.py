from typing import TYPE_CHECKING

import pytest

from src.core.exceptions import ExceptionResponse
from src.users.types.internal import UserAlreadyExistsErrorDetails
from src.users.types.schemas import UserOut


if TYPE_CHECKING:
    from httpx import AsyncClient

    from tests.users.interfaces import CreateUserRequest


@pytest.mark.usefixtures("db_session", "session_override")
@pytest.mark.asyncio
async def test_register_with_valid_info(
    create_user_request: CreateUserRequest,
    user_register: dict[str, str],
) -> None:
    response = await create_user_request(user_register)
    assert response.status_code == 201
    assert UserOut.model_validate(response.json())


@pytest.mark.usefixtures("db_session", "session_override")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("field", "invalid_value"),
    [("password", "short"), ("email", "invalid@email"), ("username", "short")],
)
async def test_register_with_invalid_fields(
    create_user_request: CreateUserRequest,
    user_register: dict[str, str],
    field: str,
    invalid_value: str,
) -> None:
    user_register[field] = invalid_value
    response = await create_user_request(user_register)
    assert response.status_code == 422


@pytest.mark.usefixtures("db_session", "session_override")
@pytest.mark.asyncio
async def test_register_with_dupe_email(
    client: AsyncClient, user_register: dict[str, str]
) -> None:
    response = await client.post("users/register", json=user_register)
    assert response.status_code == 201
    assert UserOut.model_validate(response.json())

    response = await client.post("users/register", json=user_register)
    assert response.status_code == 409
    response = ExceptionResponse[UserAlreadyExistsErrorDetails].model_validate(
        response.json()
    )

    assert response.detail.exc_code == "users/already-exists"
    assert response.detail.field == "email"
    assert response.detail.value == user_register["email"]


@pytest.mark.usefixtures("db_session", "session_override")
@pytest.mark.asyncio
async def test_register_with_dupe_username(
    client: AsyncClient, user_register: dict[str, str]
) -> None:
    response = await client.post("users/register", json=user_register)
    assert response.status_code == 201
    assert UserOut.model_validate(response.json())
    user_register["email"] = "user1@example.com"

    response = await client.post("users/register", json=user_register)
    assert response.status_code == 409
    response = ExceptionResponse[UserAlreadyExistsErrorDetails].model_validate(
        response.json()
    )

    assert response.detail.exc_code == "users/already-exists"
    assert response.detail.field == "username"
    assert response.detail.value == user_register["username"]

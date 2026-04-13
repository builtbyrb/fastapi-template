from typing import TYPE_CHECKING

from src.core.constants import (
    CLIENT_IP_NOT_FOUND_EXC_DATA,
    RESOURCE_NOT_INITIALIZED_EXC_DATA,
)
from src.core.exceptions import (
    WithHttpException,
)
from src.core.types.internal import ExceptionResponse, HTTPExceptionData


if TYPE_CHECKING:
    from alembic.environment import Any


class ClientIpNotFound(WithHttpException):
    def __init__(self) -> None:
        super().__init__(
            "Client IP could not be determined", CLIENT_IP_NOT_FOUND_EXC_DATA
        )


class ResourceNotInitialized(WithHttpException):
    def __init__(self, resource_name: str) -> None:
        self.resource_name = resource_name

        super().__init__(
            f"Resource {resource_name} was not initialized",
            RESOURCE_NOT_INITIALIZED_EXC_DATA,
        )


def to_response(
    data: HTTPExceptionData,
) -> dict[int | str, dict[str, Any]]:
    response_dict: dict[str, Any] = {
        "description": data.description,
        "model": ExceptionResponse[data.details_model],
    }

    if data.headers:
        response_dict["headers"] = {
            name: {
                "description": definition.description,
                "schema": {"type": definition.type},
            }
            for name, definition in data.headers.items()
        }

    return {data.status_code: response_dict}

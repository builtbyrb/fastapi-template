from typing import TYPE_CHECKING

from src.core.constants import (
    CLIENT_IP_NOT_FOUND_EXC_DATA,
    RESOURCE_NOT_INITIALIZED_EXC_DATA,
)
from src.core.exceptions import (
    WithHttpException,
)
from src.core.types.internal import (
    ExceptionResponse,
    HTTPExceptionData,
    ResourceNotInitializedDetailsContext,
)


if TYPE_CHECKING:
    from alembic.environment import Any


class ClientIpNotFoundException(WithHttpException):
    def __init__(self) -> None:
        super().__init__(
            message="Client IP could not be determined",
            http_exception_data=CLIENT_IP_NOT_FOUND_EXC_DATA,
        )


class ResourceNotInitializedException(WithHttpException):
    def __init__(self, context: ResourceNotInitializedDetailsContext) -> None:
        super().__init__(
            message=f"Resource {context.resource_name} was not initialized",
            http_exception_data=RESOURCE_NOT_INITIALIZED_EXC_DATA,
            context=context,
        )


def to_response(
    data: HTTPExceptionData,
) -> dict[int | str, dict[str, Any]]:
    response_dict = {
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

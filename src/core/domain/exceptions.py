from src.core.constants import (
    CLIENT_IP_NOT_FOUND_EXC_DATA,
    RESOURCE_NOT_INITIALIZED_EXC_DATA,
)
from src.core.exceptions import (
    WithHttpException,
)


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

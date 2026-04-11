from typing import Any, Protocol

from httpx import Response


class CreateUserRequest(Protocol):
    async def __call__(self, data: dict[str, Any]) -> Response: ...

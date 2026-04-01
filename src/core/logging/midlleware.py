from collections.abc import Awaitable, Callable
from asgi_correlation_id.context import correlation_id

import structlog
from fastapi import Request, Response


async def access_logging(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    structlog.contextvars.clear_contextvars()
    request_id = 

    structlog.contextvars.bind_contextvars()

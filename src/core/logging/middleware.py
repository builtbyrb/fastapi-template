import time
from collections.abc import Awaitable, Callable

import structlog
from asgi_correlation_id.context import correlation_id
from fastapi import Request, Response
from fastapi.datastructures import State
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config.env import APP_ENV
from src.core.domain import get_client_ip


access_logger = structlog.stdlib.get_logger("api.access")


class AccessLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request[State],
        call_next: Callable[[Request[State]], Awaitable[Response]],
    ) -> Response:
        structlog.contextvars.clear_contextvars()
        request_id = correlation_id.get()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()
        response = Response(status_code=500)

        try:
            response = await call_next(request)
        except Exception as exc:
            raise exc from exc
        else:
            return response
        finally:
            elapsed = time.perf_counter() - start_time
            client_host = await get_client_ip(request)

            access_logger.info(
                http={
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "method": request.method,
                    "request_id": request_id,
                    "version": request.scope["http_version"],
                },
                network={
                    "client": {"ip": client_host, "port": APP_ENV.ENTRYPOINT_PORT}
                },
                duration=elapsed,
            )

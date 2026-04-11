import time
from collections.abc import Awaitable, Callable

import structlog
from asgi_correlation_id.context import correlation_id
from fastapi import Request, Response
from fastapi.datastructures import State
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.dependencies import get_client_ip
from src.core.settings import APP_ENV_SETTINGS


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
            client_host = await get_client_ip(request)
            client_port = APP_ENV_SETTINGS.ENTRYPOINT_PORT
            http_method = request.method
            url = str(request.url)
            http_version = request.scope["http_version"]
            status_code = response.status_code
            elapsed = time.perf_counter() - start_time

            await access_logger.ainfo(
                f"{client_host}:{client_port} - "
                f"{http_method} {url} HTTP/{http_version} "
                f"{status_code}",
                http={
                    "url": url,
                    "status_code": status_code,
                    "method": http_method,
                    "request_id": request_id,
                    "version": http_version,
                },
                network={"client": {"ip": client_host, "port": client_port}},
                duration=elapsed,
            )

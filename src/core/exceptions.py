import asyncio
import logging
import sys
from typing import TYPE_CHECKING, Any

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from src.core.types.internal import (
    ExceptionResponse,
    HTTPExceptionData,
)


if TYPE_CHECKING:
    from collections.abc import Mapping
    from types import TracebackType


# region -------------------------- BaseClass -------------------------
class AppException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class WithHttpException(AppException):
    def __init__(
        self,
        message: str,
        http_exception_data: HTTPExceptionData,
    ) -> None:
        self.http_exception_data = http_exception_data
        self.details = self.http_exception_data.details_model(
            exc_code=self.http_exception_data.exc_code,
            message=message,
            **self.__dict__,
        )
        super().__init__(self.message)

    @property
    def headers_dict(
        self,
    ) -> dict[str, str] | None:
        headers = self.http_exception_data.headers
        if not headers:
            return None

        headers_dict: dict[str, str] = {}
        for name, definition in headers.items():
            if definition.value:
                headers_dict[name] = definition.value

        if not headers:
            return None

        return headers_dict

    def build_http_exception(
        self,
        status_code: int | None = None,
        payload: dict[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> HTTPException:
        status_code = status_code or self.http_exception_data.status_code
        payload = payload or ExceptionResponse[
            self.http_exception_data.details_model
        ](detail=self.details).model_dump(mode="json")
        headers = headers or self.headers_dict

        return HTTPException(
            status_code=self.http_exception_data.status_code,
            detail=payload,
            headers=headers,
        )


# endregion


# region -------------------------- Infra -------------------------
async def with_http_exception_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    if not isinstance(exc, WithHttpException):
        raise exc

    http_exception = exc.build_http_exception()

    return JSONResponse(
        status_code=http_exception.status_code,
        content={"detail": http_exception.detail},
        headers=http_exception.headers,
    )


def handle_uncaught_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType | None,
) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.getLogger("system.uncaught").critical(
        "Sync uncaught exception",
        extra={"type": "sync_uncaught_exception"},
        exc_info=(exc_type, exc_value, exc_traceback),
    )


def handle_async_uncaught_exception(
    _loop: asyncio.AbstractEventLoop, context: dict
) -> None:
    message = context["message"]
    exception = context.get("exception")

    logging.getLogger("system.async.uncaught").critical(
        "Async uncaught exception",
        extra={"type": "async_uncaught_exception", "async_msg": message},
        exc_info=exception,
    )


def setup_sync_uncaught_exception_handler() -> None:
    sys.excepthook = handle_uncaught_exception


def setup_async_uncaught_exception_handler() -> None:
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_async_uncaught_exception)


# endregion

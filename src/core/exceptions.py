import asyncio
import logging
import sys
from collections.abc import Mapping
from types import TracebackType
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.core.types.alias import OpenApiSchemaType


# region -------------------------- BaseClass -------------------------
class AppException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class BaseExceptionDetails(BaseModel):
    exc_code: str
    message: str


class ExceptionResponse[T: BaseExceptionDetails](BaseModel):
    detail: T


class HTTPExceptionHeaderDefinition(BaseModel):
    description: str
    type: OpenApiSchemaType
    value: str | None = None


class HTTPExceptionDefinition(BaseModel):
    exc_code: str
    description: str
    status_code: int
    headers: dict[str, HTTPExceptionHeaderDefinition] | None = None
    details_model: type[BaseExceptionDetails] = BaseExceptionDetails

    @property
    def headers_dict(self) -> dict[str, str] | None:
        if not self.headers:
            return None

        headers_dict: dict[str, str] = {}
        for name, definition in self.headers.items():
            if definition.value:
                headers_dict[name] = definition.value

        if not headers_dict:
            return None

        return headers_dict

    @property
    def response(self) -> dict[int | str, dict[str, Any]]:
        response_dict: dict[str, Any] = {
            "description": self.description,
            "model": ExceptionResponse[self.details_model],
        }

        if self.headers:
            response_dict["headers"] = {
                name: {
                    "description": definition.description,
                    "schema": {"type": definition.type},
                }
                for name, definition in self.headers.items()
            }

        return {self.status_code: response_dict}


class WithHttpException(AppException):
    def __init__(
        self, message: str, http_definition: HTTPExceptionDefinition
    ) -> None:
        self.message = message
        self.http_definition = http_definition
        self.exc_code = http_definition.exc_code
        super().__init__(self.message)

    def build_http_exception(
        self,
        status_code: int | None = None,
        payload: dict[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> HTTPException:
        status_code = status_code or self.http_definition.status_code
        payload = payload or self.http_definition.details_model(
            **self.__dict__
        ).model_dump(mode="json")
        headers = headers or self.http_definition.headers_dict

        return HTTPException(
            status_code=self.http_definition.status_code,
            detail=payload,
            headers=headers,
        )


# endregion

# region -------------------------- Business -------------------------
CLIENT_IP_NOT_FOUND = HTTPExceptionDefinition(
    exc_code="ip-not-found",
    status_code=status.HTTP_404_NOT_FOUND,
    description="Client ip not found",
)


class AppClientIpNotFound(WithHttpException):
    def __init__(self) -> None:
        self.message = "Client IP could not be determined"
        super().__init__(self.message, CLIENT_IP_NOT_FOUND)


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

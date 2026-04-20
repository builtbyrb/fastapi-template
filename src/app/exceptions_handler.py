from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, NotRequired, Protocol, TypedDict

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.shared.exceptions import AppException
from src.shared.security import ExpiredTokenException, InvalidTokenException
from src.shared.web import (
    ClientIpNotFoundException,
    OpenApiResponse,
)
from src.users.current_user import UserDisabledException
from src.users.features.login_user import (
    USER_INCORRECT_CREDENTIALS_OPENAPI_RESPONSE,
    UserIncorrectCredentialsException,
)
from src.users.features.refresh_user_token import (
    USER_REFRESH_TOKEN_NOT_FOUND_OPENAPI_RESPONSE,
)
from src.users.responses import (
    EXPIRED_TOKEN_OPENAPI_RESPONSE,
    INVALID_TOKEN_OPENAPI_RESPONSE,
    TOKEN_HEADER_RESPONSE,
    USER_ALREADY_EXISTS_OPENAPI_RESPONSE,
    USER_DISABLED_OPENAPI_RESPONSE,
    USER_NOT_FOUND_OPENAPI_RESPONSE,
)
from src.users.storage import UserNotFoundException
from src.users.subdomains.access_token.settings import ACCESS_TOKEN_ENV_SETTINGS
from src.users.subdomains.refresh_token.storage import RefreshTokenNotFoundException
from src.users.unique import UserAlreadyExistsException


class HTTPExceptionResponseData(BaseModel):
    exc_code: str
    openapi_response: OpenApiResponse


EXPIRED_TOKEN_RESPONSE = HTTPExceptionResponseData(
    exc_code="security/expired-token",
    openapi_response=EXPIRED_TOKEN_OPENAPI_RESPONSE,
)

INVALID_TOKEN_RESPONSE = HTTPExceptionResponseData(
    exc_code="security/invalid-token",
    openapi_response=INVALID_TOKEN_OPENAPI_RESPONSE,
)

CLIENT_IP_NOT_FOUND_RESPONSE = HTTPExceptionResponseData(
    exc_code="web/ip-not-found",
    openapi_response=INVALID_TOKEN_OPENAPI_RESPONSE,
)

USER_DISABLED_RESPONSE = HTTPExceptionResponseData(
    exc_code="users/user-disabled", openapi_response=USER_DISABLED_OPENAPI_RESPONSE
)

USER_NOT_FOUND_RESPONSE = HTTPExceptionResponseData(
    exc_code="users/user-not-found", openapi_response=USER_NOT_FOUND_OPENAPI_RESPONSE
)


USER_ALREADY_EXISTS_RESPONSE = HTTPExceptionResponseData(
    exc_code="users/already-exists",
    openapi_response=USER_ALREADY_EXISTS_OPENAPI_RESPONSE,
)

USER_INCORRECT_CREDENTIALS_RESPONSE = HTTPExceptionResponseData(
    exc_code="users/incorrect-credentials",
    openapi_response=USER_INCORRECT_CREDENTIALS_OPENAPI_RESPONSE,
)

REFRESH_TOKEN_NOT_FOUND_RESPONSE = HTTPExceptionResponseData(
    exc_code="users/refresh-token-not-found",
    openapi_response=USER_REFRESH_TOKEN_NOT_FOUND_OPENAPI_RESPONSE,
)


class HTTPExceptionDetailDict(TypedDict):
    exc_code: str
    message: str
    context: NotRequired[dict[str, Any]]


@dataclass(kw_only=True, frozen=True)
class BuildDetailsParams:
    exc_code: str
    message: str
    context: BaseModel | None = None


def build_detail(params: BuildDetailsParams) -> HTTPExceptionDetailDict:
    context = (
        params.context.model_dump(mode="json") if params.context else params.context
    )
    detail: HTTPExceptionDetailDict = {
        "exc_code": params.exc_code,
        "message": params.message,
    }

    if context:
        detail["context"] = context

    return detail


def build_http_exception(
    exc: AppException,
    http_exception_data: HTTPExceptionResponseData,
) -> HTTPException:
    detail = build_detail(
        BuildDetailsParams(
            exc_code=http_exception_data.exc_code,
            message=exc.message,
            context=exc.context,
        )
    )

    return HTTPException(
        status_code=http_exception_data.openapi_response.status_code,
        detail=detail,
    )


type TokenHeaderException = ExpiredTokenException | InvalidTokenException


def build_http_exception_token_header(
    exc: TokenHeaderException, http_exception_data: HTTPExceptionResponseData
) -> HTTPException:
    http_exception = build_http_exception(exc, http_exception_data)

    http_exception.headers = {
        TOKEN_HEADER_RESPONSE.name: ACCESS_TOKEN_ENV_SETTINGS.ACCESS_TOKEN_TYPE
    }

    return http_exception


class HTTPExceptionBuilderFn(Protocol):
    def __call__(
        self,
        *args: Any,
        **kwds: Any,
    ) -> HTTPException: ...


type ApiExceptionMapping = Mapping[type[Exception], HTTPExceptionBuilderFn]

API_EXCEPTION_MAPPING: ApiExceptionMapping = {
    ExpiredTokenException: (
        lambda exc: build_http_exception_token_header(exc, EXPIRED_TOKEN_RESPONSE)
    ),
    InvalidTokenException: (
        lambda exc: build_http_exception_token_header(exc, INVALID_TOKEN_RESPONSE)
    ),
    ClientIpNotFoundException: (
        lambda exc: build_http_exception(exc, CLIENT_IP_NOT_FOUND_RESPONSE)
    ),
    UserDisabledException: (
        lambda exc: build_http_exception(exc, USER_DISABLED_RESPONSE)
    ),
    UserNotFoundException: (
        lambda exc: build_http_exception(exc, USER_NOT_FOUND_RESPONSE)
    ),
    UserAlreadyExistsException: (
        lambda exc: build_http_exception(exc, USER_ALREADY_EXISTS_RESPONSE)
    ),
    UserIncorrectCredentialsException: (
        lambda exc: build_http_exception(exc, USER_INCORRECT_CREDENTIALS_RESPONSE)
    ),
    RefreshTokenNotFoundException: (
        lambda exc: build_http_exception(exc, REFRESH_TOKEN_NOT_FOUND_RESPONSE)
    ),
}


async def app_http_exception_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    exc_type = type(exc)
    handler = API_EXCEPTION_MAPPING[exc_type]

    if not handler:
        raise exc

    http_exception = handler(exc)

    return JSONResponse(
        status_code=http_exception.status_code,
        content=http_exception.detail,
        headers=http_exception.headers,
    )

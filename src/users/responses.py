from fastapi import status

from src.shared.web import (
    ExceptionResponse,
    ExceptionResponseWithContext,
    OpenApiHeaderResponse,
    OpenApiResponse,
)
from src.users.exceptions import UserExceptionContext
from src.users.unique import UserAlreadyExistsExceptionContext


class UserDisabledExceptionResponse(ExceptionResponseWithContext):
    context: UserExceptionContext


USER_DISABLED_OPENAPI_RESPONSE = OpenApiResponse(
    status_code=status.HTTP_401_UNAUTHORIZED,
    description="Inactive user",
    response_model=UserDisabledExceptionResponse,
)


class UserNotFoundExceptionResponse(ExceptionResponseWithContext):
    context: UserExceptionContext


USER_NOT_FOUND_OPENAPI_RESPONSE = OpenApiResponse(
    status_code=status.HTTP_404_NOT_FOUND,
    description="User not found",
    response_model=UserNotFoundExceptionResponse,
)

TOKEN_HEADER_RESPONSE = OpenApiHeaderResponse(
    name="WWW-Authenticate",
    description='Authentication scheme required (e.g., "Bearer")',
)

EXPIRED_TOKEN_OPENAPI_RESPONSE = OpenApiResponse(
    status_code=status.HTTP_401_UNAUTHORIZED,
    description="Expired token",
    headers=[TOKEN_HEADER_RESPONSE],
    response_model=ExceptionResponse,
)

INVALID_TOKEN_OPENAPI_RESPONSE = OpenApiResponse(
    status_code=status.HTTP_401_UNAUTHORIZED,
    description="Invalid token",
    headers=[TOKEN_HEADER_RESPONSE],
    response_model=ExceptionResponse,
)


CURRENT_ACTIVE_USER_RESPONSE = {
    **INVALID_TOKEN_OPENAPI_RESPONSE.openapi_response,
    **EXPIRED_TOKEN_OPENAPI_RESPONSE.openapi_response,
    **USER_DISABLED_OPENAPI_RESPONSE.openapi_response,
    **USER_NOT_FOUND_OPENAPI_RESPONSE.openapi_response,
}


class UserAlreadyExistsExceptionResponse(ExceptionResponseWithContext):
    context: UserAlreadyExistsExceptionContext


USER_ALREADY_EXISTS_OPENAPI_RESPONSE = OpenApiResponse(
    status_code=status.HTTP_409_CONFLICT,
    description="User already exists",
    response_model=UserAlreadyExistsExceptionResponse,
)

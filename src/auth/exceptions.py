from typing import TYPE_CHECKING

from fastapi import status

from src.auth.config.env import AUTH_ENV
from src.core.exceptions import (
    HTTPExceptionDefinition,
    HTTPExceptionHeaderDefinition,
    WithHttpException,
)
from src.users.exceptions import UserExceptionDetails


if TYPE_CHECKING:
    from src.core.types.interfaces import Identifiable


INVALID_TOKEN_DEF = HTTPExceptionDefinition(
    exc_code="auth/invalid-token",
    status_code=status.HTTP_401_UNAUTHORIZED,
    description="Invalid token",
    headers={
        "WWW-Authenticate": HTTPExceptionHeaderDefinition(
            value=AUTH_ENV.ACCESS_TOKEN_TYPE,
            description='Authentication scheme required (e.g., "Bearer")',
            type="string",
        )
    },
)

INCORRECT_CREDENTIALS_DEF = HTTPExceptionDefinition(
    exc_code="auth/incorrect-cred",
    status_code=status.HTTP_401_UNAUTHORIZED,
    description="Incorrect username or password",
    headers={
        "WWW-Authenticate": HTTPExceptionHeaderDefinition(
            value=AUTH_ENV.ACCESS_TOKEN_TYPE,
            description='Authentication scheme required (e.g., "Bearer")',
            type="string",
        )
    },
)

USER_DISABLED_DEF = HTTPExceptionDefinition(
    exc_code="auth/user-disabled",
    status_code=status.HTTP_400_BAD_REQUEST,
    description="Inactive user",
    details_model=UserExceptionDetails,
)


class AuthException(WithHttpException):
    pass


class AuthInvalidTokenException(AuthException):
    def __init__(self) -> None:
        self.message = "Could not validate credentials"
        super().__init__(self.message, INVALID_TOKEN_DEF)


class AuthIncorrectCredentialsException(AuthException):
    def __init__(self) -> None:
        self.message = INCORRECT_CREDENTIALS_DEF.description
        super().__init__(self.message, INCORRECT_CREDENTIALS_DEF)


class AuthUserDisabledException(AuthException):
    def __init__(self, user: Identifiable) -> None:
        self.user = user.identifier
        self.message = f"User {self.user} is inactive"
        super().__init__(self.message, USER_DISABLED_DEF)

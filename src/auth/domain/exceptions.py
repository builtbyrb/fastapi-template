from typing import TYPE_CHECKING

from src.auth.constants import (
    INCORRECT_CREDENTIALS_DATA,
    INVALID_TOKEN_EXC_DATA,
    USER_DISABLED_DATA,
)
from src.core.exceptions import WithHttpException


if TYPE_CHECKING:
    from src.users.types.internal import UserExceptionDetailsContext


class AuthException(WithHttpException):
    pass


class AuthInvalidTokenException(AuthException):
    def __init__(self) -> None:
        super().__init__(
            message="Could not validate credentials",
            http_exception_data=INVALID_TOKEN_EXC_DATA,
        )


class AuthIncorrectCredentialsException(AuthException):
    def __init__(self) -> None:
        super().__init__(
            message="Invalid email/username or password",
            http_exception_data=INCORRECT_CREDENTIALS_DATA,
        )


class AuthUserDisabledException(AuthException):
    def __init__(self, context: UserExceptionDetailsContext) -> None:
        super().__init__(
            message=f"User {context.user} is inactive",
            http_exception_data=USER_DISABLED_DATA,
            context=context,
        )

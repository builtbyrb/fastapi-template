from src.auth.constants import (
    INCORRECT_CREDENTIALS_DATA,
    INVALID_TOKEN_EXC_DATA,
    USER_DISABLED_DATA,
)
from src.core.exceptions import WithHttpException


class AuthException(WithHttpException):
    pass


class AuthInvalidTokenException(AuthException):
    def __init__(self) -> None:
        self.message = "Could not validate credentials"
        super().__init__(self.message, INVALID_TOKEN_EXC_DATA)


class AuthIncorrectCredentialsException(AuthException):
    def __init__(self) -> None:
        self.message = INCORRECT_CREDENTIALS_DATA.description
        super().__init__(self.message, INCORRECT_CREDENTIALS_DATA)


class AuthUserDisabledException(AuthException):
    def __init__(self, user: str) -> None:
        self.user = user

        super().__init__(f"User {self.user} is inactive", USER_DISABLED_DATA)

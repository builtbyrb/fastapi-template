from src.core.exceptions import (
    WithHttpException,
)
from src.users.constants import (
    USER_ALREADY_EXISTS_EXC_DATA,
    USER_NOT_FOUND_EXC_DATA,
    USER_TOO_MANY_REFRESH_TOKEN_EXC_DATA,
)


class UserException(WithHttpException):
    pass


class UserAlreadyExistsException(UserException):
    def __init__(self, user: str, field: str, value: str) -> None:
        self.user = user
        self.field = field
        self.value = value
        super().__init__(
            f"User {value} already exists",
            USER_ALREADY_EXISTS_EXC_DATA,
        )


class UserNotFoundException(UserException):
    def __init__(self, user: str) -> None:
        self.user = user

        super().__init__(
            f"User {user} not found",
            USER_NOT_FOUND_EXC_DATA,
        )


class UserTooManyRefreshTokenException(UserException):
    def __init__(self, user: str) -> None:
        self.user = user

        super().__init__(
            f"User {user} got too many refresh token",
            USER_TOO_MANY_REFRESH_TOKEN_EXC_DATA,
        )

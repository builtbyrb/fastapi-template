from fastapi import status

from src.core.exceptions import (
    BaseExceptionDetails,
    HTTPExceptionDefinition,
    WithHttpException,
)
from src.core.interfaces import Identifiable


class UserExceptionDetails(BaseExceptionDetails):
    user: str


class UserAlreadyExistsErrorDetails(UserExceptionDetails):
    field: str
    value: str


USER_ALREADY_EXISTS_DEF = HTTPExceptionDefinition(
    exc_code="users/already-exists",
    status_code=status.HTTP_409_CONFLICT,
    description="User already exists",
    details_model=UserAlreadyExistsErrorDetails,
)

USER_NOT_FOUND_DEF = HTTPExceptionDefinition(
    exc_code="users/not-found",
    status_code=status.HTTP_404_NOT_FOUND,
    description="User not found",
    details_model=UserExceptionDetails,
)

USER_TOO_MANY_REFRESH_TOKEN_DEF = HTTPExceptionDefinition(
    exc_code="users/too-many-token",
    status_code=status.HTTP_400_BAD_REQUEST,
    description="Too much refresh token",
    details_model=UserExceptionDetails,
)


class UserException(WithHttpException):
    pass


class UserAlreadyExistsException(UserException):
    def __init__(self, user: Identifiable, field: str, value: str) -> None:
        self.user = user.identifier
        self.field = field
        self.value = value
        super().__init__(
            f"User {self.value} already exists", USER_ALREADY_EXISTS_DEF
        )


class UserNotFoundException(UserException):
    def __init__(self, user: Identifiable) -> None:
        self.user = user.identifier
        self.message = f"User {user.identifier} not found"
        super().__init__(self.message, USER_NOT_FOUND_DEF)


class UserTooManyRefreshTokenException(UserException):
    def __init__(self, user: Identifiable) -> None:
        self.user = user.identifier
        self.message = f"User {user.identifier} got too many refresh token"

        super().__init__(self.message, USER_TOO_MANY_REFRESH_TOKEN_DEF)

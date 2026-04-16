from typing import TYPE_CHECKING

from src.core.exceptions import (
    WithHttpException,
)
from src.users.constants import (
    USER_ALREADY_EXISTS_EXC_DATA,
    USER_NOT_FOUND_EXC_DATA,
    USER_TOO_MANY_REFRESH_TOKEN_EXC_DATA,
)


if TYPE_CHECKING:
    from src.users.types.internal import (
        UserAlreadyExistsExceptionDetailsContext,
        UserExceptionDetailsContext,
    )


class UserException(WithHttpException):
    pass


class UserAlreadyExistsException(UserException):
    def __init__(self, context: UserAlreadyExistsExceptionDetailsContext) -> None:
        super().__init__(
            message=f"User {context.value} already exists",
            http_exception_data=USER_ALREADY_EXISTS_EXC_DATA,
            context=context,
        )


class UserNotFoundException(UserException):
    def __init__(self, context: UserExceptionDetailsContext) -> None:
        super().__init__(
            message=f"User {context.user} not found",
            http_exception_data=USER_NOT_FOUND_EXC_DATA,
            context=context,
        )


class UserTooManyRefreshTokenException(UserException):
    def __init__(self, context: UserExceptionDetailsContext) -> None:
        super().__init__(
            message=f"User {context.user} got too many refresh token",
            http_exception_data=USER_TOO_MANY_REFRESH_TOKEN_EXC_DATA,
        )

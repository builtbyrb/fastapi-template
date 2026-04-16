from typing import TYPE_CHECKING

from src.core.exceptions import (
    WithHttpException,
)
from src.refresh_token.constants import REFRESH_TOKEN_NOT_FOUND_EXC_DATA


if TYPE_CHECKING:
    from src.refresh_token.types.internal import RefreshTokenExceptionDetailsContext


class RefreshTokenException(WithHttpException):
    pass


class RefreshTokenNotFoundException(RefreshTokenException):
    def __init__(self, context: RefreshTokenExceptionDetailsContext) -> None:
        super().__init__(
            message=f"Refresh Token {context.refresh_token} not found",
            http_exception_data=REFRESH_TOKEN_NOT_FOUND_EXC_DATA,
            context=context,
        )

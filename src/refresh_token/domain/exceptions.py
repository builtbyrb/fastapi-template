from src.core.exceptions import (
    WithHttpException,
)
from src.refresh_token.constants import REFRESH_TOKEN_NOT_FOUND_EXC_DATA


class RefreshTokenException(WithHttpException):
    pass


class RefreshTokenNotFoundException(RefreshTokenException):
    def __init__(self, refresh_token: str) -> None:
        self.refresh_token = refresh_token

        super().__init__(
            f"Refresh Token {refresh_token} not found",
            REFRESH_TOKEN_NOT_FOUND_EXC_DATA,
        )

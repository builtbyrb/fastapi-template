from fastapi import status

from src.core.exceptions import (
    BaseExceptionDetails,
    HTTPExceptionDefinition,
    WithHttpException,
)
from src.core.interfaces import Identifiable


class RefreshTokenExceptionDetails(BaseExceptionDetails):
    refresh_token: str


REFRESH_TOKEN_NOT_FOUND = HTTPExceptionDefinition(
    exc_code="auth/not-found",
    status_code=status.HTTP_404_NOT_FOUND,
    description="Refresh token not found",
    details_model=RefreshTokenExceptionDetails,
)


class RefreshTokenException(WithHttpException):
    pass


class RefreshTokenNotFoundException(RefreshTokenException):
    def __init__(self, refresh_token: Identifiable) -> None:
        self.refresh_token = refresh_token.identifier
        self.message = f"Refresh Token {self.refresh_token} not found"
        super().__init__(self.message, REFRESH_TOKEN_NOT_FOUND)

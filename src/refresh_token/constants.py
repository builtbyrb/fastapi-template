from fastapi import status

from src.core.types.internal import HTTPExceptionData
from src.refresh_token.types.internal import RefreshTokenExceptionDetailsContext


REFRESH_TOKEN_NOT_FOUND_EXC_DATA = HTTPExceptionData(
    exc_code="auth/not-found",
    status_code=status.HTTP_404_NOT_FOUND,
    description="Refresh token not found",
    context_model=RefreshTokenExceptionDetailsContext,
)

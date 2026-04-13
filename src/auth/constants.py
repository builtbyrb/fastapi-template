from fastapi import status

from src.auth.domain.security import password_hash
from src.auth.settings import AUTH_ENV_SETTINGS
from src.core.domain.domain import to_response
from src.core.types.internal import HTTPExceptionData, HTTPExceptionHeaderData
from src.users.constants import USER_NOT_FOUND_EXC_DATA
from src.users.types.internal import UserExceptionDetails


DUMMY_HASH = password_hash.hash("dummyPassword")

INVALID_TOKEN_EXC_DATA = HTTPExceptionData(
    exc_code="auth/invalid-token",
    status_code=status.HTTP_401_UNAUTHORIZED,
    description="Invalid token",
    headers={
        "WWW-Authenticate": HTTPExceptionHeaderData(
            value=AUTH_ENV_SETTINGS.ACCESS_TOKEN_TYPE,
            description='Authentication scheme required (e.g., "Bearer")',
            type="string",
        )
    },
)

INCORRECT_CREDENTIALS_DATA = HTTPExceptionData(
    exc_code="auth/incorrect-cred",
    status_code=status.HTTP_401_UNAUTHORIZED,
    description="Incorrect username or password",
    headers={
        "WWW-Authenticate": HTTPExceptionHeaderData(
            value=AUTH_ENV_SETTINGS.ACCESS_TOKEN_TYPE,
            description='Authentication scheme required (e.g., "Bearer")',
            type="string",
        )
    },
)

USER_DISABLED_DATA = HTTPExceptionData(
    exc_code="auth/user-disabled",
    status_code=status.HTTP_400_BAD_REQUEST,
    description="Inactive user",
    details_model=UserExceptionDetails,
)


AUTH_CURRENT_USER_RESPONSE = {
    **to_response(INVALID_TOKEN_EXC_DATA),
    **to_response(USER_DISABLED_DATA),
    **to_response(USER_NOT_FOUND_EXC_DATA),
}

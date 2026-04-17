from pydantic import BaseModel

from src.auth.constants import (
    INCORRECT_CREDENTIALS_DATA,
    INVALID_TOKEN_EXC_DATA,
    USER_DISABLED_DATA,
)
from src.core.types.internal import HTTPExceptionData


class AppExceptionsExport(BaseModel):
    INVALID_TOKEN: HTTPExceptionData = INVALID_TOKEN_EXC_DATA
    INCORRECT_CREDENTIALS: HTTPExceptionData = INCORRECT_CREDENTIALS_DATA
    USER_DISABLED: HTTPExceptionData = USER_DISABLED_DATA


AUTH_EXCEPTIONS = AppExceptionsExport()

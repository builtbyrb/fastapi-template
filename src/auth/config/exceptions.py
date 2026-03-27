from pydantic import BaseModel

from src.auth.exceptions import (
    INCORRECT_CREDENTIALS_DEF,
    INVALID_TOKEN_DEF,
    USER_DISABLED_DEF,
)
from src.core.exceptions import HTTPExceptionDefinition
from src.users.exceptions import USER_NOT_FOUND_DEF


class AuthConfigErrors(BaseModel):
    INVALID_TOKEN: HTTPExceptionDefinition = INVALID_TOKEN_DEF

    INCORRECT_CREDENTIALS: HTTPExceptionDefinition = INCORRECT_CREDENTIALS_DEF

    USER_DISABLED: HTTPExceptionDefinition = USER_DISABLED_DEF


AUTH_ERRORS = AuthConfigErrors()

AUTH_CURRENT_USER_RESPONSE = {
    **INVALID_TOKEN_DEF.response,
    **USER_DISABLED_DEF.response,
    **USER_NOT_FOUND_DEF.response,
}

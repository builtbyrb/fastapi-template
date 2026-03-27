from pydantic import BaseModel

from src.core.exceptions import HTTPExceptionDefinition
from src.users.exceptions import USER_ALREADY_EXISTS_DEF, USER_NOT_FOUND_DEF


class UserErrors(BaseModel):
    USER_ALREADY_EXISTS: HTTPExceptionDefinition = USER_ALREADY_EXISTS_DEF

    USER_NOT_FOUND: HTTPExceptionDefinition = USER_NOT_FOUND_DEF


USER_ERRORS = UserErrors()

from typing import Any

from pydantic import BaseModel

from src.core.domain.utils import enum_do_dict
from src.core.types.internal import HTTPExceptionData, LengthRuleData
from src.users.constants import (
    USER_ALREADY_EXISTS_EXC_DATA,
    USER_EMAIL_LENGTH_RULE_DATA,
    USER_FIRST_NAME_LENGTH_RULE_DATA,
    USER_LAST_NAME_LENGTH_RULE_DATA,
    USER_NOT_FOUND_EXC_DATA,
    USER_PASSWORD_LENGTH_RULE_DATA,
    USER_USERNAME_LENGTH_RULE_DATA,
)
from src.users.types.alias import UserRole


# region -------------------------- Exceptions -------------------------
class UserExceptionsExport(BaseModel):
    USER_ALREADY_EXISTS: HTTPExceptionData = USER_ALREADY_EXISTS_EXC_DATA
    USER_NOT_FOUND: HTTPExceptionData = USER_NOT_FOUND_EXC_DATA


USER_EXCEPTIONS_EXPORT = UserExceptionsExport()
# endregion


# region -------------------------- Constants -------------------------
class UserLengthConstantsExport(BaseModel):
    FIRST_NAME: LengthRuleData = USER_FIRST_NAME_LENGTH_RULE_DATA
    LAST_NAME: LengthRuleData = USER_LAST_NAME_LENGTH_RULE_DATA
    EMAIL: LengthRuleData = USER_EMAIL_LENGTH_RULE_DATA
    USERNAME: LengthRuleData = USER_USERNAME_LENGTH_RULE_DATA
    PASSWORD: LengthRuleData = USER_PASSWORD_LENGTH_RULE_DATA


USER_LENGTH_CONSTANTS_EXPORT = UserLengthConstantsExport()


class UserConstantsExport(BaseModel):
    LENGTH: UserLengthConstantsExport = USER_LENGTH_CONSTANTS_EXPORT
    USER_ROLE: dict[str, Any] = enum_do_dict(UserRole)


USER_CONSTANTS_EXPORT = UserConstantsExport()
# endregion


class UserExport(BaseModel):
    constants: UserConstantsExport = USER_CONSTANTS_EXPORT
    exceptions: UserExceptionsExport = USER_EXCEPTIONS_EXPORT


USER_EXPORT = UserExport()

from typing import Any

from pydantic import BaseModel

from src.core.domain import enum_do_dict
from src.core.exceptions import HTTPExceptionDefinition
from src.core.types.internal import LengthRuleData
from src.users.constants import (
    USER_EMAIL_LENGTH_RULE_DATA,
    USER_FIRST_NAME_LENGTH_RULE_DATA,
    USER_LAST_NAME_LENGTH_RULE_DATA,
    USER_PASSWORD_LENGTH_RULE_DATA,
    USER_USERNAME_LENGTH_RULE_DATA,
    UserRole,
)
from src.users.exceptions import USER_ALREADY_EXISTS_DEF, USER_NOT_FOUND_DEF


# region -------------------------- Exceptions -------------------------
class UserExceptions(BaseModel):
    USER_ALREADY_EXISTS: HTTPExceptionDefinition = USER_ALREADY_EXISTS_DEF

    USER_NOT_FOUND: HTTPExceptionDefinition = USER_NOT_FOUND_DEF


USER_EXCEPTIONS = UserExceptions()
# endregion


# region -------------------------- Constants -------------------------
class UserLengthConstants(BaseModel):
    FIRST_NAME: LengthRuleData = USER_FIRST_NAME_LENGTH_RULE_DATA
    LAST_NAME: LengthRuleData = USER_LAST_NAME_LENGTH_RULE_DATA
    EMAIL: LengthRuleData = USER_EMAIL_LENGTH_RULE_DATA
    USERNAME: LengthRuleData = USER_USERNAME_LENGTH_RULE_DATA
    PASSWORD: LengthRuleData = USER_PASSWORD_LENGTH_RULE_DATA


USER_LENGTH_CONSTANTS = UserLengthConstants()


class UserConstants(BaseModel):
    LENGTH: UserLengthConstants = USER_LENGTH_CONSTANTS
    USER_ROLE: dict[str, Any] = enum_do_dict(UserRole)


USER_CONSTANTS = UserConstants()
# endregion


class UserConfig(BaseModel):
    constants: UserConstants = USER_CONSTANTS
    exceptions: UserExceptions = USER_EXCEPTIONS


USER_CONFIG = UserConfig()

from pydantic import BaseModel

from src.users.config.constants import USER_CONSTANTS, UserConstants
from src.users.config.exceptions import USER_ERRORS, UserErrors
from src.users.config.rules import USER_VALIDATION_RULES, UserValidationsRules


class UserConfig(BaseModel):
    constants: UserConstants = USER_CONSTANTS
    exceptions: UserErrors = USER_ERRORS
    validation_rules: UserValidationsRules = USER_VALIDATION_RULES


USER_CONFIG = UserConfig()

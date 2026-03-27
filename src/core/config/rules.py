from pydantic import BaseModel

from src.core.rules.rules import (
    NO_SPACE_RULE,
    ONE_LOWERCASE_RULE,
    ONE_NUMBER_RULE,
    ONE_SPECIAL_CHAR_RULE,
    ONE_UPPERCASE_RULE,
    USER_AGENT_FORMAT_RULE,
    NoSpaceValidationRule,
    OneLowercaseValidationRule,
    OneNumberValidationRule,
    OneSpecialCharValidationRule,
    OneUppercaseValidationRule,
    UserAgentFormatRule,
)


class AppValidationRules(BaseModel):
    USER_AGENT_FORMAT: UserAgentFormatRule = USER_AGENT_FORMAT_RULE
    NO_SPACE: NoSpaceValidationRule = NO_SPACE_RULE
    ONE_UPPERCASE: OneUppercaseValidationRule = ONE_UPPERCASE_RULE
    ONE_LOWERCASE: OneLowercaseValidationRule = ONE_LOWERCASE_RULE
    ONE_NUMBER: OneNumberValidationRule = ONE_NUMBER_RULE
    ONE_SPECIAL_CHAR: OneSpecialCharValidationRule = ONE_SPECIAL_CHAR_RULE


APP_VALIDATION_RULES = AppValidationRules()

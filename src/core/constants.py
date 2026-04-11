from enum import StrEnum

from src.core.rules import (
    CustomValidationRuleData,
    CustomValidationRuleRegexData,
)


ENV_FILE = (".env.prod", ".env.stag", ".env")


class Environment(StrEnum):
    DEV = "DEV"
    PROD = "PROD"
    STAG = "STAG"


USER_AGENT_FORMAT_RULE_DATA = CustomValidationRuleData(
    ERROR_CODE="invalid_user_agent_format", ERROR_MESSAGE="Invalid User-Agent format"
)

NO_SPACE_RULE_DATA = CustomValidationRuleData(
    ERROR_CODE="no_space", ERROR_MESSAGE="Must not contains space(s)"
)


ONE_UPPERCASE_RULE_DATA = CustomValidationRuleRegexData(
    ERROR_CODE="missing_uppercase",
    ERROR_MESSAGE="Must contains one capital letter",
    REGEX=r"[A-Z]",
)

ONE_LOWERCASE_RULE_DATA = CustomValidationRuleRegexData(
    ERROR_CODE="missing_lowercase",
    ERROR_MESSAGE="Must contains one lowercase letter",
    REGEX=r"[a-z]",
)

ONE_DIGIT_RULE_DATA = CustomValidationRuleRegexData(
    ERROR_CODE="missing_digit",
    ERROR_MESSAGE="Must contains one number",
    REGEX=r"[0-9]",
)

ONE_SPECIAL_CHAR_RULE_DATA = CustomValidationRuleRegexData(
    ERROR_CODE="missing_special_char",
    ERROR_MESSAGE="Must contains one special char",
    REGEX=r"[#?!@$%^&*-]",
)

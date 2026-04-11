from enum import StrEnum

from src.core.rules import CustomValidationRule, CustomValidationRuleRegex
from src.core.types.internal import (
    CustomValidationRuleData,
    CustomValidationRuleRegexData,
)
from src.core.validators import contains_no_space, is_valid_ua


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

USER_AGENT_FORMAT_RULE = CustomValidationRule(
    data=USER_AGENT_FORMAT_RULE_DATA, predicate_fn=is_valid_ua
)
NO_SPACE_RULE = CustomValidationRule(
    data=NO_SPACE_RULE_DATA, predicate_fn=contains_no_space
)

ONE_UPPERCASE_RULE = CustomValidationRuleRegex(data=ONE_UPPERCASE_RULE_DATA)

ONE_LOWERCASE_RULE = CustomValidationRuleRegex(data=ONE_LOWERCASE_RULE_DATA)

ONE_DIGIT_RULE = CustomValidationRuleRegex(data=ONE_DIGIT_RULE_DATA)

ONE_SPECIAL_CHAR_RULE = CustomValidationRuleRegex(data=ONE_SPECIAL_CHAR_RULE_DATA)

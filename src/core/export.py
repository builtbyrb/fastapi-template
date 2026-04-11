from pydantic import BaseModel

from src.core.constants import (
    NO_SPACE_RULE_DATA,
    ONE_DIGIT_RULE_DATA,
    ONE_LOWERCASE_RULE_DATA,
    ONE_SPECIAL_CHAR_RULE_DATA,
    ONE_UPPERCASE_RULE_DATA,
    USER_AGENT_FORMAT_RULE_DATA,
)
from src.core.rules import (
    CustomValidationRuleData,
    CustomValidationRuleRegexData,
)


class AppValidationRulesData(BaseModel):
    USER_AGENT_FORMAT: CustomValidationRuleData = USER_AGENT_FORMAT_RULE_DATA
    NO_SPACE: CustomValidationRuleData = NO_SPACE_RULE_DATA
    ONE_UPPERCASE: CustomValidationRuleRegexData = ONE_UPPERCASE_RULE_DATA
    ONE_LOWERCASE: CustomValidationRuleRegexData = ONE_LOWERCASE_RULE_DATA
    ONE_DIGIT: CustomValidationRuleRegexData = ONE_DIGIT_RULE_DATA
    ONE_SPECIAL_CHAR: CustomValidationRuleRegexData = ONE_SPECIAL_CHAR_RULE_DATA


APP_VALIDATION_RULES_DATA = AppValidationRulesData()


class AppExport(BaseModel):
    validation_rules_data: AppValidationRulesData = APP_VALIDATION_RULES_DATA


APP_EXPORT = AppExport()

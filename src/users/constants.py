from enum import StrEnum

from src.core.rules import CustomValidationRuleData, LengthRuleData


class UserRole(StrEnum):
    USER = "User"
    ADMIN = "Admin"


USER_FIRST_NAME_LENGTH_RULE_DATA = LengthRuleData(MIN_LENGTH=3, MAX_LENGTH=30)

USER_LAST_NAME_LENGTH_RULE_DATA = LengthRuleData(MIN_LENGTH=3, MAX_LENGTH=30)

USER_EMAIL_LENGTH_RULE_DATA = LengthRuleData(MIN_LENGTH=6, MAX_LENGTH=40)

USER_USERNAME_LENGTH_RULE_DATA = LengthRuleData(MIN_LENGTH=6, MAX_LENGTH=25)

USER_PASSWORD_LENGTH_RULE_DATA = LengthRuleData(MIN_LENGTH=8, MAX_LENGTH=40)
USER_PASSWORD_EMAIL_RULE_DATA = CustomValidationRuleData(
    ERROR_CODE="contains_email", ERROR_MESSAGE="Must not contains your email address"
)

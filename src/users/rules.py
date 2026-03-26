from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from src.core.rules.rules import CustomValidationRule, MinMaxRule
from src.core.rules.validators import contains_value


if TYPE_CHECKING:
    from src.users.interfaces import UserNoEmailRulePort


class UserPasswordRuleEmail(CustomValidationRule):
    ERROR_CODE: str = "contains_email"
    ERROR_MESSAGE: str = "Must not contains your email address"

    def validator[T: UserNoEmailRulePort](self, user: T) -> T:
        if contains_value(user.password, user.email):
            raise self.pydantic_custom_exception
        return user


USER_FIRST_NAME_MIN_MAX_RULE = MinMaxRule(MIN_LENGTH=3, MAX_LENGTH=30)

USER_LAST_NAME_MIN_MAX_RULE = MinMaxRule(MIN_LENGTH=3, MAX_LENGTH=30)

USER_EMAIL_MIN_MAX_RULE = MinMaxRule(MIN_LENGTH=6, MAX_LENGTH=40)

USER_USERNAME_MIN_MAX_RULE = MinMaxRule(MIN_LENGTH=6, MAX_LENGTH=25)

USER_PASSWORD_MIN_MAX_RULE = MinMaxRule(MIN_LENGTH=8, MAX_LENGTH=40)
USER_PASSWORD_EMAIL_RULE = UserPasswordRuleEmail()


class UserNoEmailRuleConfig(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"rules": [USER_PASSWORD_EMAIL_RULE.ERROR_CODE]},
    )

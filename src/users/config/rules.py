from pydantic import BaseModel

from src.core.rules.rules import MinMaxRule
from src.users.rules import (
    USER_EMAIL_MIN_MAX_RULE,
    USER_FIRST_NAME_MIN_MAX_RULE,
    USER_LAST_NAME_MIN_MAX_RULE,
    USER_PASSWORD_EMAIL_RULE,
    USER_PASSWORD_MIN_MAX_RULE,
    USER_USERNAME_MIN_MAX_RULE,
    UserPasswordRuleEmail,
)


class UserFirstNameValidationRules(BaseModel):
    MIN_MAX: MinMaxRule = USER_FIRST_NAME_MIN_MAX_RULE


class UserLastNameValidationRules(BaseModel):
    MIN_MAX: MinMaxRule = USER_LAST_NAME_MIN_MAX_RULE


class UserEmailValidationRules(BaseModel):
    MIN_MAX: MinMaxRule = USER_EMAIL_MIN_MAX_RULE


class UserUsernameValidationRules(BaseModel):
    MIN_MAX: MinMaxRule = USER_USERNAME_MIN_MAX_RULE


class UserPasswordValidationRules(BaseModel):
    MIN_MAX: MinMaxRule = USER_PASSWORD_MIN_MAX_RULE
    EMAIL: UserPasswordRuleEmail = USER_PASSWORD_EMAIL_RULE


USER_FIRST_NAME_RULES = UserFirstNameValidationRules()

USER_LAST_NAME_RULES = UserLastNameValidationRules()

USER_EMAIL_RULES = UserEmailValidationRules()

USER_USERNAME_RULES = UserUsernameValidationRules()

USER_PASSWORD_RULES = UserPasswordValidationRules()


class UserValidationsRules(BaseModel):
    FIRST_NAME: UserFirstNameValidationRules = USER_FIRST_NAME_RULES
    LAST_NAME: UserLastNameValidationRules = USER_LAST_NAME_RULES
    EMAIL: UserEmailValidationRules = USER_EMAIL_RULES
    USERNAME: UserUsernameValidationRules = USER_USERNAME_RULES
    PASSWORD: UserPasswordValidationRules = USER_PASSWORD_RULES


USER_VALIDATION_RULES = UserValidationsRules()

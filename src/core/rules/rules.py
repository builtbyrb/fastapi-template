from collections.abc import Callable
from typing import Any, LiteralString, cast

from pydantic import BaseModel
from pydantic_core import PydanticCustomError

from src.core.rules.validators import (
    contains_no_space,
    contains_regex,
    contains_ua,
    make_custom_field_validator,
)


class CustomValidationRule(BaseModel):
    ERROR_CODE: str
    ERROR_MESSAGE: str
    ERROR_CONTEXT: dict[str, Any] | None = None

    @property
    def pydantic_custom_exception(
        self,
    ) -> PydanticCustomError:
        return PydanticCustomError(
            cast("LiteralString", self.ERROR_CODE),
            cast("LiteralString", self.ERROR_MESSAGE),
            self.ERROR_CONTEXT,
        )


class CustomValidationRuleRegex(CustomValidationRule):
    REGEX: str


class MinMaxRule(BaseModel):
    MIN_LENGTH: int
    MAX_LENGTH: int


class UserAgentFormatRule(CustomValidationRule):
    ERROR_CODE: str = "invalid_user_agent_format"
    ERROR_MESSAGE: str = "Invalid User-Agent header"

    @property
    def validator(self) -> Callable[[str], str]:
        return make_custom_field_validator(
            self.pydantic_custom_exception, contains_ua
        )


USER_AGENT_FORMAT_RULE = UserAgentFormatRule()


class NoSpaceValidationRule(CustomValidationRule):
    ERROR_CODE: str = "no_space"
    ERROR_MESSAGE: str = "Must not contains space(s)"

    @property
    def validator(self) -> Callable[[str], str]:
        return make_custom_field_validator(
            self.pydantic_custom_exception, contains_no_space
        )


NO_SPACE_RULE = NoSpaceValidationRule()


class OneUppercaseValidationRule(CustomValidationRuleRegex):
    ERROR_CODE: str = "missing_uppercase"
    ERROR_MESSAGE: str = "Must contains one capital letter"
    REGEX: str = r"[A-Z]"

    @property
    def validator(self) -> Callable[[str], str]:
        return make_custom_field_validator(
            self.pydantic_custom_exception, contains_regex, self.REGEX
        )


ONE_UPPERCASE_RULE = OneUppercaseValidationRule()


class OneLowercaseValidationRule(CustomValidationRuleRegex):
    ERROR_CODE: str = "missing_lowercase"
    ERROR_MESSAGE: str = "Must contains one lowercase letter"
    REGEX: str = r"[a-z]"

    @property
    def validator(self) -> Callable[[str], str]:
        return make_custom_field_validator(
            self.pydantic_custom_exception, contains_regex, self.REGEX
        )


ONE_LOWERCASE_RULE = OneLowercaseValidationRule()


class OneNumberValidationRule(CustomValidationRuleRegex):
    ERROR_CODE: str = "missing_digit"
    ERROR_MESSAGE: str = "Must contains one number"
    REGEX: str = r"[0-9]"

    @property
    def validator(self) -> Callable[[str], str]:
        return make_custom_field_validator(
            self.pydantic_custom_exception, contains_regex, self.REGEX
        )


ONE_NUMBER_RULE = OneNumberValidationRule()


class OneSpecialCharValidationRule(CustomValidationRuleRegex):
    ERROR_CODE: str = "missing_special_char"
    ERROR_MESSAGE: str = "Must contains one special char"
    REGEX: str = r"[#?!@$%^&*-]"

    @property
    def validator(self) -> Callable[[str], str]:
        return make_custom_field_validator(
            self.pydantic_custom_exception, contains_regex, self.REGEX
        )


ONE_SPECIAL_CHAR_RULE = OneSpecialCharValidationRule()

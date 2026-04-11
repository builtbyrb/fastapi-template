from typing import LiteralString, cast

from pydantic_core import PydanticCustomError

from src.core.constants import (
    NO_SPACE_RULE_DATA,
    ONE_DIGIT_RULE_DATA,
    ONE_SPECIAL_CHAR_RULE_DATA,
    ONE_UPPERCASE_RULE_DATA,
    USER_AGENT_FORMAT_RULE_DATA,
)
from src.core.types.interfaces import PredicateFn, ValidatorFn
from src.core.types.internal import (
    CustomValidationRuleData,
    CustomValidationRuleRegexData,
)
from src.core.validators import (
    contains_no_space,
    contains_regex,
    is_valid_ua,
    make_custom_validator,
)


# region -------------------------- BaseClass -------------------------
class CustomValidationRuleBase[TVal, TData: CustomValidationRuleData]:
    def __init__(self, data: TData, predicate_fn: PredicateFn[TVal]) -> None:
        self.data = data
        self.predicate_fn = predicate_fn

    @property
    def pydantic_custom_exception(
        self,
    ) -> PydanticCustomError:
        return PydanticCustomError(
            cast("LiteralString", self.data.ERROR_CODE),
            cast("LiteralString", self.data.ERROR_MESSAGE),
            self.data.ERROR_CONTEXT,
        )

    @property
    def validator(self) -> ValidatorFn:
        return make_custom_validator(
            self.pydantic_custom_exception, self.predicate_fn
        )


# endregion


# region -------------------------- CustomClass -------------------------
class CustomValidationRule[TVal](
    CustomValidationRuleBase[TVal, CustomValidationRuleData]
):
    def __init__(
        self, data: CustomValidationRuleData, predicate_fn: PredicateFn[TVal]
    ) -> None:
        super().__init__(data, predicate_fn)


class CustomValidationRuleRegex(
    CustomValidationRuleBase[str, CustomValidationRuleRegexData]
):
    def __init__(self, data: CustomValidationRuleRegexData) -> None:
        super().__init__(data, lambda val: contains_regex(val, self.data.REGEX))


# endregion

# region -------------------------- Rules -------------------------
USER_AGENT_FORMAT_RULE = CustomValidationRule(
    data=USER_AGENT_FORMAT_RULE_DATA, predicate_fn=is_valid_ua
)
NO_SPACE_RULE = CustomValidationRule(
    data=NO_SPACE_RULE_DATA, predicate_fn=contains_no_space
)

ONE_UPPERCASE_RULE = CustomValidationRuleRegex(data=ONE_UPPERCASE_RULE_DATA)

ONE_LOWERCASE_RULE = CustomValidationRuleRegex(data=ONE_UPPERCASE_RULE_DATA)

ONE_DIGIT_RULE = CustomValidationRuleRegex(data=ONE_DIGIT_RULE_DATA)

ONE_SPECIAL_CHAR_RULE = CustomValidationRuleRegex(data=ONE_SPECIAL_CHAR_RULE_DATA)
# endregion

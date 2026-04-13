from typing import TYPE_CHECKING, LiteralString, cast

from pydantic_core import PydanticCustomError

from src.core.domain.validators import (
    contains_regex,
    make_custom_validator,
)
from src.core.types.internal import (
    CustomValidationRuleData,
    CustomValidationRuleRegexData,
)


if TYPE_CHECKING:
    from src.core.types.interfaces import PredicateFn, ValidatorFn


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
    def validator(self) -> ValidatorFn[TVal]:
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

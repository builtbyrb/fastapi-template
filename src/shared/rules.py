import re
from typing import Any, LiteralString, Protocol, cast

from pydantic import BaseModel
from pydantic_core import PydanticCustomError


class PredicateFn[TVal](Protocol):
    def __call__(self, val: TVal, *args: Any, **kwds: Any) -> bool: ...


class ValidatorFn[TVal](Protocol):
    def __call__(self, val: TVal) -> TVal: ...


def make_custom_validator[TVal](
    pydantic_custom_exception: PydanticCustomError,
    predicate: PredicateFn[TVal],
) -> ValidatorFn[TVal]:
    def validator(val: TVal) -> TVal:
        if not predicate(val):
            raise pydantic_custom_exception
        return val

    return validator


class LengthRuleData(BaseModel):
    MIN_LENGTH: int
    MAX_LENGTH: int


class CustomValidationRuleData(BaseModel):
    EXC_CODE: str
    EXC_MESSAGE: str
    EXC_CONTEXT: dict[str, Any] | None = None


class CustomValidationRuleRegexData(CustomValidationRuleData):
    REGEX: str


class CustomValidationRuleBase[TVal, TData: CustomValidationRuleData]:
    def __init__(self, data: TData, predicate_fn: PredicateFn[TVal]) -> None:
        self.data = data
        self.predicate_fn = predicate_fn

    @property
    def pydantic_custom_exception(
        self,
    ) -> PydanticCustomError:
        return PydanticCustomError(
            cast(LiteralString, self.data.EXC_CODE),
            cast(LiteralString, self.data.EXC_MESSAGE),
            self.data.EXC_CONTEXT,
        )

    @property
    def validator(self) -> ValidatorFn[TVal]:
        return make_custom_validator(
            self.pydantic_custom_exception, self.predicate_fn
        )


class CustomValidationRule[TVal](
    CustomValidationRuleBase[TVal, CustomValidationRuleData]
):
    def __init__(
        self, data: CustomValidationRuleData, predicate_fn: PredicateFn[TVal]
    ) -> None:
        super().__init__(data, predicate_fn)


def contains_regex(val: str, regex: str) -> bool:
    return bool(re.search(regex, val))


class CustomValidationRuleRegex(
    CustomValidationRuleBase[str, CustomValidationRuleRegexData]
):
    def __init__(self, data: CustomValidationRuleRegexData) -> None:
        super().__init__(data, lambda val: contains_regex(val, self.data.REGEX))

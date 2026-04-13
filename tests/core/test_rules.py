import pytest
from pydantic_core import PydanticCustomError

from src.core.rules import CustomValidationRule, CustomValidationRuleRegex
from src.core.types.internal import (
    CustomValidationRuleData,
    CustomValidationRuleRegexData,
)


@pytest.mark.parametrize(
    "custom_validation_rule",
    [
        CustomValidationRule[str](
            CustomValidationRuleData(
                ERROR_CODE="not_red", ERROR_MESSAGE="str is not equal to red"
            ),
            predicate_fn=lambda val: val == "Red",
        ),
        CustomValidationRuleRegex(
            CustomValidationRuleRegexData(
                ERROR_CODE="no_uppercase",
                ERROR_MESSAGE="Must contains an uppercase",
                REGEX=r"[A-Z]",
            )
        ),
    ],
    ids=["custom_validation_rule", "custom_validation_rule_regex"],
)
def test_custom_validation_rule_cases(
    custom_validation_rule: CustomValidationRule | CustomValidationRuleRegex,
) -> None:
    custom_validation_rule_data = custom_validation_rule.data
    pydantic_custom_exception = custom_validation_rule.pydantic_custom_exception

    assert isinstance(pydantic_custom_exception, PydanticCustomError)
    assert (
        pydantic_custom_exception.message()
        == custom_validation_rule_data.ERROR_MESSAGE
    )
    assert pydantic_custom_exception.type == custom_validation_rule_data.ERROR_CODE

    with pytest.raises(PydanticCustomError):
        raise custom_validation_rule.pydantic_custom_exception

    with pytest.raises(PydanticCustomError):
        custom_validation_rule.validator("blue")

    assert custom_validation_rule.validator("Red") == "Red"

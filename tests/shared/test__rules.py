import re

import pytest
from pydantic_core import PydanticCustomError

from src.shared.rules import (
    contains_regex,
    make_custom_validator,
)


def predicate(val: str) -> bool:
    return val == "test"


CUSTOM_VALIDATOR = make_custom_validator(
    PydanticCustomError("test", "test"), predicate
)


def test_make_custom_validator_returns_callable() -> None:
    assert callable(
        make_custom_validator(PydanticCustomError("test", "test"), predicate)
    )


def test_custom_validator_returns_val_when_predicate_is_true() -> None:
    val = "test"
    assert CUSTOM_VALIDATOR(val) == val


def test_custom_validator_raises_pydantic_custom_error_when_predicate_is_false() -> (
    None
):
    val = "foo"
    with pytest.raises(PydanticCustomError):
        assert CUSTOM_VALIDATOR(val) == val


@pytest.mark.parametrize(
    ("val", "regex", "expected_bool"),
    [
        ("123", r"^\d+$", True),
        ("abc", r"^\d+$", False),
        ("test@un.com", r"\.com$", True),
        ("test@un.fr", r"\.com$", False),
        ("hello", r"ell", True),
    ],
    ids=[
        "true_when_digits_match",
        "false_when_digits_mismatch",
        "true_when_suffix_matches",
        "false_when_suffix_mismatches",
        "true_when_substring_exists",
    ],
)
def test_contains_regex_returns_expected_bool(
    val: str, regex: str, *, expected_bool: bool
) -> None:
    assert contains_regex(val, regex) == expected_bool


def test_contains_regex_raises_error_when_invalid_pattern() -> None:
    with pytest.raises(re.error):
        contains_regex("data", r"[")

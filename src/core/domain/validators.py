import re
from typing import TYPE_CHECKING

from user_agents import parse


if TYPE_CHECKING:
    from pydantic_core import PydanticCustomError

    from src.core.types.interfaces import PredicateFn, ValidatorFn


def contains_no_space(val: str) -> bool:
    return " " not in val


def contains_no_value(search: str, val: str) -> bool:
    return search.lower() not in val.lower()


def contains_regex(val: str, regex: str) -> bool:
    return bool(re.search(regex, val))


def is_valid_ua(val: str) -> bool:
    user_agent = parse(val)
    return (
        not (user_agent.get_browser() == "Other" and user_agent.get_os() == "Other")
        or user_agent.is_bot
    )


def make_custom_validator[TVal](
    pydantic_custom_exception: PydanticCustomError,
    predicate: PredicateFn[TVal],
) -> ValidatorFn:
    def validator(val: TVal) -> TVal:
        if not predicate(val):
            raise pydantic_custom_exception
        return val

    return validator

import re
from collections.abc import Callable
from typing import Concatenate

from pydantic_core import PydanticCustomError
from user_agents import parse


def contains_no_space(val: str) -> bool:
    return " " not in val


def contains_value(val: str, search: str) -> bool:
    return search in val


def contains_regex(val: str, regex: str) -> bool:
    return bool(re.search(regex, val))


def contains_ua(ua: str) -> bool:
    user_agent = parse(ua)
    is_unknown = (
        user_agent.get_browser() == "Other" and user_agent.get_os() == "Other"
    )
    return not user_agent.is_bot or is_unknown


def make_custom_field_validator[**P](
    pydantic_custom_exception: PydanticCustomError,
    func: Callable[Concatenate[str, P], bool],
    *args: P.args,
    **kwargs: P.kwargs,
) -> Callable[[str], str]:
    def validator(val: str) -> str:
        if not func(val, *args, **kwargs):
            raise pydantic_custom_exception
        return val

    return validator

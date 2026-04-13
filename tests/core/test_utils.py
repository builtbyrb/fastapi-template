import datetime
from enum import IntEnum, StrEnum
from ipaddress import IPv4Address, IPv6Address

import pytest
from pydantic_core import PydanticCustomError

from src.core.constants import USER_AGENT_FORMAT_RULE
from src.core.types.alias import Environment, IpAnyAddress
from src.core.utils import (
    enum_do_dict,
    get_utc_datetime,
    remove_email_domain,
    serialize_ip,
    to_seconds,
    to_timedelta,
)
from src.core.validators import (
    contains_no_space,
    contains_no_value,
    contains_regex,
    is_valid_ua,
    make_custom_validator,
)


def test_get_utc_datetime_return_datetime_object() -> None:
    current_utc_datetime = get_utc_datetime()
    assert isinstance(current_utc_datetime, datetime.datetime)


def test_enum_to_dict_return_correct_dict() -> None:
    class TestStrEnum(StrEnum):
        TEST = "TEST"
        FOO = "Foo"

    class TestIntEnum(IntEnum):
        FOO = 12
        BAR = 24

    str_enum_dict = enum_do_dict(TestStrEnum)
    int_enum_dict = enum_do_dict(TestIntEnum)
    env_enum_dict = enum_do_dict(Environment)

    assert str_enum_dict == {"TEST": "TEST", "FOO": "Foo"}
    assert int_enum_dict == {"FOO": 12, "BAR": 24}
    assert env_enum_dict == {"DEV": "DEV", "PROD": "PROD", "STAG": "STAG"}


def test_to_timedelta_return_timedelta() -> None:
    minutes = 10
    result = to_timedelta(minutes)

    assert isinstance(result, datetime.timedelta)


def test_to_seconds_return_valid_seconds() -> None:
    minutes = 1
    result = to_seconds(to_timedelta(minutes))

    assert result == 60


@pytest.mark.parametrize(
    ("username", "domain"),
    [("jean_du_67", "@gmail.com"), ("JeanDu78", "@spain.co.uk")],
    ids=["basic_domain", "complex_domain"],
)
def test_remove_email_domain_cases(username: str, domain: str) -> None:
    assert remove_email_domain(username + domain) == username


@pytest.mark.parametrize(
    ("ip", "expected_ip"),
    [
        (IPv4Address(address="127.1.0.2"), "127.1.0.2"),
        (
            IPv6Address(address="2001:0db8:0000:0000:0008:0800:200c:417a"),
            "2001:db8::8:800:200c:417a",
        ),
    ],
    ids=["ipv4", "ipv6"],
)
def test_serialize_ip_cases(ip: IpAnyAddress, expected_ip: str) -> None:
    assert serialize_ip(ip) == expected_ip


@pytest.mark.parametrize(
    ("value", "expected_bool"),
    [
        ("foo bar", False),
        (
            """foo
        bar""",
            False,
        ),
        ("foo", True),
    ],
    ids=["invalid", "complex_invalid", "valid"],
)
def test_contains_no_space_cases(value: str, *, expected_bool: bool) -> None:
    assert contains_no_space(value) == expected_bool


def test_contains_no_value_return_false() -> None:
    search = "foo"
    val = "helloFoo"

    assert not contains_no_value(search, val)


def test_contains_regex_have_lowercase() -> None:
    val = "hello"
    regex = r"[a-z]"

    assert contains_regex(val, regex)


@pytest.mark.parametrize(
    ("ua", "expected_bool"),
    [
        ("foo", False),
        ("", False),
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
            True,
        ),
    ],
    ids=[
        "simple_invalid",
        "empty_string",
        "valid_chrome_ua",
    ],
)
def test_is_valid_ua_cases(ua: str, *, expected_bool: bool) -> None:
    assert is_valid_ua(ua) == expected_bool


def test_make_custom_validator() -> None:
    validator = make_custom_validator(
        USER_AGENT_FORMAT_RULE.pydantic_custom_exception, predicate=is_valid_ua
    )
    with pytest.raises(PydanticCustomError):
        validator("foo")

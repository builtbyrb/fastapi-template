import datetime
from enum import IntEnum, StrEnum

from src.core.constants import Environment
from src.core.domain import (
    enum_do_dict,
    get_utc_datetime,
    to_seconds,
    to_timedelta,
)


def test_type_get_utc_datetime() -> None:
    current_utc_datetime = get_utc_datetime()
    assert isinstance(current_utc_datetime, datetime.datetime)


def test_dict_content_enum_to_dict() -> None:
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


def test_type_to_timedelta() -> None:
    minutes = 10
    result = to_timedelta(minutes)

    assert isinstance(result, datetime.timedelta)


def test_to_seconds() -> None:
    minutes = 1
    result = to_seconds(to_timedelta(minutes))

    assert result == 60

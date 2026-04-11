import datetime
from datetime import timedelta
from enum import Enum
from typing import Any

from pydantic import EmailStr
from pydantic.networks import IPvAnyAddressType


def get_utc_datetime() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def enum_do_dict(enum: type[Enum]) -> dict[str, Any]:
    return {e.name: e.value for e in enum}


def to_timedelta(minutes: int) -> timedelta:
    return timedelta(minutes=minutes)


def to_seconds(timedelta: timedelta) -> int:
    return int(timedelta.total_seconds())


def remove_email_domain(val: EmailStr) -> EmailStr:
    return val.split("@")[0]


def serialize_ip(val: IPvAnyAddressType) -> str:
    return val.compressed

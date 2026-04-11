import datetime
from collections.abc import Mapping
from datetime import timedelta
from enum import Enum
from typing import Any

from pydantic import EmailStr
from pydantic.networks import IPvAnyAddressType

from src.core.constants import Environment
from src.core.exceptions import (
    AppClientIpNotFound,
    setup_sync_uncaught_exception_handler,
)
from src.core.logging.logging import setup_logging
from src.core.types.typings import (
    ANY_IP_ADAPTER,
    IpAnyAddress,
)


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


def resolve_ip_form_data(
    headers: Mapping[str, str],
    client_host: str | None,
    environment: Environment,
    default_dev_ip: IpAnyAddress,
    resolve_ip_header: str,
) -> IpAnyAddress:
    if environment == Environment.DEV:
        return default_dev_ip

    ip = headers.get(resolve_ip_header) or client_host

    if not ip:
        raise AppClientIpNotFound

    return ANY_IP_ADAPTER.validate_python(ip)


def start_setup() -> None:
    setup_sync_uncaught_exception_handler()
    setup_logging()

import datetime
from collections.abc import Mapping
from datetime import timedelta
from enum import Enum
from typing import Any

from fastapi import Request
from pydantic import EmailStr

from src.core.constants import Environment
from src.core.exceptions import (
    AppClientIpNotFound,
    setup_sync_uncaught_exception_handler,
)
from src.core.logging.logging import setup_logging
from src.core.settings import APP_ENV_SETTINGS
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


def resolve_ip_form_data(
    headers: Mapping[str, str], client_host: str | None, environment: Environment
) -> IpAnyAddress:
    if environment == Environment.DEV:
        return ANY_IP_ADAPTER.validate_python("127.0.0.1")

    ip = headers.get("X-Real-Ip") or client_host

    if not ip:
        raise AppClientIpNotFound

    return ANY_IP_ADAPTER.validate_python(ip)


async def get_client_ip(
    request: Request, environment: Environment = APP_ENV_SETTINGS.ENVIRONMENT
) -> IpAnyAddress:
    return resolve_ip_form_data(
        request.headers, request.client.host if request.client else None, environment
    )


def start_setup() -> None:
    setup_sync_uncaught_exception_handler()
    setup_logging()

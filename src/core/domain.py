import datetime
from datetime import timedelta
from enum import Enum
from typing import Any

from fastapi import Request

from src.core.constants import Environment
from src.core.config.env import APP_ENV
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


async def get_client_ip(request: Request) -> IpAnyAddress:
    if APP_ENV.ENVIRONMENT == Environment.DEV:
        return ANY_IP_ADAPTER.validate_python("127.0.0.1")

    ip = request.headers.get("X-Real-Ip")

    if not ip and request.client:
        return ANY_IP_ADAPTER.validate_python(request.client.host)

    if not ip:
        raise AppClientIpNotFound

    return ANY_IP_ADAPTER.validate_python(ip)


def start_setup() -> None:
    setup_sync_uncaught_exception_handler()
    setup_logging()

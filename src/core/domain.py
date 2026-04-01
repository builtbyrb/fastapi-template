import datetime
from datetime import timedelta
from enum import Enum
from typing import Any

from src.core.exceptions import setup_sync_uncaught_exception_handler
from src.core.logging.logging import setup_logging


def get_utc_datetime() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def enum_do_dict(enum: type[Enum]) -> dict[str, Any]:
    return {e.name: e.value for e in enum}


def to_timedelta(minutes: int) -> timedelta:
    return timedelta(minutes=minutes)


def to_seconds(timedelta: timedelta) -> int:
    return int(timedelta.total_seconds())


def start_setup() -> None:
    setup_sync_uncaught_exception_handler()
    setup_logging()

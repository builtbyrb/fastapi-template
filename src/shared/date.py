import datetime
from datetime import timedelta


def get_utc_datetime() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def to_seconds(timedelta: timedelta) -> int:
    return int(timedelta.total_seconds())

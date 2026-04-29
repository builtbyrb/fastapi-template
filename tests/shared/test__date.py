import datetime

from src.shared.date import get_utc_datetime, to_seconds


def test_get_utc_datetime_returns_datetime() -> None:
    assert isinstance(get_utc_datetime(), datetime.datetime)


def test_get_utc_datetime_returns_datetime_in_utc_tz() -> None:
    assert get_utc_datetime().utcoffset() == datetime.timedelta(0)


def test_to_seconds_returns_int_when_valid_timedelta() -> None:
    assert isinstance(to_seconds(timedelta=datetime.timedelta(days=2)), int)


def test_to_seconds_returns_120_when_2_minutes_timedelta() -> None:
    assert to_seconds(timedelta=datetime.timedelta(minutes=2)) == 120

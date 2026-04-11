import datetime
from enum import IntEnum, StrEnum
from ipaddress import IPv4Address

import pytest

from src.core.domain import resolve_ip_form_data
from src.core.exceptions import AppClientIpNotFound
from src.core.types.alias import Environment
from src.core.types.internal import ResolveIpFromDataParams
from src.core.types.typings import ANY_IP_ADAPTER
from src.core.utils import (
    enum_do_dict,
    get_utc_datetime,
    remove_email_domain,
    serialize_ip,
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


def test_seconds_to_seconds() -> None:
    minutes = 1
    result = to_seconds(to_timedelta(minutes))

    assert result == 60


def test_result_remove_email_domain() -> None:
    domain = "@gmail.com"
    name = "example"
    assert remove_email_domain(name + domain) == name


def test_result_serialize_ip_with_ipv4() -> None:
    ip = IPv4Address(address="123.1.1.0")
    assert serialize_ip(ip) == "123.1.1.0"


@pytest.mark.parametrize(
    ("params", "expected_ip"),
    [
        (
            ResolveIpFromDataParams(
                environment=Environment.DEV,
                default_dev_ip="127.1.1.1",
                client_host=None,
                headers={},
                resolve_ip_header="",
            ),
            "127.1.1.1",
        ),
        (
            ResolveIpFromDataParams(
                environment=Environment.PROD,
                default_dev_ip="",
                client_host=None,
                headers={"X-IP": "127.1.1.1"},
                resolve_ip_header="X-IP",
            ),
            "127.1.1.1",
        ),
        (
            ResolveIpFromDataParams(
                environment=Environment.PROD,
                default_dev_ip="",
                client_host="127.1.1.1",
                headers={},
                resolve_ip_header="",
            ),
            "127.1.1.1",
        ),
        (
            ResolveIpFromDataParams(
                environment=Environment.PROD,
                default_dev_ip="",
                client_host="127.1.1.1",
                headers={"X-IP": "127.1.1.2"},
                resolve_ip_header="X-IP",
            ),
            "127.1.1.2",
        ),
    ],
)
def test_resolve_ip_case_params(
    params: ResolveIpFromDataParams,
    expected_ip: str,
) -> None:
    ip = ANY_IP_ADAPTER.dump_python(resolve_ip_form_data(params))
    assert ip == expected_ip


@pytest.mark.parametrize(
    "params",
    [
        ResolveIpFromDataParams(
            environment=Environment.PROD,
            default_dev_ip="",
            client_host=None,
            headers={},
            resolve_ip_header="",
        ),
        ResolveIpFromDataParams(
            environment=Environment.PROD,
            default_dev_ip="",
            client_host=None,
            headers={"X-IP": "foo"},
            resolve_ip_header="X-IP",
        ),
        ResolveIpFromDataParams(
            environment=Environment.PROD,
            default_dev_ip="",
            client_host="foo",
            headers={},
            resolve_ip_header="",
        ),
        ResolveIpFromDataParams(
            environment=Environment.PROD,
            default_dev_ip="",
            client_host="foo",
            headers={"X-IP": "foo"},
            resolve_ip_header="X-IP",
        ),
    ],
)
def test_resolve_ip_error(params: ResolveIpFromDataParams) -> None:
    with pytest.raises(AppClientIpNotFound):
        resolve_ip_form_data(params)

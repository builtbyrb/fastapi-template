from ipaddress import IPv4Address, IPv6Address

import pytest
from pydantic import BaseModel
from pydantic.networks import IPvAnyAddressType

from src.config.settings import Environment
from src.shared.web import (
    IpAnyAddress,
    ResolveIpFromDataParams,
    is_valid_ua,
    resolve_ip_form_data,
    serialize_ip,
)


ARGS_NAME = ("ip", "expected_ip")
ARGS_VALUES = [
    (IPv4Address("127.1.1.1"), "127.1.1.1"),
    (
        IPv6Address("2001:0db8:0000:0000:0000:ff00:0042:8329"),
        "2001:db8::ff00:42:8329",
    ),
]
ARGS_IDS = ["ipv4_when_ipv4", "ipv6_compressed_when_ipv6"]


@pytest.mark.parametrize(
    ARGS_NAME,
    ARGS_VALUES,
    ids=ARGS_IDS,
)
def test_serialize_ip_returns_expected_ip(
    ip: IPvAnyAddressType, expected_ip: str
) -> None:
    assert serialize_ip(ip) == expected_ip


@pytest.mark.parametrize(
    ARGS_NAME,
    ARGS_VALUES,
    ids=ARGS_IDS,
)
def test_ip_any_address_type_returns_expected_ip(
    ip: IPvAnyAddressType, expected_ip: str
) -> None:
    class TestModel(BaseModel):
        ip: IpAnyAddress

    assert TestModel.model_validate({"ip": ip}).model_dump()["ip"] == expected_ip


@pytest.mark.parametrize(
    ("params", "expected_ip"),
    [
        (
            ResolveIpFromDataParams(
                environment=Environment.DEV,
                default_dev_ip="127.1.1.1",
                client_host="127.2.2.2",
                resolve_ip_header="X-ip",
                headers={"X-ip": "127.3.3.3"},
            ),
            "127.1.1.1",
        ),
        (
            ResolveIpFromDataParams(
                environment=Environment.PROD,
                default_dev_ip="127.1.1.1",
                client_host="127.2.2.2",
                resolve_ip_header="X-ip",
                headers={"X-ip": "127.3.3.3"},
            ),
            "127.3.3.3",
        ),
        (
            ResolveIpFromDataParams(
                environment=Environment.PROD,
                default_dev_ip="127.1.1.1",
                client_host="127.2.2.2",
                resolve_ip_header="X-ip",
                headers={},
            ),
            "127.2.2.2",
        ),
        (
            ResolveIpFromDataParams(
                environment=Environment.PROD,
                default_dev_ip="127.1.1.1",
                client_host="127.2.2.2",
                resolve_ip_header="X-ip",
                headers={"X-id": "127.3.3.3"},
            ),
            "127.2.2.2",
        ),
    ],
    ids=[
        "default_dev_ip_when_dev_environment",
        "header_ip_when_resolve_ip_header",
        "client_ip_when_no_header",
        "client_ip_when_invalid_header",
    ],
)
def test_resolve_ip_from_data_returns_expected_ip(
    params: ResolveIpFromDataParams, expected_ip: str
) -> None:
    assert serialize_ip(resolve_ip_form_data(params)) == expected_ip


VALID_UA = "Mozilla/5.0 (Linux; Android 13; SM-S908U) AppleWebKit/537.36 "
"(KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36"


@pytest.mark.parametrize(
    ("ua", "expected_bool"),
    [(VALID_UA, True), ("foo", False), ("", False)],
    ids=[
        "true_when_valid_ua",
        "false_when_other_string",
        "false_when_empty_string",
    ],
)
def test_is_valid_ua_returns_expected_bool(ua: str, *, expected_bool: bool) -> None:
    assert is_valid_ua(ua) == expected_bool

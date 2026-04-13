import pytest

from src.core.domain.domain import resolve_ip_form_data
from src.core.domain.exceptions import ClientIpNotFound
from src.core.types.alias import Environment
from src.core.types.internal import ResolveIpFromDataParams
from src.core.types.typings import ANY_IP_ADAPTER


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
    ids=["dev_environment", "header_ip", "client_host", "all_ip"],
)
def test_resolve_ip_form_data_cases(
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
    ids=["no_data", "invalid_ip_header", "invalid_client_host", "all_invalid"],
)
def test_resolve_ip_raises_app_client_ip_not_found_cases(
    params: ResolveIpFromDataParams,
) -> None:
    with pytest.raises(ClientIpNotFound):
        resolve_ip_form_data(params)

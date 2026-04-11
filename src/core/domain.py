from collections.abc import Mapping

from src.core.constants import Environment
from src.core.exceptions import (
    AppClientIpNotFound,
)
from src.core.types.alias import IpAnyAddress
from src.core.types.typings import ANY_IP_ADAPTER


def resolve_ip_form_data(
    headers: Mapping[str, str],
    client_host: str | None,
    environment: Environment,
    default_dev_ip: str,
    resolve_ip_header: str,
) -> IpAnyAddress:
    if environment == Environment.DEV:
        return ANY_IP_ADAPTER.validate_python(default_dev_ip)

    ip = headers.get(resolve_ip_header) or client_host

    if not ip:
        raise AppClientIpNotFound

    return ANY_IP_ADAPTER.validate_python(ip)

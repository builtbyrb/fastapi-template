from pydantic import ValidationError

from src.core.exceptions import (
    AppClientIpNotFound,
)
from src.core.types.alias import Environment, IpAnyAddress
from src.core.types.internal import ResolveIpFromDataParams
from src.core.types.typings import ANY_IP_ADAPTER


def resolve_ip_form_data(params: ResolveIpFromDataParams) -> IpAnyAddress:
    if params.environment == Environment.DEV:
        return ANY_IP_ADAPTER.validate_python(params.default_dev_ip)

    try:
        ip = ANY_IP_ADAPTER.validate_python(
            params.headers.get(params.resolve_ip_header) or params.client_host
        )
    except ValidationError:
        ip = None

    if not ip:
        raise AppClientIpNotFound

    return ip

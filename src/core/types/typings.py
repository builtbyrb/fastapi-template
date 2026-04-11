from typing import Annotated

from pydantic import (
    AfterValidator,
    Field,
    TypeAdapter,
)
from pydantic.dataclasses import dataclass

from src.core.constants import (
    NO_SPACE_RULE,
    NO_SPACE_RULE_DATA,
    USER_AGENT_FORMAT_RULE,
    USER_AGENT_FORMAT_RULE_DATA,
)
from src.core.types.alias import AnyPort, IpAnyAddress


type UserAgent = Annotated[
    str,
    Field(json_schema_extra={"rules": [USER_AGENT_FORMAT_RULE_DATA.ERROR_CODE]}),
    AfterValidator(USER_AGENT_FORMAT_RULE.validator),
]

type NoSpaceStr = Annotated[
    str,
    Field(json_schema_extra={"rules": [NO_SPACE_RULE_DATA.ERROR_CODE]}),
    AfterValidator(NO_SPACE_RULE.validator),
]

ANY_IP_ADAPTER = TypeAdapter(IpAnyAddress)

ANY_PORT_ADAPTER = TypeAdapter(AnyPort)


@dataclass(frozen=True, kw_only=True)
class RequestInfo:
    ip: IpAnyAddress
    user_agent: UserAgent


@dataclass(frozen=True, kw_only=True)
class OptionalAuthInfo:
    ip: IpAnyAddress | None = None
    user_agent: UserAgent | None = None

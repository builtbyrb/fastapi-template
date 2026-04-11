from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    Field,
    IPvAnyAddress,
    PlainSerializer,
    TypeAdapter,
)

from src.core.constants import NO_SPACE_RULE_DATA, USER_AGENT_FORMAT_RULE_DATA
from src.core.rules import NO_SPACE_RULE, USER_AGENT_FORMAT_RULE


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

type IpAnyAddress = Annotated[IPvAnyAddress, PlainSerializer(str, return_type=str)]

type AnyPort = Annotated[int, Field(ge=0, le=65535)]

ANY_IP_ADAPTER = TypeAdapter(IpAnyAddress)

ANY_PORT_ADAPTER = TypeAdapter(AnyPort)

type OpenApiSchemaType = Literal[
    "string", "number", "integer", "boolean", "array", "object"
]

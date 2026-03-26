from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    Field,
    IPvAnyAddress,
    PlainSerializer,
    TypeAdapter,
)

from src.core.rules.rules import NO_SPACE_RULE, USER_AGENT_FORMAT_RULE


type UserAgent = Annotated[
    str,
    Field(json_schema_extra={"rules": [USER_AGENT_FORMAT_RULE.ERROR_CODE]}),
    AfterValidator(USER_AGENT_FORMAT_RULE.validator),
]

type IpAnyAddress = Annotated[IPvAnyAddress, PlainSerializer(str, return_type=str)]

ANY_IP_ADAPTER = TypeAdapter(IpAnyAddress)

type OpenApiSchemaType = Literal[
    "string", "number", "integer", "boolean", "array", "object"
]


type NoSpaceStr = Annotated[
    str,
    Field(json_schema_extra={"rules": [NO_SPACE_RULE.ERROR_CODE]}),
    AfterValidator(NO_SPACE_RULE.validator),
]

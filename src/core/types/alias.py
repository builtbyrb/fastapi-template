from typing import Annotated, Literal

from pydantic import (
    Field,
    IPvAnyAddress,
    PlainSerializer,
)

from src.core.utils import serialize_ip


type IpAnyAddress = Annotated[
    IPvAnyAddress, PlainSerializer(serialize_ip, return_type=str)
]


type OpenApiSchemaType = Literal[
    "string", "number", "integer", "boolean", "array", "object"
]


type AnyPort = Annotated[int, Field(ge=0, le=65535)]

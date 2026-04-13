from enum import StrEnum
from typing import Annotated, Literal

from pydantic import (
    BeforeValidator,
    Field,
    IPvAnyAddress,
    PlainSerializer,
)

from src.core.utils import bool_to_health, serialize_ip


type IpAnyAddress = Annotated[
    IPvAnyAddress, PlainSerializer(serialize_ip, return_type=str)
]

type HealthValues = Literal["healthy", "unhealthy"]

type Health = Annotated[
    HealthValues,
    BeforeValidator(
        lambda v: bool_to_health(status=v) if isinstance(v, bool) else v
    ),
]

type OpenApiSchemaType = Literal[
    "string", "number", "integer", "boolean", "array", "object"
]


type AnyPort = Annotated[int, Field(ge=0, le=65535)]


class Environment(StrEnum):
    DEV = "DEV"
    PROD = "PROD"
    STAG = "STAG"

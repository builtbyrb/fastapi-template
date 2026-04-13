from typing import Annotated

from pydantic import (
    AfterValidator,
    BeforeValidator,
    Field,
    TypeAdapter,
)
from pydantic.dataclasses import dataclass

from src.core.constants import (
    NO_SPACE_RULE,
    NO_SPACE_RULE_DATA,
    ONE_DIGIT_RULE,
    ONE_DIGIT_RULE_DATA,
    ONE_LOWERCASE_RULE,
    ONE_LOWERCASE_RULE_DATA,
    ONE_SPECIAL_CHAR_RULE,
    ONE_SPECIAL_CHAR_RULE_DATA,
    ONE_UPPERCASE_RULE,
    ONE_UPPERCASE_RULE_DATA,
    USER_AGENT_FORMAT_RULE,
    USER_AGENT_FORMAT_RULE_DATA,
)
from src.core.types.alias import AnyPort, HealthValues, IpAnyAddress
from src.core.utils import bool_to_health


ANY_IP_ADAPTER = TypeAdapter(IpAnyAddress)

ANY_PORT_ADAPTER = TypeAdapter(AnyPort)

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

type OneUppercaseStr = Annotated[
    str,
    Field(json_schema_extra={"rules": [ONE_UPPERCASE_RULE_DATA.ERROR_CODE]}),
    AfterValidator(ONE_UPPERCASE_RULE.validator),
]

type OneLowercaseStr = Annotated[
    str,
    Field(json_schema_extra={"rules": [ONE_LOWERCASE_RULE_DATA.ERROR_CODE]}),
    AfterValidator(ONE_LOWERCASE_RULE.validator),
]

type OneDigitStr = Annotated[
    str,
    Field(json_schema_extra={"rules": [ONE_DIGIT_RULE_DATA.ERROR_CODE]}),
    AfterValidator(ONE_DIGIT_RULE.validator),
]

type OneSpecialCharStr = Annotated[
    str,
    Field(json_schema_extra={"rules": [ONE_SPECIAL_CHAR_RULE_DATA.ERROR_CODE]}),
    AfterValidator(ONE_SPECIAL_CHAR_RULE.validator),
]





@dataclass(frozen=True, kw_only=True)
class RequestInfo:
    ip: IpAnyAddress
    user_agent: UserAgent


@dataclass(frozen=True, kw_only=True)
class OptionalAuthInfo:
    ip: IpAnyAddress | None = None
    user_agent: UserAgent | None = None

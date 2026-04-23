from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Annotated, Any, Literal, TypedDict

from fastapi import Request, status
from pydantic import (
    AfterValidator,
    BaseModel,
    Field,
    IPvAnyAddress,
    PlainSerializer,
    TypeAdapter,
    ValidationError,
)
from pydantic.networks import IPvAnyAddressType
from user_agents import parse

from src.config.settings import APP_ENV_SETTINGS, Environment
from src.shared.exceptions import AppException
from src.shared.rules import CustomValidationRule, CustomValidationRuleData


# region -------------------------- Ip -------------------------
def serialize_ip(val: IPvAnyAddressType) -> str:
    return val.compressed


type IpAnyAddress = Annotated[
    IPvAnyAddress, PlainSerializer(serialize_ip, return_type=str)
]

ANY_IP_ADAPTER = TypeAdapter(IpAnyAddress)


class ClientIpNotFoundException(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Client IP could not be determined",
        )


@dataclass(frozen=True, kw_only=True)
class ResolveIpFromDataParams:
    environment: Environment
    default_dev_ip: str
    client_host: str | None
    headers: Mapping[str, str]
    resolve_ip_header: str


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
        raise ClientIpNotFoundException

    return ip


async def get_client_ip(
    request: Request,
    environment: Environment = APP_ENV_SETTINGS.ENVIRONMENT,
    default_dev_ip: str = APP_ENV_SETTINGS.DEFAULT_DEV_IP,
    resolve_ip_header: str = APP_ENV_SETTINGS.RESOLVE_IP_HEADER,
) -> IpAnyAddress:
    return resolve_ip_form_data(
        ResolveIpFromDataParams(
            environment=environment,
            default_dev_ip=default_dev_ip,
            client_host=request.client.host if request.client else None,
            headers=request.headers,
            resolve_ip_header=resolve_ip_header,
        )
    )


# endregion


# region -------------------------- UserAgent -------------------------
def is_valid_ua(val: str) -> bool:
    user_agent = parse(val)
    is_unknown = (
        user_agent.get_browser() == "Other" and user_agent.get_os() == "Other"
    )
    is_invalid = is_unknown or user_agent.is_bot
    return not is_invalid


USER_AGENT_FORMAT_RULE_DATA = CustomValidationRuleData(
    EXC_CODE="invalid_user_agent_format", EXC_MESSAGE="Invalid User-Agent format"
)

USER_AGENT_FORMAT_RULE = CustomValidationRule(
    data=USER_AGENT_FORMAT_RULE_DATA, predicate_fn=is_valid_ua
)


type UserAgent = Annotated[
    str,
    Field(json_schema_extra={"rules": [USER_AGENT_FORMAT_RULE_DATA.EXC_CODE]}),
    AfterValidator(USER_AGENT_FORMAT_RULE.validator),
]
# endregion

# region -------------------------- OpenApi -------------------------
type OpenApiSchemaType = Literal[
    "string", "number", "integer", "boolean", "array", "object"
]


class OpenApiHeaderSchemaResponseDict(TypedDict):
    type: OpenApiSchemaType


class OpenApiHeaderResponseDict(TypedDict):
    description: str
    schema: OpenApiHeaderSchemaResponseDict


type OpenApiHeadersResponseDict = dict[str, OpenApiHeaderResponseDict]


class OpenApiResponse(BaseModel):
    status_code: int
    description: str
    headers: Sequence[OpenApiHeaderResponse] | None = None
    response_model: type[BaseModel]

    @property
    def openapi_headers_response(self) -> OpenApiHeadersResponseDict | None:
        if not self.headers:
            return None

        headers_dict: OpenApiHeadersResponseDict = {}
        for data in self.headers:
            headers_dict[data.name] = {
                "description": data.description,
                "schema": {"type": data.header_type},
            }
        return headers_dict

    @property
    def openapi_response(self) -> dict[str | int, dict[str, Any]]:
        response_dict = {
            "description": self.description,
            "model": self.response_model,
        }

        if self.headers:
            response_dict["headers"] = self.openapi_headers_response

        return {self.status_code: response_dict}


class OpenApiHeaderResponse(BaseModel):
    name: str
    header_type: OpenApiSchemaType = "string"
    description: str

    @property
    def header_dict(self) -> OpenApiHeadersResponseDict:
        return {
            self.name: {
                "description": self.description,
                "schema": {"type": self.header_type},
            }
        }


# endregion


# region -------------------------- Responses -------------------------
class ExceptionResponse(BaseModel):
    exc_code: str
    message: str


class ExceptionResponseWithContext[T: BaseModel](ExceptionResponse):
    context: T


CLIENT_IP_NOT_FOUND_OPENAPI_RESPONSE = OpenApiResponse(
    status_code=status.HTTP_404_NOT_FOUND,
    description="Client ip not found",
    response_model=ExceptionResponse,
)

# endregion

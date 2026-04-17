from typing import Annotated

from fastapi.params import Header
from pydantic import (
    BaseModel,
)

from src.core.dependencies import IpDep
from src.core.types.alias import Health
from src.core.types.typings import UserAgent


type UserAgentHeader = Annotated[
    UserAgent,
    Header(alias="User-Agent", description="User-Agent header from the client"),
]


class RequestInfoInput(BaseModel):
    ip: IpDep
    user_agent: UserAgentHeader


class HealthStatus(BaseModel):
    redis_health: Health
    sql_db_health: Health
    health: Health

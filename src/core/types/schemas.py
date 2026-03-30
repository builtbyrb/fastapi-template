from typing import Literal

from pydantic import BaseModel

from src.core.dependencies import IpDep
from src.core.types.request import UserAgentHeader


class RequestInfoInput(BaseModel):
    ip: IpDep
    user_agent: UserAgentHeader


class HealthStatus(BaseModel):
    status: Literal["healthy"]

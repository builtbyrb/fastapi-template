from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Cookie
from pydantic import BaseModel, Field

from src.core.domain.utils import get_utc_datetime, to_timedelta
from src.core.types.typings import IpAnyAddress, UserAgent
from src.refresh_token.settings import REFRESH_TOKEN_ENV_SETTINGS


type RefreshTokenCookie = Annotated[
    str,
    Cookie(
        alias=REFRESH_TOKEN_ENV_SETTINGS.REFRESH_TOKEN_COOKIE_KEY,
        description="Token used to refresh access and maintain session persistence",
    ),
]


class RefreshTokenUserIdGetter(BaseModel):
    user_id: UUID

    @property
    def identifier(self) -> str:
        return str(self.user_id)


class RefreshTokenJtiGetter(BaseModel):
    jti: UUID

    @property
    def identifier(self) -> str:
        return str(self.jti)


class RefreshTokenBase(BaseModel):
    jti: UUID
    user_id: UUID

    user_agent: UserAgent
    ip: IpAnyAddress


class RefreshTokenCreate(RefreshTokenBase):
    pass


class RefreshTokenUpdate(BaseModel):
    user_id: UUID | None = Field(default=None)

    user_agent: UserAgent | None = Field(default=None)
    ip: IpAnyAddress | None = Field(default=None)


class RefreshTokenUpdateTimestamp(BaseModel):
    expires_at: datetime | None = Field(
        default_factory=lambda: (
            get_utc_datetime()
            + to_timedelta(REFRESH_TOKEN_ENV_SETTINGS.REFRESH_TOKEN_EXPIRE_MINUTES)
        ),
    )


type RefreshTokenGetter = RefreshTokenJtiGetter | RefreshTokenUserIdGetter

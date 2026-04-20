from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.date import get_utc_datetime
from src.shared.web import IpAnyAddress, UserAgent
from src.users.subdomains.refresh_token.settings import REFRESH_TOKEN_ENV_SETTINGS
from src.users.subdomains.refresh_token.storage import (
    RefreshToken,
    RefreshTokenJtiGetter,
)


class RefreshTokenUpdate(BaseModel):
    user_id: UUID | None = Field(default=None)

    user_agent: UserAgent | None = Field(default=None)
    ip: IpAnyAddress | None = Field(default=None)


class RefreshTokenUpdateTimestamp(BaseModel):
    expires_at: datetime | None = Field(
        default_factory=lambda: (
            get_utc_datetime()
            + timedelta(REFRESH_TOKEN_ENV_SETTINGS.REFRESH_TOKEN_EXPIRE_MINUTES)
        ),
    )


def update_refresh_token_dict(update: RefreshTokenUpdate) -> dict[str, Any]:
    update_timestamp_dict = RefreshTokenUpdateTimestamp().model_dump(
        exclude_none=True
    )
    update_dict = update.model_dump(exclude_unset=True)
    return {
        **update_timestamp_dict,
        **update_dict,
    }


class RefreshTokenUpdatePort(Protocol):
    async def update_refresh_token(
        self, sql_session: Any, getter: RefreshTokenJtiGetter, values: dict[str, Any]
    ) -> RefreshToken: ...


@dataclass(frozen=True, kw_only=True)
class RefreshTokenUpdateServiceParams:
    sql_session: AsyncSession
    refresh_token_repo: RefreshTokenUpdatePort
    getter: RefreshTokenJtiGetter
    update: RefreshTokenUpdate


async def refresh_token_update_service(
    params: RefreshTokenUpdateServiceParams,
) -> RefreshToken:
    update_dict = update_refresh_token_dict(params.update)
    return await params.refresh_token_repo.update_refresh_token(
        params.sql_session, params.getter, update_dict
    )

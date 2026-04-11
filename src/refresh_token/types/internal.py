from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils import get_utc_datetime, to_timedelta
from src.refresh_token.config.env import REFRESH_TOKEN_ENV


if TYPE_CHECKING:
    from src.refresh_token.types.interfaces import (
        RefreshTokenInsertPort,
        RefreshTokenUpdatePort,
    )
    from src.refresh_token.types.schemas import (
        RefreshTokenCreate,
        RefreshTokenJtiGetter,
        RefreshTokenUpdate,
    )


@dataclass(frozen=True, kw_only=True)
class SetRefreshTokenCookieParams:
    response: Response
    token: str
    max_age: int


# region -------------------------- UserRefreshTokenCreate -------------------------
@dataclass(frozen=True, kw_only=True)
class RefreshTokenCreateServiceParams:
    session: AsyncSession
    refresh_token_repo: RefreshTokenInsertPort
    create: RefreshTokenCreate


class RefreshTokenCreateInternal(BaseModel):
    expires_at: datetime = Field(
        default_factory=lambda: (
            get_utc_datetime()
            + to_timedelta(REFRESH_TOKEN_ENV.REFRESH_TOKEN_EXPIRE_MINUTES)
        ),
    )
    created_at: datetime = Field(default_factory=get_utc_datetime)


# endregion


# region -------------------------- UserRefreshTokenUpdate -------------------------
@dataclass(frozen=True, kw_only=True)
class RefreshTokenUpdateServiceParams:
    session: AsyncSession
    refresh_token_repo: RefreshTokenUpdatePort
    getter: RefreshTokenJtiGetter
    update: RefreshTokenUpdate


# endregion

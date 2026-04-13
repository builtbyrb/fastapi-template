from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from src.core.domain.utils import get_utc_datetime, to_timedelta
from src.core.types.internal import HTTPExceptionDetails
from src.refresh_token.settings import REFRESH_TOKEN_ENV_SETTINGS


if TYPE_CHECKING:
    from fastapi import Response
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.refresh_token.types.interfaces import (
        RefreshTokenInsertPort,
        RefreshTokenUpdatePort,
    )
    from src.refresh_token.types.schemas import (
        RefreshTokenCreate,
        RefreshTokenJtiGetter,
        RefreshTokenUpdate,
    )


# region -------------------------- UserRefreshTokenCreate -------------------------
@dataclass(frozen=True, kw_only=True)
class RefreshTokenCreateServiceParams:
    sql_session: AsyncSession
    refresh_token_repo: RefreshTokenInsertPort
    create: RefreshTokenCreate


class RefreshTokenCreateInternal(BaseModel):
    expires_at: datetime = Field(
        default_factory=lambda: (
            get_utc_datetime()
            + to_timedelta(REFRESH_TOKEN_ENV_SETTINGS.REFRESH_TOKEN_EXPIRE_MINUTES)
        ),
    )
    created_at: datetime = Field(default_factory=get_utc_datetime)


# endregion


@dataclass(frozen=True, kw_only=True)
class RefreshTokenUpdateServiceParams:
    sql_session: AsyncSession
    refresh_token_repo: RefreshTokenUpdatePort
    getter: RefreshTokenJtiGetter
    update: RefreshTokenUpdate



@dataclass(frozen=True, kw_only=True)
class SetRefreshTokenCookieParams:
    response: Response
    token: str
    max_age: int


class RefreshTokenExceptionDetails(HTTPExceptionDetails):
    refresh_token: str

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
)


class RefreshTokenInsertPort(Protocol):
    async def insert_refresh_token(
        self, sql_session: Any, values: dict[str, Any]
    ) -> RefreshToken: ...


class RefreshTokenBase(BaseModel):
    jti: UUID
    user_id: UUID

    user_agent: UserAgent
    ip: IpAnyAddress


class RefreshTokenCreate(RefreshTokenBase):
    pass


class RefreshTokenCreateInternal(BaseModel):
    expires_at: datetime = Field(
        default_factory=lambda: (
            get_utc_datetime()
            + timedelta(REFRESH_TOKEN_ENV_SETTINGS.REFRESH_TOKEN_EXPIRE_MINUTES)
        ),
    )
    created_at: datetime = Field(default_factory=get_utc_datetime)


def create_refresh_token_dict(create: RefreshTokenCreate) -> dict[str, Any]:
    return {**create.model_dump(), **RefreshTokenCreateInternal().model_dump()}


@dataclass(frozen=True, kw_only=True)
class RefreshTokenCreateServiceParams:
    sql_session: AsyncSession
    refresh_token_repo: RefreshTokenInsertPort
    create: RefreshTokenCreate


async def refresh_token_create_service(
    params: RefreshTokenCreateServiceParams,
) -> RefreshToken:
    create_dict = create_refresh_token_dict(params.create)
    return await params.refresh_token_repo.insert_refresh_token(
        params.sql_session, create_dict
    )

import uuid
from dataclasses import dataclass
from typing import Protocol

from redis.typing import EncodableT

from src.users.subdomains.access_token.blacklist import append_prefix
from src.users.subdomains.access_token.settings import ACCESS_TOKEN_ENV_SETTINGS
from src.users.subdomains.access_token.storage import (
    AccessTokenJtiRepo,
)


class AccessTokenJtiInsert(AccessTokenJtiRepo, Protocol):
    async def insert(
        self,
        *,
        jti: str,
        value: EncodableT,
        ex_seconds: int,
    ) -> None: ...


@dataclass(kw_only=True, frozen=True)
class SharedBlacklistTokenParams:
    redis_access_token_jti_repo: AccessTokenJtiInsert
    prefix: str = ACCESS_TOKEN_ENV_SETTINGS.ACCESS_TOKEN_BLACKLIST_PREFIX


@dataclass(kw_only=True, frozen=True)
class InsertAccessTokenJtiData:
    access_token_jti: uuid.UUID
    value: EncodableT = 1
    ex_seconds: int = int(ACCESS_TOKEN_ENV_SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES / 60)


@dataclass(kw_only=True, frozen=True)
class BlacklistTokenParams(SharedBlacklistTokenParams):
    insert_data: InsertAccessTokenJtiData


async def blacklist_token(params: BlacklistTokenParams) -> None:
    name = append_prefix(params.insert_data.access_token_jti, params.prefix)
    await params.redis_access_token_jti_repo.insert(
        jti=name,
        value=params.insert_data.value,
        ex_seconds=params.insert_data.ex_seconds,
    )


@dataclass(kw_only=True, frozen=True)
class BlacklistTokensParams(SharedBlacklistTokenParams):
    insert_data: list[InsertAccessTokenJtiData]


async def blacklist_tokens(params: BlacklistTokensParams) -> None:
    for data in params.insert_data:
        await blacklist_token(
            BlacklistTokenParams(
                redis_access_token_jti_repo=params.redis_access_token_jti_repo,
                insert_data=data,
            )
        )

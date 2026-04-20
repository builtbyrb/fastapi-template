import uuid
from dataclasses import dataclass
from typing import Any, Protocol

import redis.asyncio as redis
from redis.typing import EncodableT

from src.users.subdomains.access_token.blacklist import append_prefix
from src.users.subdomains.access_token.settings import ACCESS_TOKEN_ENV_SETTINGS


class AccessTokenJtiInsert(Protocol):
    async def insert(
        self,
        *,
        client: Any,
        jti: str,
        value: EncodableT,
        ex_seconds: int,
    ) -> None: ...


@dataclass(kw_only=True, frozen=True)
class SharedBlacklistTokenParams:
    redis_client: redis.Redis
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
        client=params.redis_client,
        jti=name,
        value=params.insert_data.value,
        ex_seconds=params.insert_data.ex_seconds,
    )


@dataclass(kw_only=True, frozen=True)
class BlacklistTokensParams(SharedBlacklistTokenParams):
    insert_data: list[InsertAccessTokenJtiData]


async def blacklist_tokens(params: BlacklistTokensParams) -> None:
    async with params.redis_client.pipeline(transaction=True) as pipe:
        for data in params.insert_data:
            await blacklist_token(
                BlacklistTokenParams(
                    redis_client=pipe,
                    redis_access_token_jti_repo=params.redis_access_token_jti_repo,
                    insert_data=data,
                )
            )
        await pipe.execute()

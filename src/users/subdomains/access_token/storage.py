import uuid
from typing import Annotated, Protocol

import redis.asyncio as redis
from fastapi import Depends
from pydantic.dataclasses import dataclass
from redis.typing import EncodableT

from src.database.database import RedisClientDep
from src.users.subdomains.access_token.settings import ACCESS_TOKEN_ENV_SETTINGS


@dataclass(kw_only=True, frozen=True)
class InsertAccessTokenJtiData:
    access_token_jti: uuid.UUID
    value: EncodableT = 1
    ex_seconds: int = int(ACCESS_TOKEN_ENV_SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES / 60)


class IsAccessTokenJtiBlacklistedPort(Protocol):
    async def is_token_blacklisted(self, access_token_jti: uuid.UUID) -> bool: ...


class RedisBlacklistAccessTokenJtiRepoAdapter:
    def __init__(
        self,
        client: redis.Redis,
        prefix: str = ACCESS_TOKEN_ENV_SETTINGS.ACCESS_TOKEN_BLACKLIST_PREFIX,
    ) -> None:
        self.client = client
        self.prefix = (
            prefix or ACCESS_TOKEN_ENV_SETTINGS.ACCESS_TOKEN_BLACKLIST_PREFIX
        )

    def append_prefix(self, access_token_jti: uuid.UUID) -> str:
        return f"{self.prefix}:{access_token_jti}"

    async def blacklist_token(
        self,
        insert_data: InsertAccessTokenJtiData,
    ) -> None:
        await self.client.set(
            name=self.append_prefix(insert_data.access_token_jti),
            value=insert_data.value,
            ex=insert_data.ex_seconds,
        )

    async def blacklist_tokens(
        self, insert_data: list[InsertAccessTokenJtiData]
    ) -> None:
        async with self.client.pipeline(transaction=True) as pipe:
            for data in insert_data:
                await self.blacklist_token(insert_data=data)
        await pipe.execute()

    async def is_token_blacklisted(self, access_token_jti: uuid.UUID) -> bool:
        result = await self.client.exists(self.append_prefix(access_token_jti))
        return result > 0


async def get_redis_blacklist_token_jti_repo_adapter(
    client: RedisClientDep,
) -> RedisBlacklistAccessTokenJtiRepoAdapter:
    return RedisBlacklistAccessTokenJtiRepoAdapter(client)


AccessTokenBlacklistPortDep = Annotated[
    RedisBlacklistAccessTokenJtiRepoAdapter,
    Depends(get_redis_blacklist_token_jti_repo_adapter),
]

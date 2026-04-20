from typing import Any, Protocol

import redis.asyncio as redis
from redis.typing import EncodableT

from src.database.database import REDIS_MANGER


class AccessTokenJtiRepo(Protocol):
    @property
    def client(self) -> Any: ...


class RedisAccessTokenJtiRepo:
    def __init__(self, client: redis.Redis) -> None:
        self.client = client

    async def insert(
        self,
        *,
        jti: str,
        value: EncodableT,
        ex_seconds: int,
    ) -> None:
        await self.client.set(name=jti, value=value, ex=ex_seconds)

    async def count(self, jti: str) -> int:
        return await self.client.exists(jti)


REDIS_ACCESS_TOKEN_JTI_REPO = RedisAccessTokenJtiRepo(REDIS_MANGER.client)

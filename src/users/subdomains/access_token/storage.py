import redis.asyncio as redis
from redis.typing import EncodableT


class RedisAccessTokenJtiRepo:
    async def insert(
        self,
        *,
        client: redis.Redis,
        jti: str,
        value: EncodableT,
        ex_seconds: int,
    ) -> None:
        await client.set(name=jti, value=value, ex=ex_seconds)

    async def count(self, client: redis.Redis, jti: str) -> int:
        return await client.exists(jti)


REDIS_ACCESS_TOKEN_JTI_REPO = RedisAccessTokenJtiRepo()

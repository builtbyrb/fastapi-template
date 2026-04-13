from datetime import timedelta
from typing import TYPE_CHECKING

from src.auth.config.env import AUTH_ENV
from src.core.utils import to_seconds
from src.refresh_token.config.env import REFRESH_TOKEN_ENV


if TYPE_CHECKING:
    import uuid

    import redis.asyncio as redis


class RedisAuthAccessTokenBlacklistRepo:
    def __init__(self) -> None:
        self.prefix = REFRESH_TOKEN_ENV.REFRESH_TOKEN_BLACKLIST_PREFIX
        self.ex = to_seconds(timedelta(minutes=AUTH_ENV.ACCESS_TOKEN_EXPIRE_MINUTES))

    def append_prefix(self, jti: uuid.UUID) -> str:
        return f"{self.prefix}:{jti}"

    async def blacklist_token(
        self,
        client: redis.Redis,
        jti: uuid.UUID,
    ) -> None:
        await client.set(name=self.append_prefix(jti), value=1, ex=self.ex)

    async def blacklist_tokens(
        self, client: redis.Redis, jti_list: list[uuid.UUID]
    ) -> None:
        async with client.pipeline(transaction=True) as pipe:
            for jti in jti_list:
                await self.blacklist_token(pipe, jti)
            await pipe.execute()

    async def is_blacklisted(self, client: redis.Redis, jti: uuid.UUID) -> bool:
        result = await client.exists(self.append_prefix(jti))
        return result > 0


REDIS_AUTH_ACCESS_TOKEN_BLACKLIST_REPO = RedisAuthAccessTokenBlacklistRepo()

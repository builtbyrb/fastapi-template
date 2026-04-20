import uuid
from typing import Any, Protocol

import redis.asyncio as redis

from src.users.subdomains.access_token.settings import ACCESS_TOKEN_ENV_SETTINGS


class BlacklistTokenPort(Protocol):
    async def blacklist_token(self, client: Any, jti: uuid.UUID) -> None: ...


class BlacklistMultipleTokenPort(Protocol):
    async def blacklist_tokens(
        self, client: Any, jti_list: list[uuid.UUID]
    ) -> None: ...


class IsTokenBlacklistedPort(Protocol):
    async def is_blacklisted(self, client: Any, jti: uuid.UUID) -> bool: ...


class BlackListTokenRefreshPort(
    BlacklistTokenPort, BlacklistMultipleTokenPort, Protocol
): ...


class RedisAuthAccessTokenBlacklistRepo:
    def __init__(self) -> None:
        self.prefix = ACCESS_TOKEN_ENV_SETTINGS.ACCESS_TOKEN_BLACKLIST_PREFIX
        self.ex = int(ACCESS_TOKEN_ENV_SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES / 60)

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

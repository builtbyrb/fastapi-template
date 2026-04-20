import uuid
from dataclasses import dataclass
from typing import Protocol

from src.users.subdomains.access_token.blacklist import append_prefix
from src.users.subdomains.access_token.settings import ACCESS_TOKEN_ENV_SETTINGS
from src.users.subdomains.access_token.storage import AccessTokenJtiRepo


class AccessTokenJtiCount(AccessTokenJtiRepo, Protocol):
    async def count(self, jti: str) -> int: ...


@dataclass(kw_only=True, frozen=True)
class IsTokenBlacklistedParams:
    redis_access_token_jti_repo: AccessTokenJtiCount
    access_token_jti: uuid.UUID
    prefix: str = ACCESS_TOKEN_ENV_SETTINGS.ACCESS_TOKEN_BLACKLIST_PREFIX


async def is_token_blacklisted(params: IsTokenBlacklistedParams) -> bool:
    name = append_prefix(params.access_token_jti, params.prefix)
    result = await params.redis_access_token_jti_repo.count(name)
    return result > 0

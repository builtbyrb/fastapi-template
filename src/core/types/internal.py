from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    import redis.asyncio as redis
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.core.types.typings import IpAnyAddress, UserAgent


@dataclass(frozen=True, kw_only=True)
class RequestInfo:
    ip: IpAnyAddress
    user_agent: UserAgent


@dataclass(frozen=True, kw_only=True)
class OptionalAuthInfo:
    ip: IpAnyAddress | None = None
    user_agent: UserAgent | None = None


@dataclass(frozen=True, kw_only=True)
class DatabaseProviders:
    session: AsyncSession
    client: redis.Redis

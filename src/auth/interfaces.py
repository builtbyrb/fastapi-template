import uuid
from typing import Any, Protocol

from src.refresh_token.interfaces import (
    RefreshTokenDeleteAllByUserIdPort,
    RefreshTokenDeletePort,
    RefreshTokenInsertPort,
    RefreshTokenReadByJtiPort,
)


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


class AuthRefreshTokenRefreshPort(
    RefreshTokenInsertPort,
    RefreshTokenDeletePort,
    RefreshTokenDeleteAllByUserIdPort,
    RefreshTokenReadByJtiPort,
    Protocol,
): ...

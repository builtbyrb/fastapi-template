from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.auth.interfaces import (
        AuthRefreshTokenRefreshPort,
        BlacklistMultipleTokenPort,
        BlacklistTokenPort,
        BlackListTokenRefreshPort,
        IsTokenBlacklistedPort,
    )
    from src.auth.types.schemas import (
        OAuth2PasswordRequestFormStrictTyped,
        TokenDataCreate,
    )
    from src.core.types.internal import DatabaseProviders, RequestInfo
    from src.refresh_token.interfaces import (
        RefreshTokenDeleteAllByUserIdPort,
        RefreshTokenDeletePort,
        RefreshTokenInsertPort,
    )
    from src.refresh_token.types.schemas import (
        RefreshTokenJtiGetter,
        RefreshTokenUserIdGetter,
    )
    from src.users.interfaces import UserReadPort
    from src.users.types.typings import UserEmail


# region -------------------------- Token -------------------------
@dataclass(frozen=True, kw_only=True)
class TokenConfig:
    secret_key: str
    algorithm: str


@dataclass(frozen=True, kw_only=True)
class CreateTokenParams:
    data: TokenDataCreate
    config: TokenConfig


@dataclass(frozen=True, kw_only=True)
class DecodeTokenParams:
    token: str
    config: TokenConfig


# endregion


# region -------------------------- GetCurrentUserService -------------------------
@dataclass(frozen=True, kw_only=True)
class GetCurrentUserServiceParams:
    providers: DatabaseProviders
    user_repo: UserReadPort
    access_token_blacklist_repo: IsTokenBlacklistedPort
    token: str


# endregion


# region -------------------------- UserLoginService -------------------------
@dataclass(frozen=True, kw_only=True)
class AuthenticateUserServiceParams:
    session: AsyncSession
    user_repo: UserReadPort
    email: UserEmail
    password: str


@dataclass(frozen=True, kw_only=True)
class UserLoginServiceParams:
    session: AsyncSession
    user_repo: UserReadPort
    refresh_token_repo: RefreshTokenInsertPort
    req_info: RequestInfo
    form_data: OAuth2PasswordRequestFormStrictTyped


# endregion


# region -------------------------- RevokeUserSession ------------------------
@dataclass(frozen=True, kw_only=True)
class RevokeUserSessionServiceParams:
    providers: DatabaseProviders
    refresh_token_repo: RefreshTokenDeletePort
    access_token_blacklist_repo: BlacklistTokenPort
    getter: RefreshTokenJtiGetter


@dataclass(frozen=True, kw_only=True)
class RevokeAllUserSessionServiceParams:
    providers: DatabaseProviders
    access_token_blacklist_repo: BlacklistMultipleTokenPort
    refresh_token_repo: RefreshTokenDeleteAllByUserIdPort
    getter: RefreshTokenUserIdGetter


# endregion


# region -------------------------- UserRefreshToken -------------------------
@dataclass(frozen=True, kw_only=True)
class UserRefreshTokenServiceParams:
    providers: DatabaseProviders
    access_token_blacklist_repo: BlackListTokenRefreshPort
    refresh_token_repo: AuthRefreshTokenRefreshPort
    user_repo: UserReadPort
    req_info: RequestInfo
    refresh_token: str


# endregion

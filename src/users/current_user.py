from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.database.database import DatabaseProviders, DataBaseProvidersDep
from src.shared.security import (
    DecodeTokenParams,
    InvalidTokenException,
    decode_token,
)
from src.users.exceptions import UserException, UserExceptionContext
from src.users.storage import (
    SQL_ALCHEMY_USER_REPO,
    User,
    UserReadPort,
)
from src.users.subdomains.access_token.settings import ACCESS_TOKEN_ENV_SETTINGS
from src.users.subdomains.access_token.storage import (
    REDIS_AUTH_ACCESS_TOKEN_BLACKLIST_REPO,
    IsTokenBlacklistedPort,
)
from src.users.tokens import UserJwtTokenClaims
from src.users.validations import UserEmailGetter, UserOut


# region -------------------------- CurrentUser -------------------------
@dataclass(frozen=True, kw_only=True)
class GetCurrentUserServiceParams:
    providers: DatabaseProviders
    user_repo: UserReadPort
    access_token_blacklist_repo: IsTokenBlacklistedPort
    token: str


async def get_current_user_service(params: GetCurrentUserServiceParams) -> UserOut:
    access_token_payload = decode_token(
        DecodeTokenParams(
            token=params.token, config=ACCESS_TOKEN_ENV_SETTINGS.access_token_config
        ),
        UserJwtTokenClaims,
    )

    is_blacklisted = await params.access_token_blacklist_repo.is_blacklisted(
        params.providers.client, access_token_payload.jti
    )
    if is_blacklisted:
        raise InvalidTokenException

    user = await params.user_repo.get_model(
        params.providers.sql_session, UserEmailGetter(email=access_token_payload.sub)
    )

    return UserOut.model_validate(user)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token/")
TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(
    token: TokenDep, providers: DataBaseProvidersDep
) -> UserOut:
    return await get_current_user_service(
        GetCurrentUserServiceParams(
            providers=DatabaseProviders(
                sql_session=providers.sql_session, client=providers.client
            ),
            user_repo=SQL_ALCHEMY_USER_REPO,
            access_token_blacklist_repo=REDIS_AUTH_ACCESS_TOKEN_BLACKLIST_REPO,
            token=token,
        )
    )


CurrentUserDep = Annotated[UserOut, Depends(get_current_user)]
# endregion


# region -------------------------- CurrentActiveUser -------------------------
class UserDisabledException(UserException):
    def __init__(self, context: UserExceptionContext) -> None:
        super().__init__(message=f"User {context.user} is inactive", context=context)


def verify_disabled_user(user: UserOut | User) -> None:
    if user.disabled:
        raise UserDisabledException(UserExceptionContext(user=user.identifier))


def get_current_active_user(
    current_user: CurrentUserDep,
) -> UserOut:
    verify_disabled_user(current_user)
    return current_user


CurrentActiveUserDep = Annotated[UserOut, Depends(get_current_active_user)]
# endregion

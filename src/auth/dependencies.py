from typing import Annotated

from fastapi import Depends
from fastapi.security import (
    OAuth2PasswordBearer,
)

from src.auth.adapter import REDIS_AUTH_ACCESS_TOKEN_BLACKLIST_REPO
from src.auth.domain import verify_disabled_user
from src.auth.services import get_current_user_service
from src.auth.types.internal import (
    GetCurrentUserServiceParams,
)
from src.auth.types.schemas import OAuth2PasswordRequestFormStrictTyped
from src.core.dependencies import DataBaseProvidersDep
from src.core.types.internal import DatabaseProviders
from src.users.adapter import SQL_ALCHEMY_USER_REPO
from src.users.types.schemas import UserOut


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token/")


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


def get_current_active_user(
    current_user: CurrentUserDep,
) -> UserOut:
    verify_disabled_user(current_user)
    return current_user


TokenDep = Annotated[str, Depends(oauth2_scheme)]
FormDataDep = Annotated[OAuth2PasswordRequestFormStrictTyped, Depends()]
CurrentUserDep = Annotated[UserOut, Depends(get_current_user)]
CurrentActiveUserDep = Annotated[UserOut, Depends(get_current_active_user)]

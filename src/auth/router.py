from typing import Annotated

from fastapi import APIRouter, Depends, Response

from src.auth.adapter import (
    REDIS_AUTH_ACCESS_TOKEN_BLACKLIST_REPO,
)
from src.auth.config.config import AUTH_ERRORS
from src.auth.config.env import AUTH_ENV
from src.auth.config.exceptions import AUTH_CURRENT_USER_RESPONSE
from src.auth.dependencies import FormDataDep
from src.auth.services import user_login_service, user_refresh_service
from src.auth.types.internal import (
    UserLoginServiceParams,
    UserRefreshTokenServiceParams,
)
from src.auth.types.schemas import (
    AccessToken,
)
from src.core.dependencies import DataBaseProvidersDep, SessionDep
from src.core.types.internal import DatabaseProviders, RequestInfo
from src.core.types.schemas import RequestInfoInput
from src.refresh_token.adapter import SQL_ALCHEMY_REFRESH_TOKEN_REPO
from src.refresh_token.domain import set_refresh_token_cookie
from src.refresh_token.types.internal import SetRefreshTokenCookieParams
from src.refresh_token.types.request import RefreshTokenCookie
from src.users.adapter import SQL_ALCHEMY_USER_REPO


token_router = APIRouter(prefix="/token", tags=["Token"])


@token_router.post(
    "/",
    summary="User login",
    response_description="The access token and a http-only refresh token cookie.",
    responses={
        **AUTH_ERRORS.INCORRECT_CREDENTIALS.response,
        **AUTH_ERRORS.USER_DISABLED.response,
    },
)
async def login(
    session: SessionDep,
    form_data: FormDataDep,
    response: Response,
    req_info: Annotated[RequestInfoInput, Depends()],
) -> AccessToken:
    tokens = await user_login_service(
        UserLoginServiceParams(
            session=session,
            user_repo=SQL_ALCHEMY_USER_REPO,
            refresh_token_repo=SQL_ALCHEMY_REFRESH_TOKEN_REPO,
            req_info=RequestInfo(**req_info.model_dump()),
            form_data=form_data,
        )
    )

    set_refresh_token_cookie(
        SetRefreshTokenCookieParams(
            response=response,
            token=tokens.refresh_token,
            max_age=tokens.refresh_token_data_create.expiration_in_seconds,
        ),
    )

    return AccessToken(
        access_token=tokens.access_token, token_type=AUTH_ENV.ACCESS_TOKEN_TYPE
    )


@token_router.post(
    "/refresh",
    summary="Refresh access token",
    response_description="A new access token and a http-only refresh token cookie.",
    responses={**AUTH_CURRENT_USER_RESPONSE},
)
async def refresh(
    providers: DataBaseProvidersDep,
    response: Response,
    req_info: Annotated[RequestInfoInput, Depends()],
    refresh_token: RefreshTokenCookie,
) -> AccessToken:
    result = await user_refresh_service(
        UserRefreshTokenServiceParams(
            providers=DatabaseProviders(
                session=providers.session, client=providers.client
            ),
            access_token_blacklist_repo=REDIS_AUTH_ACCESS_TOKEN_BLACKLIST_REPO,
            refresh_token_repo=SQL_ALCHEMY_REFRESH_TOKEN_REPO,
            user_repo=SQL_ALCHEMY_USER_REPO,
            req_info=RequestInfo(**req_info.model_dump()),
            refresh_token=refresh_token,
        )
    )

    set_refresh_token_cookie(
        SetRefreshTokenCookieParams(
            response=response,
            token=result.refresh_token,
            max_age=result.refresh_token_data_create.expiration_in_seconds,
        )
    )

    return AccessToken(
        access_token=result.access_token, token_type=AUTH_ENV.ACCESS_TOKEN_TYPE
    )

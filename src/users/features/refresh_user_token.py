from dataclasses import dataclass
from typing import Annotated, Protocol

from fastapi import APIRouter, Depends, Response, status

from src.database.database import (
    DatabaseProviders,
    DatabaseProvidersDep,
)
from src.shared.security import (
    DecodeTokenParams,
    InvalidTokenException,
    decode_token,
)
from src.shared.web import ExceptionResponseWithContext, OpenApiResponse
from src.users.current_user import verify_disabled_user
from src.users.responses import CURRENT_ACTIVE_USER_RESPONSE
from src.users.storage import SQL_ALCHEMY_USER_REPO, UserReadPort
from src.users.subdomains.access_token.features.blacklist_token import (
    AccessTokenJtiInsert,
    BlacklistTokenParams,
    BlacklistTokensParams,
    InsertAccessTokenJtiData,
    blacklist_token,
    blacklist_tokens,
)
from src.users.subdomains.access_token.settings import ACCESS_TOKEN_ENV_SETTINGS
from src.users.subdomains.access_token.storage import (
    REDIS_ACCESS_TOKEN_JTI_REPO,
)
from src.users.subdomains.refresh_token.features.create_token import (
    RefreshTokenCreate,
    RefreshTokenCreateServiceParams,
    RefreshTokenInsertPort,
    refresh_token_create_service,
)
from src.users.subdomains.refresh_token.settings import REFRESH_TOKEN_ENV_SETTINGS
from src.users.subdomains.refresh_token.storage import (
    SQL_ALCHEMY_REFRESH_TOKEN_REPO,
    RefreshToken,
    RefreshTokenDeleteAllByUserIdPort,
    RefreshTokenDeletePort,
    RefreshTokenExceptionContext,
    RefreshTokenJtiGetter,
    RefreshTokenNotFoundException,
    RefreshTokenReadByJtiPort,
    RefreshTokenUserIdGetter,
)
from src.users.tokens import (
    AccessToken,
    RefreshTokenCookie,
    SetRefreshTokenCookieParams,
    UserJwtTokenClaims,
    UsersTokens,
    create_user_tokens,
    set_refresh_token_cookie,
)
from src.users.validations import RequestInfo, RequestInfoInput, UserEmailGetter


@dataclass(frozen=True, kw_only=True)
class RevokeUserSessionServiceParams:
    providers: DatabaseProviders
    refresh_token_repo: RefreshTokenDeletePort
    access_token_jti_repo: AccessTokenJtiInsert
    getter: RefreshTokenJtiGetter


async def revoke_user_session_service(
    params: RevokeUserSessionServiceParams,
) -> RefreshToken:
    await blacklist_token(
        BlacklistTokenParams(
            redis_client=params.providers.redis_client,
            redis_access_token_jti_repo=params.access_token_jti_repo,
            insert_data=InsertAccessTokenJtiData(access_token_jti=params.getter.jti),
        )
    )

    return await params.refresh_token_repo.delete_refresh_token(
        params.providers.sql_session, params.getter
    )


@dataclass(frozen=True, kw_only=True)
class RevokeAllUserSessionServiceParams:
    providers: DatabaseProviders
    access_token_jti_repo: AccessTokenJtiInsert
    refresh_token_repo: RefreshTokenDeleteAllByUserIdPort
    getter: RefreshTokenUserIdGetter


async def revoke_all_user_session_service(
    params: RevokeAllUserSessionServiceParams,
) -> list[RefreshToken]:
    refresh_tokens = (
        await params.refresh_token_repo.delete_all_refresh_token_by_user_id(
            params.providers.sql_session, params.getter
        )
    )

    await blacklist_tokens(
        BlacklistTokensParams(
            redis_client=params.providers.redis_client,
            redis_access_token_jti_repo=params.access_token_jti_repo,
            insert_data=[
                InsertAccessTokenJtiData(access_token_jti=rf.jti)
                for rf in refresh_tokens
            ],
        )
    )

    return refresh_tokens


class RefreshTokenRefreshPort(
    RefreshTokenInsertPort,
    RefreshTokenDeletePort,
    RefreshTokenDeleteAllByUserIdPort,
    RefreshTokenReadByJtiPort,
    Protocol,
): ...


@dataclass(frozen=True, kw_only=True)
class UserRefreshTokenServiceParams:
    providers: DatabaseProvidersDep
    access_token_jti_repo: AccessTokenJtiInsert
    refresh_token_repo: RefreshTokenRefreshPort
    user_repo: UserReadPort
    req_info: RequestInfo
    refresh_token: str


async def user_refresh_service(
    params: UserRefreshTokenServiceParams,
) -> UsersTokens:
    sql_session = params.providers.sql_session

    refresh_token_data = decode_token(
        DecodeTokenParams(
            token=params.refresh_token,
            config=REFRESH_TOKEN_ENV_SETTINGS.refresh_token_config,
        ),
        UserJwtTokenClaims,
    )
    user = await params.user_repo.get_model(
        sql_session, UserEmailGetter(email=refresh_token_data.sub)
    )

    verify_disabled_user(user)
    try:
        current_user_refresh_token = await params.refresh_token_repo.get_by_jti(
            sql_session, RefreshTokenJtiGetter(jti=refresh_token_data.jti)
        )
    except RefreshTokenNotFoundException as err:
        raise InvalidTokenException from err

    if (
        params.req_info.user_agent != current_user_refresh_token.user_agent
        and params.req_info.ip != current_user_refresh_token.ip
    ):
        await revoke_all_user_session_service(
            RevokeAllUserSessionServiceParams(
                providers=params.providers,
                access_token_jti_repo=params.access_token_jti_repo,
                refresh_token_repo=params.refresh_token_repo,
                getter=RefreshTokenUserIdGetter(user_id=user.id),
            )
        )

        await sql_session.commit()

        raise InvalidTokenException

    result = create_user_tokens(user.email)

    await revoke_user_session_service(
        RevokeUserSessionServiceParams(
            providers=params.providers,
            refresh_token_repo=params.refresh_token_repo,
            access_token_jti_repo=params.access_token_jti_repo,
            getter=RefreshTokenJtiGetter(jti=current_user_refresh_token.jti),
        )
    )

    await refresh_token_create_service(
        RefreshTokenCreateServiceParams(
            sql_session=sql_session,
            refresh_token_repo=params.refresh_token_repo,
            create=RefreshTokenCreate(
                jti=result.refresh_token_claims.jti,
                user_id=user.id,
                user_agent=params.req_info.user_agent,
                ip=params.req_info.ip,
            ),
        )
    )

    await sql_session.commit()

    return result


class UserRefreshTokenNotFoundExceptionResponse(ExceptionResponseWithContext):
    context: RefreshTokenExceptionContext


USER_REFRESH_TOKEN_NOT_FOUND_OPENAPI_RESPONSE = OpenApiResponse(
    status_code=status.HTTP_404_NOT_FOUND,
    description="Refresh token not found",
    response_model=UserRefreshTokenNotFoundExceptionResponse,
)

router = APIRouter()


@router.post(
    "/refresh_token",
    summary="Refresh access token",
    response_description="A new access token and a http-only refresh token cookie.",
    responses={
        **CURRENT_ACTIVE_USER_RESPONSE,
        **USER_REFRESH_TOKEN_NOT_FOUND_OPENAPI_RESPONSE.openapi_response,
    },
)
async def refresh(
    providers: DatabaseProvidersDep,
    response: Response,
    req_info: Annotated[RequestInfoInput, Depends()],
    refresh_token: RefreshTokenCookie,
) -> AccessToken:
    result = await user_refresh_service(
        UserRefreshTokenServiceParams(
            providers=providers,
            access_token_jti_repo=REDIS_ACCESS_TOKEN_JTI_REPO,
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
            max_age=int(
                REFRESH_TOKEN_ENV_SETTINGS.REFRESH_TOKEN_EXPIRE_MINUTES / 60
            ),
        )
    )

    return AccessToken(
        access_token=result.access_token,
        token_type=ACCESS_TOKEN_ENV_SETTINGS.ACCESS_TOKEN_TYPE,
    )

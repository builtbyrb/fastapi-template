from fastapi.concurrency import run_in_threadpool

from src.auth.config.env import AUTH_ENV
from src.auth.domain import (
    authenticate_user,
    create_user_tokens,
    decode_token,
    verify_disabled_user,
)
from src.auth.exceptions import AuthInvalidTokenException
from src.auth.types.internal import (
    AuthenticateUserServiceParams,
    DecodeTokenParams,
    GetCurrentUserServiceParams,
    RevokeAllUserSessionServiceParams,
    RevokeUserSessionServiceParams,
    UserLoginServiceParams,
    UserRefreshTokenServiceParams,
)
from src.auth.types.schemas import UsersTokens
from src.refresh_token.config.env import REFRESH_TOKEN_ENV
from src.refresh_token.exceptions import RefreshTokenNotFoundException
from src.refresh_token.models import RefreshToken
from src.refresh_token.services import refresh_token_create_service
from src.refresh_token.types.internal import RefreshTokenCreateServiceParams
from src.refresh_token.types.schemas import (
    RefreshTokenCreate,
    RefreshTokenJtiGetter,
    RefreshTokenUserIdGetter,
)
from src.users.exceptions import (
    UserNotFoundException,
)
from src.users.models import User
from src.users.types.schemas import (
    UserEmailGetter,
    UserOut,
)


# region -------------------------- GetCurrentUser -------------------------
async def get_current_user_service(params: GetCurrentUserServiceParams) -> UserOut:
    access_token_payload = decode_token(
        DecodeTokenParams(token=params.token, config=AUTH_ENV.access_token_config)
    )

    is_blacklisted = await params.access_token_blacklist_repo.is_blacklisted(
        params.providers.client, access_token_payload.jti
    )
    if is_blacklisted:
        raise AuthInvalidTokenException

    user = await params.user_repo.get_model(
        params.providers.session, UserEmailGetter(email=access_token_payload.sub)
    )

    return UserOut.model_validate(user)


# endregion


# region -------------------------- UserLogin -------------------------
async def authenticate_user_service(
    params: AuthenticateUserServiceParams,
) -> User:
    try:
        user = await params.user_repo.get_model(
            params.session, UserEmailGetter(email=params.email)
        )
    except UserNotFoundException:
        user = None

    return await run_in_threadpool(authenticate_user, user, params.password)


async def user_login_service(
    params: UserLoginServiceParams,
) -> UsersTokens:
    user = await authenticate_user_service(
        AuthenticateUserServiceParams(
            session=params.session,
            user_repo=params.user_repo,
            email=params.form_data.username,
            password=params.form_data.password,
        )
    )

    result = create_user_tokens(user)

    await refresh_token_create_service(
        RefreshTokenCreateServiceParams(
            session=params.session,
            refresh_token_repo=params.refresh_token_repo,
            create=RefreshTokenCreate(
                jti=result.refresh_token_data_create.jti,
                user_id=user.id,
                user_agent=params.req_info.user_agent,
                ip=params.req_info.ip,
            ),
        )
    )

    await params.session.commit()

    return result


# endregion


# region -------------------------- RevokeSession -------------------------
async def revoke_user_session_service(
    params: RevokeUserSessionServiceParams,
) -> RefreshToken:
    session = params.providers.session

    await params.access_token_blacklist_repo.blacklist_token(
        params.providers.client, params.getter.jti
    )

    return await params.refresh_token_repo.delete_refresh_token(
        session, params.getter
    )


async def revoke_all_user_session_service(
    params: RevokeAllUserSessionServiceParams,
) -> list[RefreshToken]:
    session = params.providers.session

    refresh_tokens = (
        await params.refresh_token_repo.delete_all_refresh_token_by_user_id(
            session, params.getter
        )
    )

    await params.access_token_blacklist_repo.blacklist_tokens(
        params.providers.client, [rf.jti for rf in refresh_tokens]
    )

    return refresh_tokens


# endregion


# region -------------------------- Refresh -------------------------
async def user_refresh_service(
    params: UserRefreshTokenServiceParams,
) -> UsersTokens:
    session = params.providers.session
    client = params.providers.client

    refresh_token_data = decode_token(
        DecodeTokenParams(
            token=params.refresh_token, config=REFRESH_TOKEN_ENV.refresh_token_config
        )
    )
    user = await params.user_repo.get_model(
        session, UserEmailGetter(email=refresh_token_data.sub)
    )

    verify_disabled_user(user)
    try:
        current_user_refresh_token = await params.refresh_token_repo.get_by_jti(
            session, RefreshTokenJtiGetter(jti=refresh_token_data.jti)
        )
    except RefreshTokenNotFoundException as err:
        raise AuthInvalidTokenException from err

    if (
        params.req_info.user_agent != current_user_refresh_token.user_agent
        and params.req_info.ip != current_user_refresh_token.ip
    ):
        await revoke_all_user_session_service(
            RevokeAllUserSessionServiceParams(
                providers=params.providers,
                access_token_blacklist_repo=params.access_token_blacklist_repo,
                refresh_token_repo=params.refresh_token_repo,
                getter=RefreshTokenUserIdGetter(user_id=user.id),
            )
        )

        await session.commit()

        raise AuthInvalidTokenException

    result = create_user_tokens(user)

    await params.access_token_blacklist_repo.blacklist_token(
        client, current_user_refresh_token.jti
    )
    await revoke_user_session_service(
        RevokeUserSessionServiceParams(
            providers=params.providers,
            refresh_token_repo=params.refresh_token_repo,
            access_token_blacklist_repo=params.access_token_blacklist_repo,
            getter=RefreshTokenJtiGetter(jti=refresh_token_data.jti),
        )
    )

    await refresh_token_create_service(
        RefreshTokenCreateServiceParams(
            session=session,
            refresh_token_repo=params.refresh_token_repo,
            create=RefreshTokenCreate(
                jti=result.refresh_token_data_create.jti,
                user_id=user.id,
                user_agent=params.req_info.user_agent,
                ip=params.req_info.ip,
            ),
        )
    )

    await session.commit()

    return result


# endregion

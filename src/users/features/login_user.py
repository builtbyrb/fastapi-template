from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Response, status
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import SqlSessionDep
from src.shared.security import DUMMY_HASH, verify_password
from src.shared.web import ExceptionResponse, OpenApiResponse
from src.users.current_user import UserDisabledException
from src.users.exceptions import UserException, UserExceptionContext
from src.users.responses import USER_DISABLED_OPENAPI_RESPONSE
from src.users.storage import (
    SQL_ALCHEMY_USER_REPO,
    User,
    UserNotFoundException,
    UserReadPort,
)
from src.users.subdomains.access_token.settings import ACCESS_TOKEN_ENV_SETTINGS
from src.users.subdomains.refresh_token.features.create_token import (
    RefreshTokenCreate,
    RefreshTokenCreateServiceParams,
    RefreshTokenInsertPort,
    refresh_token_create_service,
)
from src.users.subdomains.refresh_token.settings import REFRESH_TOKEN_ENV_SETTINGS
from src.users.subdomains.refresh_token.storage import SQL_ALCHEMY_REFRESH_TOKEN_REPO
from src.users.tokens import (
    AccessToken,
    SetRefreshTokenCookieParams,
    UsersTokens,
    create_user_tokens,
    set_refresh_token_cookie,
)
from src.users.validations import (
    RequestInfo,
    RequestInfoInput,
    UserEmail,
    UserEmailGetter,
)


class UserIncorrectCredentialsException(UserException):
    def __init__(self) -> None:
        super().__init__(
            message="Invalid email/username or password",
        )


@dataclass(frozen=True, kw_only=True)
class AuthenticateUserServiceParams:
    sql_session: AsyncSession
    user_repo: UserReadPort
    email: UserEmail
    password: str


def authenticate_user(user: User | None, password: str) -> User:
    if not user:
        verify_password(password, DUMMY_HASH)
        raise UserIncorrectCredentialsException
    correct_password = verify_password(password, user.password_hash)

    if not correct_password:
        raise UserIncorrectCredentialsException
    if user.disabled:
        raise UserDisabledException(UserExceptionContext(user=user.identifier))

    return user


async def authenticate_user_service(
    params: AuthenticateUserServiceParams,
) -> User:
    try:
        user = await params.user_repo.get_model(
            params.sql_session, UserEmailGetter(email=params.email)
        )
    except UserNotFoundException:
        user = None

    return await run_in_threadpool(authenticate_user, user, params.password)


class OAuth2PasswordRequestFormStrictTypedData(BaseModel):
    grant_type: str = Field(pattern="^password$")
    username: UserEmail
    password: str
    scope: str = ""
    client_id: str | None = None
    client_secret: str | None = None


class OAuth2PasswordRequestFormStrictTyped:
    def __init__(
        self,
        data: Annotated[OAuth2PasswordRequestFormStrictTypedData, Form()],
    ) -> None:
        self.grant_type = data.grant_type
        self.username = data.username
        self.password = data.password
        self.scopes = data.scope.split()
        self.client_id = data.client_id
        self.client_secret = data.client_secret


@dataclass(frozen=True, kw_only=True)
class UserLoginServiceParams:
    sql_session: AsyncSession
    user_repo: UserReadPort
    refresh_token_repo: RefreshTokenInsertPort
    req_info: RequestInfo
    form_data: OAuth2PasswordRequestFormStrictTyped


async def user_login_service(
    params: UserLoginServiceParams,
) -> UsersTokens:
    user = await authenticate_user_service(
        AuthenticateUserServiceParams(
            sql_session=params.sql_session,
            user_repo=params.user_repo,
            email=params.form_data.username,
            password=params.form_data.password,
        )
    )

    result = create_user_tokens(user.email)

    await refresh_token_create_service(
        RefreshTokenCreateServiceParams(
            sql_session=params.sql_session,
            refresh_token_repo=params.refresh_token_repo,
            create=RefreshTokenCreate(
                jti=result.refresh_token_claims.jti,
                user_id=user.id,
                user_agent=params.req_info.user_agent,
                ip=params.req_info.ip,
            ),
        )
    )

    await params.sql_session.commit()

    return result


FormDataDep = Annotated[OAuth2PasswordRequestFormStrictTyped, Depends()]


USER_INCORRECT_CREDENTIALS_OPENAPI_RESPONSE = OpenApiResponse(
    status_code=status.HTTP_401_UNAUTHORIZED,
    description="Incorrect username or password",
    response_model=ExceptionResponse,
)

router = APIRouter()


@router.post(
    "/login",
    summary="User login",
    response_description="The access token and a http-only refresh token cookie.",
    responses={
        **USER_INCORRECT_CREDENTIALS_OPENAPI_RESPONSE.openapi_response,
        **USER_DISABLED_OPENAPI_RESPONSE.openapi_response,
    },
)
async def login(
    sql_session: SqlSessionDep,
    form_data: FormDataDep,
    response: Response,
    req_info: Annotated[RequestInfoInput, Depends()],
) -> AccessToken:
    tokens = await user_login_service(
        UserLoginServiceParams(
            sql_session=sql_session,
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
            max_age=int(
                REFRESH_TOKEN_ENV_SETTINGS.REFRESH_TOKEN_EXPIRE_MINUTES / 60
            ),
        ),
    )

    return AccessToken(
        access_token=tokens.access_token,
        token_type=ACCESS_TOKEN_ENV_SETTINGS.ACCESS_TOKEN_TYPE,
    )

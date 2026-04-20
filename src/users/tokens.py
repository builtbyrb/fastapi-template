import uuid
from dataclasses import dataclass
from datetime import timedelta
from typing import Annotated

from fastapi import Cookie, Response
from pydantic import BaseModel

from src.shared.date import get_utc_datetime
from src.shared.security import BaseJwtTokenClaims, CreateTokenParams, create_token
from src.users.subdomains.access_token.settings import ACCESS_TOKEN_ENV_SETTINGS
from src.users.subdomains.refresh_token.settings import REFRESH_TOKEN_ENV_SETTINGS
from src.users.validations import UserEmail


class AccessToken(BaseModel):
    access_token: str
    token_type: str


type RefreshTokenCookie = Annotated[
    str,
    Cookie(
        alias=REFRESH_TOKEN_ENV_SETTINGS.REFRESH_TOKEN_COOKIE_KEY,
        description="Token used to refresh access and maintain session persistence",
    ),
]


class UserJwtTokenClaims(BaseJwtTokenClaims):
    jti: uuid.UUID
    sub: UserEmail


class UsersTokens(BaseModel):
    refresh_token: str
    refresh_token_claims: UserJwtTokenClaims
    access_token: str


def create_user_tokens(email: UserEmail) -> UsersTokens:
    refresh_token_data_create = UserJwtTokenClaims(
        sub=email,
        jti=uuid.uuid4(),
        exp=get_utc_datetime()
        + timedelta(minutes=REFRESH_TOKEN_ENV_SETTINGS.REFRESH_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = create_token(
        CreateTokenParams(
            claims=refresh_token_data_create.model_dump(mode="json"),
            config=REFRESH_TOKEN_ENV_SETTINGS.refresh_token_config,
        )
    )

    access_token_data_create = UserJwtTokenClaims(
        sub=email,
        jti=refresh_token_data_create.jti,
        exp=get_utc_datetime()
        + timedelta(minutes=ACCESS_TOKEN_ENV_SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    access_token = create_token(
        CreateTokenParams(
            claims=access_token_data_create.model_dump(mode="json"),
            config=ACCESS_TOKEN_ENV_SETTINGS.access_token_config,
        )
    )

    return UsersTokens(
        refresh_token=refresh_token,
        refresh_token_claims=refresh_token_data_create,
        access_token=access_token,
    )


@dataclass(frozen=True, kw_only=True)
class SetRefreshTokenCookieParams:
    response: Response
    token: str
    max_age: int


def set_refresh_token_cookie(params: SetRefreshTokenCookieParams) -> None:
    params.response.set_cookie(
        key=REFRESH_TOKEN_ENV_SETTINGS.REFRESH_TOKEN_COOKIE_KEY,
        value=params.token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=params.max_age,
    )

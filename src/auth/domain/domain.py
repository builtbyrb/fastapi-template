import uuid
from typing import TYPE_CHECKING

import jwt
from jwt import PyJWTError
from pydantic import ValidationError

from src.auth.constants import DUMMY_HASH
from src.auth.domain.exceptions import (
    AuthIncorrectCredentialsException,
    AuthInvalidTokenException,
    AuthUserDisabledException,
)
from src.auth.domain.security import verify_password
from src.auth.settings import AUTH_ENV_SETTINGS
from src.auth.types.internal import (
    CreateTokenParams,
    DecodeTokenParams,
)
from src.auth.types.schemas import TokenData, TokenDataCreate, UsersTokens
from src.core.domain.utils import get_utc_datetime, to_timedelta
from src.refresh_token.settings import REFRESH_TOKEN_ENV_SETTINGS


if TYPE_CHECKING:
    from src.users.models import User
    from src.users.types.schemas import UserOut


def create_token(
    params: CreateTokenParams,
) -> str:
    expire = params.data.expiration + get_utc_datetime()
    token_data = TokenData(sub=params.data.email, exp=expire, jti=params.data.jti)
    return jwt.encode(
        token_data.model_dump(mode="json"),
        params.config.secret_key,
        params.config.algorithm,
    )


def decode_token(params: DecodeTokenParams) -> TokenData:
    try:
        payload = jwt.decode(
            params.token, params.config.secret_key, params.config.algorithm
        )
        return TokenData.model_validate(payload)
    except (PyJWTError, ValidationError) as exc:
        raise AuthInvalidTokenException from exc


def authenticate_user(user: User | None, password: str) -> User:
    if not user:
        verify_password(password, DUMMY_HASH)
        raise AuthIncorrectCredentialsException
    correct_password = verify_password(password, user.password_hash)

    if not correct_password:
        raise AuthIncorrectCredentialsException
    if user.disabled:
        raise AuthUserDisabledException(user.identifier)

    return user


def verify_disabled_user(user: UserOut | User) -> None:
    if user.disabled:
        raise AuthUserDisabledException(user.identifier)


def create_user_tokens(user: User) -> UsersTokens:
    refresh_token_data_create = TokenDataCreate(
        email=user.email,
        jti=uuid.uuid4(),
        expiration=to_timedelta(
            minutes=REFRESH_TOKEN_ENV_SETTINGS.REFRESH_TOKEN_EXPIRE_MINUTES
        ),
    )
    refresh_token = create_token(
        CreateTokenParams(
            data=refresh_token_data_create,
            config=REFRESH_TOKEN_ENV_SETTINGS.refresh_token_config,
        )
    )

    access_token_data_create = TokenDataCreate(
        email=user.email,
        jti=refresh_token_data_create.jti,
        expiration=to_timedelta(AUTH_ENV_SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    access_token = create_token(
        CreateTokenParams(
            data=access_token_data_create,
            config=AUTH_ENV_SETTINGS.access_token_config,
        )
    )

    return UsersTokens(
        refresh_token=refresh_token,
        refresh_token_data_create=refresh_token_data_create,
        access_token=access_token,
    )

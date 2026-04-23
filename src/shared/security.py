import datetime
from dataclasses import dataclass
from typing import Annotated, Any, overload

import jwt
from pwdlib import PasswordHash
from pydantic import BaseModel, PlainSerializer, ValidationError

from src.shared.exceptions import AppException


class SecurityException(AppException):
    pass


class ExpiredTokenException(SecurityException):
    def __init__(self) -> None:
        super().__init__(message="Token has expired")


class InvalidTokenException(SecurityException):
    def __init__(self) -> None:
        super().__init__(message="Invalid token")


def datetime_to_timestamp(date: datetime.datetime) -> int:
    return int(date.timestamp())


type TimestampDatetime = Annotated[
    datetime.datetime, PlainSerializer(datetime_to_timestamp, return_type=int)
]


class BaseJwtTokenClaims(BaseModel):
    exp: TimestampDatetime


@dataclass(frozen=True, kw_only=True)
class TokenConfig:
    secret_key: str
    algorithm: str


@dataclass(frozen=True, kw_only=True)
class CreateTokenParams:
    claims: dict[str, Any]
    config: TokenConfig


def create_token(
    params: CreateTokenParams,
) -> str:
    return jwt.encode(
        params.claims,
        params.config.secret_key,
        params.config.algorithm,
    )


@dataclass(kw_only=True, frozen=True)
class DecodeTokenParams:
    token: str
    config: TokenConfig


@overload
def decode_token(
    params: DecodeTokenParams, decode_model: None = None
) -> dict[str, Any]: ...


@overload
def decode_token[T: BaseModel](
    params: DecodeTokenParams, decode_model: type[T]
) -> T: ...


def decode_token(
    params: DecodeTokenParams, decode_model: type[BaseModel] | None = None
) -> dict[str, Any] | BaseModel:
    try:
        payload = jwt.decode(
            params.token, params.config.secret_key, params.config.algorithm
        )
        if not decode_model:
            return payload

        return decode_model.model_validate(payload)
    except jwt.ExpiredSignatureError as err:
        raise ExpiredTokenException from err
    except (jwt.PyJWTError, ValidationError) as err:
        raise InvalidTokenException from err


password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummyPassword")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)

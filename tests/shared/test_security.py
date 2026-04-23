from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from pydantic import BaseModel, TypeAdapter, ValidationError

from src.shared.security import (
    BaseJwtTokenClaims,
    CreateTokenParams,
    DecodeTokenParams,
    ExpiredTokenException,
    InvalidTokenException,
    TimestampDatetime,
    TokenConfig,
    create_token,
    datetime_to_timestamp,
    decode_token,
    hash_password,
    verify_password,
)


DATETIME_NOW_UTC = datetime.now(UTC)

TOKEN_CLAIMS = {
    "exp": datetime_to_timestamp(DATETIME_NOW_UTC + timedelta(minutes=15)),
    "sub": "test_username",
}
TOKEN_SECRET_KEY = "7a6ae8f625e26bf350b01884beca94545c603cdce2ce64b1889d870e2d44b9ac"
TOKEN_ALGO = "HS256"
TOKEN_CONFIG = TokenConfig(secret_key=TOKEN_SECRET_KEY, algorithm=TOKEN_ALGO)
TOKEN = create_token(
    CreateTokenParams(
        claims=TOKEN_CLAIMS,
        config=TOKEN_CONFIG,
    )
)


def test_datetime_to_timestamp_returns_int_when_valid_data() -> None:
    assert isinstance(datetime_to_timestamp(DATETIME_NOW_UTC), int)


@pytest.mark.parametrize(
    ("value", "expected_exception"),
    [(True, ValidationError), ("foo", ValidationError)],
    ids=[
        "raises_validation_error_when_bool_value",
        "raises_validation_error_when_string_value",
    ],
)
def test_timestamp_datetime_type_raises_expected_exception(
    value: Any, expected_exception: type[Exception]
) -> None:
    timestamp_datetime_adapter = TypeAdapter[TimestampDatetime](TimestampDatetime)
    with pytest.raises(expected_exception):
        timestamp_datetime_adapter.validate_python(value)


def test_timestamp_datetime_returns_int_when_valid_datetime() -> None:
    class TimestampDatetimeTestModel(BaseModel):
        datetime: TimestampDatetime

    assert isinstance(
        TimestampDatetimeTestModel.model_validate(
            {"datetime": DATETIME_NOW_UTC}
        ).model_dump()["datetime"],
        int,
    )


def test_create_token_returns_str_when_valid_claims() -> None:
    assert isinstance(
        create_token(
            CreateTokenParams(
                claims=TOKEN_CLAIMS,
                config=TOKEN_CONFIG,
            )
        ),
        str,
    )


def test_decode_token_returns_dict_when_valid_token() -> None:
    assert isinstance(
        decode_token(DecodeTokenParams(token=TOKEN, config=TOKEN_CONFIG)), dict
    )


def test_decode_token_returns_decode_model_when_provided() -> None:
    class DecodeTokenModel(BaseJwtTokenClaims):
        sub: str

    assert isinstance(
        decode_token(
            DecodeTokenParams(token=TOKEN, config=TOKEN_CONFIG),
            decode_model=DecodeTokenModel,
        ),
        DecodeTokenModel,
    )


EXPIRED_TOKEN_CLAIMS = {
    "exp": datetime_to_timestamp(DATETIME_NOW_UTC - timedelta(minutes=15)),
    "sub": "test_username",
}

EXPIRED_TOKEN = create_token(
    CreateTokenParams(
        claims=EXPIRED_TOKEN_CLAIMS,
        config=TOKEN_CONFIG,
    )
)

INVALID_TOKEN_SECRET_KEY = (
    "ab7ecc8cc9fbc269dd6a16edc42cba3c7e58f80be88d1779494f663e66a157a8"
)
INVALID_TOKEN_SECRET_KEY_CONFIG = TokenConfig(
    secret_key=INVALID_TOKEN_SECRET_KEY, algorithm=TOKEN_ALGO
)


class InvalidDecodeTokenModel(BaseModel):
    sub: int


@pytest.mark.parametrize(
    ("decode_token_params", "decode_model", "expected_exception"),
    [
        (
            DecodeTokenParams(token=EXPIRED_TOKEN, config=TOKEN_CONFIG),
            None,
            ExpiredTokenException,
        ),
        (
            DecodeTokenParams(token=TOKEN, config=INVALID_TOKEN_SECRET_KEY_CONFIG),
            None,
            InvalidTokenException,
        ),
        (
            DecodeTokenParams(token=TOKEN, config=TOKEN_CONFIG),
            InvalidDecodeTokenModel,
            InvalidTokenException,
        ),
    ],
    ids=[
        "raises_expired_token_exception_when_token_is_expired",
        "raises_invalid_token_exception_when_secret_key_is_invalid",
        "raises_invalid_token_exception_when_decode_model_is_invalid",
    ],
)
def test_decode_token_model_raises_expected_exception(
    decode_token_params: DecodeTokenParams,
    decode_model: type[BaseModel] | None,
    expected_exception: type[Exception],
) -> None:
    with pytest.raises(expected_exception):
        decode_token(decode_token_params, decode_model=decode_model)


def test_hash_password_returns_different_str_when_valid_password() -> None:
    plain_password = "test"
    result = hash_password(plain_password)
    assert isinstance(result, str)
    assert result != plain_password


@pytest.mark.parametrize(
    ("plain_password", "password_to_hash", "expected_value"),
    [("bar", None, True), ("bar", "foo", False)],
    ids=["true_when_password_matches", "false_when_password_does_not_match"],
)
def test_verify_password_returns_expected_value(
    plain_password: str, password_to_hash: str | None, *, expected_value: bool
) -> None:
    if not password_to_hash:
        hashed_password = hash_password(plain_password)
    else:
        hashed_password = hash_password(password_to_hash)
    assert verify_password(plain_password, hashed_password) == expected_value

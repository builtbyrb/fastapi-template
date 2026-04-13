from typing import TYPE_CHECKING, Any

from src.refresh_token.settings import REFRESH_TOKEN_ENV_SETTINGS
from src.refresh_token.types.internal import (
    RefreshTokenCreateInternal,
    SetRefreshTokenCookieParams,
)
from src.refresh_token.types.schemas import (
    RefreshTokenCreate,
    RefreshTokenUpdate,
    RefreshTokenUpdateTimestamp,
)


if TYPE_CHECKING:
    from fastapi import Response


def create_refresh_token_dict(create: RefreshTokenCreate) -> dict[str, Any]:
    return {**create.model_dump(), **RefreshTokenCreateInternal().model_dump()}


def update_refresh_token_dict(update: RefreshTokenUpdate) -> dict[str, Any]:
    update_timestamp_dict = RefreshTokenUpdateTimestamp().model_dump(
        exclude_none=True
    )
    update_dict = update.model_dump(exclude_unset=True)
    return {
        **update_timestamp_dict,
        **update_dict,
    }


def set_refresh_token_cookie(params: SetRefreshTokenCookieParams) -> None:
    params.response.set_cookie(
        key=REFRESH_TOKEN_ENV_SETTINGS.REFRESH_TOKEN_COOKIE_KEY,
        value=params.token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=params.max_age,
    )


def delete_refresh_token_cookie(response: Response) -> None:
    response.delete_cookie(
        key=REFRESH_TOKEN_ENV_SETTINGS.REFRESH_TOKEN_COOKIE_KEY,
        httponly=True,
        secure=True,
        samesite="lax",
    )

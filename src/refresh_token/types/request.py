from typing import Annotated

from fastapi import Cookie

from src.refresh_token.config.env import REFRESH_TOKEN_ENV


type RefreshTokenCookie = Annotated[
    str,
    Cookie(
        alias=REFRESH_TOKEN_ENV.REFRESH_TOKEN_COOKIE_KEY,
        description="Token used to refresh access and maintain session persistence",
    ),
]

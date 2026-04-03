from pydantic import Field

from src.auth.types.internal import TokenConfig
from src.core.config.env import BaseEnvSettings


class RefreshTokenConfigEnv(BaseEnvSettings):
    REFRESH_TOKEN_SECRET_KEY: str = Field(default=...)

    REFRESH_TOKEN_ALGORITHM: str = Field(default="HS256")
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=10080)
    REFRESH_TOKEN_COOKIE_KEY: str = Field(default="refresh_token")
    REFRESH_TOKEN_LIMIT: int = Field(default=10)
    REFRESH_TOKEN_BLACKLIST_PREFIX: str = Field(default="blacklist")

    @property
    def refresh_token_config(self) -> TokenConfig:
        return TokenConfig(
            secret_key=self.REFRESH_TOKEN_SECRET_KEY,
            algorithm=self.REFRESH_TOKEN_ALGORITHM,
        )


REFRESH_TOKEN_ENV = RefreshTokenConfigEnv()

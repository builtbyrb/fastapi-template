from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.auth.types.internal import TokenConfig


class RefreshTokenConfigEnv(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    REFRESH_TOKEN_SECRET_KEY: str = Field(default=...)
    REFRESH_TOKEN_ALGORITHM: str = Field(default=...)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=...)

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

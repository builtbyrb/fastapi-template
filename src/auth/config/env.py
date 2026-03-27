from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.auth.types.internal import TokenConfig


class AuthConfigEnv(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    ACCESS_TOKEN_SECRET_KEY: str = Field(default=...)
    ACCESS_TOKEN_ALGORITHM: str = Field(default=...)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=...)

    ACCESS_TOKEN_TYPE: str = Field(default=...)

    @property
    def access_token_config(self) -> TokenConfig:
        return TokenConfig(
            secret_key=self.ACCESS_TOKEN_SECRET_KEY,
            algorithm=self.ACCESS_TOKEN_ALGORITHM,
        )


AUTH_ENV = AuthConfigEnv()

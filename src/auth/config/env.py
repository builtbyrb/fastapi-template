from pydantic import Field

from src.auth.types.internal import TokenConfig
from src.core.config.env import BaseEnvSettings


class AuthConfigEnv(BaseEnvSettings):
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

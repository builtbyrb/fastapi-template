from pydantic import Field

from src.config.settings import BaseEnvSettings
from src.shared.security import TokenConfig


class AccessTokenEnvSettings(BaseEnvSettings):
    ACCESS_TOKEN_SECRET_KEY: str = Field(default=...)

    ACCESS_TOKEN_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    ACCESS_TOKEN_TYPE: str = Field(default="Bearer")
    ACCESS_TOKEN_BLACKLIST_PREFIX: str = Field(default="blacklist")

    @property
    def access_token_config(self) -> TokenConfig:
        return TokenConfig(
            secret_key=self.ACCESS_TOKEN_SECRET_KEY,
            algorithm=self.ACCESS_TOKEN_ALGORITHM,
        )


ACCESS_TOKEN_ENV_SETTINGS = AccessTokenEnvSettings()

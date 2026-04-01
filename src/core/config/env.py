from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.config.constants import ENV_FILE, Environment


class BaseEnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )


class AppEnv(BaseEnvSettings):
    ENVIRONMENT: Environment = Field(default=...)

    POSTGRES_DRIVER_NAME: str = Field(default="postgresql+asyncpg")
    POSTGRES_USER: str = Field(default=...)
    POSTGRES_PASSWORD: str = Field(default=...)
    POSTGRES_DB: str = Field(default=...)
    PG_BOUNCER_HOST: str = Field(default=...)
    PG_BOUNCER_PORT: int = Field(default=5432)

    REDIS_HOST: str = Field(default=...)
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=...)


APP_ENV = AppEnv()

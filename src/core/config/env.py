from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.constants import Environment


class AppEnv(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    ENVIRONMENT: Environment = Field(default=...)

    POSTGRES_DRIVER_NAME: str = Field(default="postgresql+asyncpg")
    POSTGRES_USER: str = Field(default=...)
    POSTGRES_PASSWORD: str = Field(default=...)
    POSTGRES_DB: str = Field(default=...)
    PG_BOUNCER_HOST: str = Field(default=...)
    PG_BOUNCER_PORT: int = Field(default=5432)

    REDIS_HOST: str = Field(default=...)
    REDIS_PORT: int = Field(default=6369)
    REDIS_DB: int = Field(default=...)


APP_ENV = AppEnv()

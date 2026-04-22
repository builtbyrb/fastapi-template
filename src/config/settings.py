from enum import IntEnum, StrEnum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = (".env.prod", ".env.stag", ".env")


class Environment(StrEnum):
    DEV = "DEV"
    PROD = "PROD"
    STAG = "STAG"


class LogLevel(IntEnum):
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10


class BaseEnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )


class AppEnvSettings(BaseEnvSettings):
    ENVIRONMENT: Environment = Field(default=...)
    LOGGING_LEVEL: LogLevel = Field(default=...)
    DEFAULT_DEV_IP: str = Field(default="127.0.0.1")
    RESOLVE_IP_HEADER: str = Field(default="X-Real-Ip")

    POSTGRES_DRIVER_NAME: str = Field(default="postgresql+asyncpg")
    POSTGRES_HOST: str = Field(default=...)
    POSTGRES_PORT: int = Field(default=...)
    POSTGRES_USER: str = Field(default=...)
    POSTGRES_PASSWORD: str = Field(default=...)
    POSTGRES_DB: str = Field(default=...)

    PG_BOUNCER_HOST: str = Field(default=...)
    PG_BOUNCER_PORT: int = Field(default=...)

    REDIS_HOST: str = Field(default=...)
    REDIS_PORT: int = Field(default=...)
    REDIS_DB: int = Field(default=...)

    ENTRYPOINT_PORT: int = Field(default=...)


APP_ENV_SETTINGS = AppEnvSettings()

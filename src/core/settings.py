from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from src.core.constants import ENV_FILE, Environment
from src.core.logging.constants import LogLevel
from src.core.types.typings import ANY_IP_ADAPTER, IpAnyAddress


class BaseEnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )


class AppEnvSettings(BaseEnvSettings):
    ENVIRONMENT: Environment = Field(default=...)
    LOGGING_LEVEL: LogLevel = Field(default=...)
    DEFAULT_DEV_IP: IpAnyAddress = Field(
        default=ANY_IP_ADAPTER.validate_python("127.0.0.1")
    )
    RESOLVE_IP_HEADER: str = Field(default="X-Real-Ip")

    POSTGRES_DRIVER_NAME: str = Field(default="postgresql+asyncpg")
    POSTGRES_HOST: str = Field(default=...)
    POSTGRES_PORT: int = Field(default=...)
    POSTGRES_USER: str = Field(default=...)
    POSTGRES_PASSWORD: str = Field(default=...)
    POSTGRES_DB: str = Field(default=...)

    PG_BOUNCER_HOST: str = Field(default=...)
    PG_BOUNCER_PORT: int = Field(default=...)

    @property
    def postgres_database_url(self) -> URL:
        return URL.create(
            drivername=self.POSTGRES_DRIVER_NAME,
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        )

    @property
    def pgbouncer_database_url(self) -> URL:
        return URL.create(
            drivername=self.POSTGRES_DRIVER_NAME,
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.PG_BOUNCER_HOST,
            port=self.PG_BOUNCER_PORT,
            database=self.POSTGRES_DB,
        )

    REDIS_HOST: str = Field(default=...)
    REDIS_PORT: int = Field(default=...)
    REDIS_DB: int = Field(default=...)

    ENTRYPOINT_PORT: int = Field(default=...)


APP_ENV_SETTINGS = AppEnvSettings()

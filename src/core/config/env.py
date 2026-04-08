from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from src.core.constants import ENV_FILE, Environment
from src.core.logging.constants import LogLevel


class BaseEnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )


class AppEnv(BaseEnvSettings):
    ENVIRONMENT: Environment = Field(default=...)
    LOGGING_LEVEL: LogLevel = Field(default=...)

    POSTGRES_DRIVER_NAME: str = Field(default="postgresql+asyncpg")
    POSTGRES_USER: str = Field(default=...)
    POSTGRES_PASSWORD: str = Field(default=...)
    POSTGRES_DB: str = Field(default=...)
    PG_BOUNCER_HOST: str = Field(default=...)
    PG_BOUNCER_PORT: int = Field(default=5432)

    @property
    def postgres_database_url(self) -> str:
        return str(
            URL.create(
                drivername=self.POSTGRES_DRIVER_NAME,
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.PG_BOUNCER_HOST,
                port=self.PG_BOUNCER_PORT,
                database=self.POSTGRES_DB,
            ),
        )

    REDIS_HOST: str = Field(default=...)
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=...)

    ENTRYPOINT_PORT: int = Field(default=...)


APP_ENV = AppEnv()

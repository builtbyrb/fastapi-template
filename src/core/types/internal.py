from dataclasses import dataclass

import redis.asyncio as redis
from alembic.environment import Any
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


class LengthRuleData(BaseModel):
    MIN_LENGTH: int
    MAX_LENGTH: int


class CustomValidationRuleData(BaseModel):
    ERROR_CODE: str
    ERROR_MESSAGE: str
    ERROR_CONTEXT: dict[str, Any] | None = None


class CustomValidationRuleRegexData(CustomValidationRuleData):
    REGEX: str


@dataclass(frozen=True, kw_only=True)
class DatabaseProviders:
    session: AsyncSession
    client: redis.Redis

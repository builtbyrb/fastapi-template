from collections.abc import Mapping
from dataclasses import dataclass

import redis.asyncio as redis
from alembic.environment import Any
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.types.alias import Environment


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


@dataclass(frozen=True, kw_only=True)
class ResolveIpFromDataParams:
    environment: Environment
    default_dev_ip: str
    client_host: str | None
    headers: Mapping[str, str]
    resolve_ip_header: str

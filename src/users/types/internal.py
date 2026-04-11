import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic_core import Url
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils import get_utc_datetime
from src.users.constants import UserRole
from src.users.types.schemas import UserIdGetter


if TYPE_CHECKING:
    from src.users.types.interfaces import (
        UserRepoCreateUserPort,
        UserRepoDeleteUserPort,
        UserRepoUpdateUserPort,
    )
    from src.users.types.schemas import UserCreate, UserUpdate


# region -------------------------- General -------------------------
class UserUniqueFields(BaseModel):
    email: str | None = Field(default=None)
    username: str | None = Field(default=None)


@dataclass(frozen=True, kw_only=True)
class UserDupeFieldData:
    name: str
    value: str


# endregion


# region -------------------------- UserCreate -------------------------
@dataclass(frozen=True, kw_only=True)
class UserCreateServiceParams:
    session: AsyncSession
    user_repo: UserRepoCreateUserPort
    create: UserCreate


class UserCreateInternal(BaseModel):
    id: UUID = Field(default_factory=uuid.uuid4)

    role: UserRole = Field(default=UserRole.USER)
    login_notification: bool = Field(default=True)
    disabled: bool = Field(default=False)
    avatar_url: Url | None = Field(default=None)

    created_at: datetime = Field(default_factory=get_utc_datetime)
    updated_password_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)
    last_login_at: datetime | None = Field(default=None)


# endregion


@dataclass(frozen=True, kw_only=True)
class UserUpdateServiceParams:
    session: AsyncSession
    getter: UserIdGetter
    user_repo: UserRepoUpdateUserPort
    update: UserUpdate


@dataclass(frozen=True, kw_only=True)
class UserDeleteServiceParams:
    session: AsyncSession
    getter: UserIdGetter
    user_repo: UserRepoDeleteUserPort

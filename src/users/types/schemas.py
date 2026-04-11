import datetime
import uuid
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)
from pydantic_core import Url

from src.core.domain import get_utc_datetime
from src.users.constants import UserRole
from src.users.rules import (
    UserNoEmailRuleConfig,
    UserPasswordEmailRule,
)
from src.users.types.typings import (
    UserEmail,
    UserFirstName,
    UserLastName,
    UserPassword,
    UserUsername,
)


class UserBase(BaseModel):
    first_name: UserFirstName
    last_name: UserLastName
    username: UserUsername
    email: UserEmail

    @property
    def identifier(self) -> str:
        return self.email


class UserEmailGetter(BaseModel):
    email: UserEmail

    @property
    def identifier(self) -> str:
        return self.email


class UserUsernameGetter(BaseModel):
    username: UserUsername

    @property
    def identifier(self) -> str:
        return self.username


class UserIdGetter(BaseModel):
    id: uuid.UUID

    @property
    def identifier(self) -> str:
        return str(self.id)


class UserEmailPassword(UserNoEmailRuleConfig):
    email: UserEmail
    password: UserPassword = Field(exclude=True)


class UserCreate(UserBase, UserEmailPassword):
    @model_validator(mode="after")
    def validator(self) -> Self:
        return UserPasswordEmailRule[Self]().validator(self)


class UserUpdate(BaseModel):
    first_name: UserFirstName | None = Field(default=None)
    last_name: UserLastName | None = Field(default=None)
    username: UserUsername | None = Field(default=None)
    email: UserEmail | None = Field(default=None)
    avatar_url: Url | None = Field(default=None)
    login_notification: bool | None = Field(default=None)


class UserUpdateTimestamp(BaseModel):
    updated_at: datetime.datetime | None = Field(default_factory=get_utc_datetime)
    last_login_at: datetime.datetime | None = Field(default_factory=get_utc_datetime)
    updated_password_at: datetime.datetime | None = Field(
        default_factory=get_utc_datetime
    )


class UserUpdatePassword(UserEmailPassword):
    old_password: UserPassword

    @model_validator(mode="after")
    def validator(self) -> Self:
        validator: Self = UserPasswordEmailRule[Self]().validator(self)
        return validator


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime | None
    last_login_at: datetime.datetime | None
    updated_password_at: datetime.datetime | None
    login_notification: bool
    role: UserRole
    disabled: bool
    avatar_url: Url | None

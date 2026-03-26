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
from src.users.rules import USER_PASSWORD_EMAIL_RULE, UserNoEmailRuleConfig
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


class UserCreate(UserBase, UserNoEmailRuleConfig):
    password: UserPassword = Field(exclude=True)

    @model_validator(mode="after")
    def validator(self) -> Self:
        return USER_PASSWORD_EMAIL_RULE.validator(self)


class UserUpdate(UserNoEmailRuleConfig):
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


class UserUpdatePasswordInput(BaseModel):
    password: UserPassword
    new_password: UserPassword


class UserUpdatePassword(UserUpdatePasswordInput, UserNoEmailRuleConfig):
    email: UserEmail

    @model_validator(mode="after")
    def validator(self) -> Self:
        return USER_PASSWORD_EMAIL_RULE.validator(self)


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

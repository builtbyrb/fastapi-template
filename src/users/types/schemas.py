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

from src.core.domain.utils import get_utc_datetime, remove_email_domain
from src.core.domain.validators import contains_no_value
from src.core.rules import CustomValidationRule
from src.users.constants import USER_PASSWORD_EMAIL_RULE_DATA
from src.users.types.alias import UserRole
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


type UserGetter = UserEmailGetter | UserUsernameGetter | UserIdGetter


class UserEmailPassword(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"rules": [USER_PASSWORD_EMAIL_RULE_DATA.EXC_CODE]},
    )

    email: UserEmail
    password: UserPassword = Field(exclude=True)

    @model_validator(mode="after")
    def validator(self) -> Self:
        return CustomValidationRule[Self](
            data=USER_PASSWORD_EMAIL_RULE_DATA,
            predicate_fn=lambda val: contains_no_value(
                val.password, remove_email_domain(val.email)
            ),
        ).validator(self)


class UserCreate(UserBase, UserEmailPassword):
    pass


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

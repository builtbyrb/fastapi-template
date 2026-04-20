import datetime
import uuid
from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated, Self

from fastapi import Depends, Header
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    model_validator,
)
from pydantic_core import Url

from src.shared.date import get_utc_datetime
from src.shared.rules import (
    CustomValidationRule,
    CustomValidationRuleData,
    CustomValidationRuleRegex,
    CustomValidationRuleRegexData,
    LengthRuleData,
)
from src.shared.web import IpAnyAddress, UserAgent, get_client_ip


# region -------------------------- RequestInfoInput -------------------------
type UserAgentHeader = Annotated[
    UserAgent,
    Header(alias="User-Agent", description="User-Agent header from the client"),
]

IpDep = Annotated[IpAnyAddress, Depends(get_client_ip)]


@dataclass(frozen=True, kw_only=True)
class RequestInfo:
    ip: IpAnyAddress
    user_agent: UserAgent


class RequestInfoInput(BaseModel):
    ip: IpDep
    user_agent: UserAgentHeader


# endregion


# region -------------------------- NoSpace -------------------------
def contains_no_space(val: str) -> bool:
    return " " not in val


NO_SPACE_RULE_DATA = CustomValidationRuleData(
    EXC_CODE="no_space", EXC_MESSAGE="Must not contains space(s)"
)


NO_SPACE_RULE = CustomValidationRule(
    data=NO_SPACE_RULE_DATA, predicate_fn=contains_no_space
)


type NoSpaceStr = Annotated[
    str,
    Field(json_schema_extra={"rules": [NO_SPACE_RULE_DATA.EXC_CODE]}),
    AfterValidator(NO_SPACE_RULE.validator),
]

# endregion

# region -------------------------- UserFirstName -------------------------
USER_FIRST_NAME_LENGTH_RULE_DATA = LengthRuleData(MIN_LENGTH=3, MAX_LENGTH=30)

type UserFirstName = Annotated[
    NoSpaceStr,
    Field(
        min_length=USER_FIRST_NAME_LENGTH_RULE_DATA.MIN_LENGTH,
        max_length=USER_FIRST_NAME_LENGTH_RULE_DATA.MAX_LENGTH,
        description=(
            f"First name must be between "
            f"{USER_FIRST_NAME_LENGTH_RULE_DATA.MIN_LENGTH} "
            f"and {USER_FIRST_NAME_LENGTH_RULE_DATA.MAX_LENGTH} "
            "characters and contain no spaces"
        ),
    ),
]
# endregion

# region -------------------------- UserLastName -------------------------
USER_LAST_NAME_LENGTH_RULE_DATA = LengthRuleData(MIN_LENGTH=3, MAX_LENGTH=30)

type UserLastName = Annotated[
    NoSpaceStr,
    Field(
        min_length=USER_LAST_NAME_LENGTH_RULE_DATA.MIN_LENGTH,
        max_length=USER_LAST_NAME_LENGTH_RULE_DATA.MAX_LENGTH,
        description=(
            f"Last name must be between "
            f"{USER_LAST_NAME_LENGTH_RULE_DATA.MIN_LENGTH} "
            f"and {USER_LAST_NAME_LENGTH_RULE_DATA.MAX_LENGTH} "
            "characters and contain no spaces"
        ),
    ),
]
# endregion

# region -------------------------- UserEmail -------------------------
USER_EMAIL_LENGTH_RULE_DATA = LengthRuleData(MIN_LENGTH=6, MAX_LENGTH=40)

type UserEmail = Annotated[
    EmailStr,
    Field(
        max_length=USER_EMAIL_LENGTH_RULE_DATA.MAX_LENGTH,
        min_length=USER_EMAIL_LENGTH_RULE_DATA.MIN_LENGTH,
        description=(
            f"Email must be between {USER_EMAIL_LENGTH_RULE_DATA.MIN_LENGTH} "
            f"and {USER_EMAIL_LENGTH_RULE_DATA.MAX_LENGTH} characters "
            "follow a valid format"
        ),
    ),
]
# endregion

# region -------------------------- UserUsername -------------------------
USER_USERNAME_LENGTH_RULE_DATA = LengthRuleData(MIN_LENGTH=6, MAX_LENGTH=25)

type UserUsername = Annotated[
    NoSpaceStr,
    Field(
        max_length=USER_USERNAME_LENGTH_RULE_DATA.MAX_LENGTH,
        min_length=USER_USERNAME_LENGTH_RULE_DATA.MIN_LENGTH,
        description=(
            f"Username must be between {USER_USERNAME_LENGTH_RULE_DATA.MIN_LENGTH} "
            f"and {USER_USERNAME_LENGTH_RULE_DATA.MAX_LENGTH} "
            "characters and contain no spaces"
        ),
    ),
]

# endregion

# region -------------------------- UserPassword -------------------------
ONE_UPPERCASE_RULE_DATA = CustomValidationRuleRegexData(
    EXC_CODE="missing_uppercase",
    EXC_MESSAGE="Must contains one capital letter",
    REGEX=r"[A-Z]",
)

ONE_LOWERCASE_RULE_DATA = CustomValidationRuleRegexData(
    EXC_CODE="missing_lowercase",
    EXC_MESSAGE="Must contains one lowercase letter",
    REGEX=r"[a-z]",
)

ONE_DIGIT_RULE_DATA = CustomValidationRuleRegexData(
    EXC_CODE="missing_digit",
    EXC_MESSAGE="Must contains one number",
    REGEX=r"[0-9]",
)

ONE_SPECIAL_CHAR_RULE_DATA = CustomValidationRuleRegexData(
    EXC_CODE="missing_special_char",
    EXC_MESSAGE="Must contains one special char",
    REGEX=r"[#?!@$%^&*-]",
)

USER_PASSWORD_LENGTH_RULE_DATA = LengthRuleData(MIN_LENGTH=8, MAX_LENGTH=40)

ONE_UPPERCASE_RULE = CustomValidationRuleRegex(data=ONE_UPPERCASE_RULE_DATA)

ONE_LOWERCASE_RULE = CustomValidationRuleRegex(data=ONE_LOWERCASE_RULE_DATA)

ONE_DIGIT_RULE = CustomValidationRuleRegex(data=ONE_DIGIT_RULE_DATA)

ONE_SPECIAL_CHAR_RULE = CustomValidationRuleRegex(data=ONE_SPECIAL_CHAR_RULE_DATA)

type UserPassword = Annotated[
    NoSpaceStr,
    Field(
        max_length=USER_PASSWORD_LENGTH_RULE_DATA.MAX_LENGTH,
        min_length=USER_PASSWORD_LENGTH_RULE_DATA.MIN_LENGTH,
        description=(
            f"Password must be between {USER_PASSWORD_LENGTH_RULE_DATA.MIN_LENGTH} "
            f"and {USER_PASSWORD_LENGTH_RULE_DATA.MAX_LENGTH} characters, "
            "not contains your email address, "
            "contains one special char, contains one number, "
            "contains one lowercase letter, contains one capital letter"
        ),
        json_schema_extra={
            "rules": [
                NO_SPACE_RULE_DATA.EXC_CODE,
                ONE_UPPERCASE_RULE_DATA.EXC_CODE,
                ONE_LOWERCASE_RULE_DATA.EXC_CODE,
                ONE_DIGIT_RULE_DATA.EXC_CODE,
                ONE_SPECIAL_CHAR_RULE_DATA.EXC_CODE,
            ]
        },
    ),
    AfterValidator(ONE_UPPERCASE_RULE.validator),
    AfterValidator(ONE_LOWERCASE_RULE.validator),
    AfterValidator(ONE_DIGIT_RULE.validator),
    AfterValidator(ONE_SPECIAL_CHAR_RULE.validator),
]


def remove_email_domain(val: EmailStr) -> EmailStr:
    return val.split("@")[0]


def contains_no_value(search: str, val: str) -> bool:
    return search.lower() not in val.lower()


USER_PASSWORD_EMAIL_RULE_DATA = CustomValidationRuleData(
    EXC_CODE="contains_email", EXC_MESSAGE="Must not contains your email address"
)


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


# endregion


# region -------------------------- Getter -------------------------
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

# endregion


# region -------------------------- UserBase -------------------------
class UserBase(BaseModel):
    first_name: UserFirstName
    last_name: UserLastName
    username: UserUsername
    email: UserEmail

    @property
    def identifier(self) -> str:
        return self.email


# endregion


# region -------------------------- UserUpdate -------------------------
class UserUpdateTimestamp(BaseModel):
    updated_at: datetime.datetime | None = Field(default_factory=get_utc_datetime)
    last_login_at: datetime.datetime | None = Field(default_factory=get_utc_datetime)
    updated_password_at: datetime.datetime | None = Field(
        default_factory=get_utc_datetime
    )


# endregion


# region -------------------------- UserOut -------------------------
class UserRole(StrEnum):
    USER = "User"
    ADMIN = "Admin"


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


# endregion

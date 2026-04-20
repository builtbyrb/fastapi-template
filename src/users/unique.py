from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from src.users.exceptions import (
    UserException,
    UserExceptionContext,
)


if TYPE_CHECKING:
    pass


class UserAlreadyExistsExceptionContext(UserExceptionContext):
    field: str
    value: str


class UserAlreadyExistsException(UserException):
    def __init__(self, context: UserAlreadyExistsExceptionContext) -> None:
        super().__init__(
            message=f"User {context.value} already exists", context=context
        )


@dataclass(frozen=True, kw_only=True)
class UserDupeFieldData:
    name: str
    value: str


class RequiredUserUniqueFields(BaseModel):
    email: str
    username: str


class OptionalUserUniqueFields(BaseModel):
    email: str | None = Field(default=None)
    username: str | None = Field(default=None)


type UserUniqueFields = RequiredUserUniqueFields | OptionalUserUniqueFields


def find_user_dupe_field(
    user_unique_fields: UserUniqueFields,
    unique_fields: UserUniqueFields,
) -> list[UserDupeFieldData]:
    return [
        UserDupeFieldData(name=key, value=value)
        for key, value in unique_fields.model_dump(exclude_none=True).items()
        if getattr(user_unique_fields, key) == value
    ]


def validate_user_unique_fields(
    user_unique_fields: RequiredUserUniqueFields | None,
    unique_fields: UserUniqueFields,
) -> None:
    if not user_unique_fields:
        return

    dupe_fields = find_user_dupe_field(user_unique_fields, unique_fields)

    if dupe_fields:
        dupe_field = dupe_fields[0]
        raise UserAlreadyExistsException(
            UserAlreadyExistsExceptionContext(
                user=user_unique_fields.email,
                field=dupe_field.name,
                value=dupe_field.value,
            )
        )

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from src.users.exceptions import (
    UserException,
    UserExceptionContext,
)


if TYPE_CHECKING:
    from src.users.storage import User


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


class UserUniqueFields(BaseModel):
    email: str | None = Field(default=None)
    username: str | None = Field(default=None)


def find_user_dupe_field(
    user: User, unique_fields: UserUniqueFields
) -> list[UserDupeFieldData]:
    return [
        UserDupeFieldData(name=key, value=value)
        for key, value in unique_fields.model_dump(exclude_none=True).items()
        if getattr(user, key) == value
    ]


def validate_user_unique_fields(
    user: User | None, unique_fields: UserUniqueFields
) -> None:
    if not user:
        return

    dupe_fields = find_user_dupe_field(user, unique_fields)

    if dupe_fields:
        dupe_field = dupe_fields[0]
        raise UserAlreadyExistsException(
            UserAlreadyExistsExceptionContext(
                user=user.identifier, field=dupe_field.name, value=dupe_field.value
            )
        )

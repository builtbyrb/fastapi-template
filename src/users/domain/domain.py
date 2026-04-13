from typing import TYPE_CHECKING, Any

from src.auth.domain.security import hash_password
from src.users.domain.exceptions import (
    UserAlreadyExistsException,
    UserTooManyRefreshTokenException,
)
from src.users.types.internal import (
    UserCreateInternal,
    UserDupeFieldData,
    UserUniqueFields,
)
from src.users.types.schemas import (
    UserCreate,
    UserUpdate,
    UserUpdateTimestamp,
)


if TYPE_CHECKING:
    from src.users.models import User


def create_user_dict(create: UserCreate) -> dict[str, Any]:
    return {
        **create.model_dump(),
        **UserCreateInternal().model_dump(),
        "password_hash": hash_password(create.password),
    }


def update_user_dict(update: UserUpdate) -> dict[str, Any]:
    update_timestamp_dict = UserUpdateTimestamp(
        last_login_at=None, updated_password_at=None
    ).model_dump(exclude_none=True)
    update_dict = update.model_dump(exclude_unset=True)
    return {
        **update_timestamp_dict,
        **update_dict,
    }


def update_user_password_dict(new_password: str) -> dict[str, Any]:
    password_hash = hash_password(new_password)
    update_timestamp_dict = UserUpdateTimestamp(last_login_at=None).model_dump(
        exclude_none=True
    )
    return {"password_hash": password_hash, **update_timestamp_dict}


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
            user.identifier, dupe_field.name, dupe_field.value
        )


def verify_user_token_limit(user: User, token_limit: int) -> None:
    if len(user.refresh_tokens) >= token_limit:
        raise UserTooManyRefreshTokenException(user.identifier)

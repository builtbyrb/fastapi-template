# region -------------------------- Types -------------------------
from typing import Any, Protocol

from src.shared.security import hash_password
from src.users.storage import User
from src.users.validations import (
    UserEmailPassword,
    UserIdGetter,
    UserPassword,
    UserUpdateTimestamp,
)


class UserUpdatePasswordPort(Protocol):
    async def update_user_password(
        self, sql_session: Any, getter: UserIdGetter, values: dict[str, Any]
    ) -> User: ...


class UserUpdatePassword(UserEmailPassword):
    old_password: UserPassword


def update_user_password_dict(new_password: str) -> dict[str, Any]:
    password_hash = hash_password(new_password)
    update_timestamp_dict = UserUpdateTimestamp(last_login_at=None).model_dump(
        exclude_none=True
    )
    return {"password_hash": password_hash, **update_timestamp_dict}

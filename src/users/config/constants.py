from typing import Any

from pydantic import BaseModel

from src.core.domain import enum_do_dict
from src.users.constants import UserRole


class UserConstants(BaseModel):
    USER_ROLE: dict[str, Any] = enum_do_dict(UserRole)


USER_CONSTANTS = UserConstants()

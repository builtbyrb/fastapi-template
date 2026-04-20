from pydantic import BaseModel

from src.shared.exceptions import (
    AppException,
)


# region -------------------------- Exception -------------------------
class UserException(AppException):
    pass


class UserExceptionContext(BaseModel):
    user: str


# endregion

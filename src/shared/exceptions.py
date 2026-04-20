from pydantic import BaseModel


class AppException(Exception):
    def __init__(self, *, message: str, context: BaseModel | None = None) -> None:
        self.message = message
        self.context = context
        super().__init__(self.message)

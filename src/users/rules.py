from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict


if TYPE_CHECKING:
    from src.users.types.schemas import UserEmailPassword

from src.core.rules import CustomValidationRule
from src.core.validators import contains_value
from src.users.constants import USER_PASSWORD_EMAIL_RULE_DATA


class UserPasswordEmailRule[T: UserEmailPassword](CustomValidationRule[T]):
    def __init__(
        self,
    ) -> None:
        super().__init__(USER_PASSWORD_EMAIL_RULE_DATA, self.predicate_fn)

    def predicate_fn(self, val: T) -> bool:
        return contains_value(val.password, val.email)


class UserNoEmailRuleConfig(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"rules": [USER_PASSWORD_EMAIL_RULE_DATA.ERROR_CODE]},
    )

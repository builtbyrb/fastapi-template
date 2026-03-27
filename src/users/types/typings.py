from typing import Annotated

from pydantic import (
    AfterValidator,
    EmailStr,
    Field,
)

from src.core.rules.rules import (
    NO_SPACE_RULE,
    ONE_LOWERCASE_RULE,
    ONE_NUMBER_RULE,
    ONE_SPECIAL_CHAR_RULE,
    ONE_UPPERCASE_RULE,
)
from src.core.types.typings import NoSpaceStr
from src.users.rules import (
    USER_EMAIL_MIN_MAX_RULE,
    USER_FIRST_NAME_MIN_MAX_RULE,
    USER_LAST_NAME_MIN_MAX_RULE,
    USER_PASSWORD_MIN_MAX_RULE,
    USER_USERNAME_MIN_MAX_RULE,
)


type UserFirstName = Annotated[
    NoSpaceStr,
    Field(
        min_length=USER_FIRST_NAME_MIN_MAX_RULE.MIN_LENGTH,
        max_length=USER_FIRST_NAME_MIN_MAX_RULE.MAX_LENGTH,
        description=(
            f"First name must be between {USER_FIRST_NAME_MIN_MAX_RULE.MIN_LENGTH} "
            f"and {USER_FIRST_NAME_MIN_MAX_RULE.MAX_LENGTH} "
            "characters and contain no spaces"
        ),
    ),
]

type UserLastName = Annotated[
    NoSpaceStr,
    Field(
        min_length=USER_LAST_NAME_MIN_MAX_RULE.MIN_LENGTH,
        max_length=USER_LAST_NAME_MIN_MAX_RULE.MAX_LENGTH,
        description=(
            f"Last name must be between {USER_LAST_NAME_MIN_MAX_RULE.MIN_LENGTH} "
            f"and {USER_LAST_NAME_MIN_MAX_RULE.MAX_LENGTH} "
            "characters and contain no spaces"
        ),
    ),
]

type UserUsername = Annotated[
    NoSpaceStr,
    Field(
        max_length=USER_USERNAME_MIN_MAX_RULE.MAX_LENGTH,
        min_length=USER_USERNAME_MIN_MAX_RULE.MIN_LENGTH,
        description=(
            f"Username must be between {USER_USERNAME_MIN_MAX_RULE.MIN_LENGTH} "
            f"and {USER_USERNAME_MIN_MAX_RULE.MAX_LENGTH} "
            "characters and contain no spaces"
        ),
    ),
]

type UserEmail = Annotated[
    EmailStr,
    Field(
        max_length=USER_EMAIL_MIN_MAX_RULE.MAX_LENGTH,
        min_length=USER_EMAIL_MIN_MAX_RULE.MIN_LENGTH,
        description=(
            f"Email must be between {USER_EMAIL_MIN_MAX_RULE.MIN_LENGTH} "
            f"and {USER_EMAIL_MIN_MAX_RULE.MAX_LENGTH} characters "
            "follow a valid format"
        ),
    ),
]

type UserPassword = Annotated[
    NoSpaceStr,
    Field(
        max_length=USER_PASSWORD_MIN_MAX_RULE.MAX_LENGTH,
        min_length=USER_PASSWORD_MIN_MAX_RULE.MIN_LENGTH,
        description=(
            f"Password must be between {USER_PASSWORD_MIN_MAX_RULE.MIN_LENGTH} "
            f"and {USER_PASSWORD_MIN_MAX_RULE.MAX_LENGTH} characters, "
            "not contains your email address, "
            "contains one special char, contains one number, "
            "contains one lowercase letter, contains one capital letter"
        ),
        json_schema_extra={
            "rules": [
                NO_SPACE_RULE.ERROR_CODE,
                ONE_UPPERCASE_RULE.ERROR_CODE,
                ONE_LOWERCASE_RULE.ERROR_CODE,
                ONE_NUMBER_RULE.ERROR_CODE,
                ONE_SPECIAL_CHAR_RULE.ERROR_CODE,
            ]
        },
    ),
    AfterValidator(ONE_UPPERCASE_RULE.validator),
    AfterValidator(ONE_LOWERCASE_RULE.validator),
    AfterValidator(ONE_NUMBER_RULE.validator),
    AfterValidator(ONE_SPECIAL_CHAR_RULE.validator),
]

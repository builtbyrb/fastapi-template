from typing import Annotated

from pydantic import (
    AfterValidator,
    EmailStr,
    Field,
)

from src.core.constants import (
    NO_SPACE_RULE_DATA,
    ONE_DIGIT_RULE,
    ONE_DIGIT_RULE_DATA,
    ONE_LOWERCASE_RULE,
    ONE_LOWERCASE_RULE_DATA,
    ONE_SPECIAL_CHAR_RULE,
    ONE_SPECIAL_CHAR_RULE_DATA,
    ONE_UPPERCASE_RULE,
    ONE_UPPERCASE_RULE_DATA,
)
from src.core.types.typings import (
    NoSpaceStr,
)
from src.users.constants import (
    USER_EMAIL_LENGTH_RULE_DATA,
    USER_FIRST_NAME_LENGTH_RULE_DATA,
    USER_LAST_NAME_LENGTH_RULE_DATA,
    USER_PASSWORD_LENGTH_RULE_DATA,
    USER_USERNAME_LENGTH_RULE_DATA,
)


type UserFirstName = Annotated[
    NoSpaceStr,
    Field(
        min_length=USER_FIRST_NAME_LENGTH_RULE_DATA.MIN_LENGTH,
        max_length=USER_FIRST_NAME_LENGTH_RULE_DATA.MAX_LENGTH,
        description=(
            f"First name must be between {USER_FIRST_NAME_LENGTH_RULE_DATA.MIN_LENGTH} "
            f"and {USER_FIRST_NAME_LENGTH_RULE_DATA.MAX_LENGTH} "
            "characters and contain no spaces"
        ),
    ),
]

type UserLastName = Annotated[
    NoSpaceStr,
    Field(
        min_length=USER_LAST_NAME_LENGTH_RULE_DATA.MIN_LENGTH,
        max_length=USER_LAST_NAME_LENGTH_RULE_DATA.MAX_LENGTH,
        description=(
            f"Last name must be between {USER_LAST_NAME_LENGTH_RULE_DATA.MIN_LENGTH} "
            f"and {USER_LAST_NAME_LENGTH_RULE_DATA.MAX_LENGTH} "
            "characters and contain no spaces"
        ),
    ),
]

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
                NO_SPACE_RULE_DATA.ERROR_CODE,
                ONE_UPPERCASE_RULE_DATA.ERROR_CODE,
                ONE_LOWERCASE_RULE_DATA.ERROR_CODE,
                ONE_DIGIT_RULE_DATA.ERROR_CODE,
                ONE_SPECIAL_CHAR_RULE_DATA.ERROR_CODE,
            ]
        },
    ),
    AfterValidator(ONE_UPPERCASE_RULE.validator),
    AfterValidator(ONE_LOWERCASE_RULE.validator),
    AfterValidator(ONE_DIGIT_RULE.validator),
    AfterValidator(ONE_SPECIAL_CHAR_RULE.validator),
]

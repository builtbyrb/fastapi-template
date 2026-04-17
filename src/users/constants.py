from fastapi import status

from src.core.types.internal import (
    CustomValidationRuleData,
    HTTPExceptionData,
    LengthRuleData,
)
from src.users.types.internal import (
    UserAlreadyExistsExceptionDetailsContext,
    UserExceptionDetailsContext,
)


# region -------------------------- Rules -------------------------
USER_FIRST_NAME_LENGTH_RULE_DATA = LengthRuleData(MIN_LENGTH=3, MAX_LENGTH=30)

USER_LAST_NAME_LENGTH_RULE_DATA = LengthRuleData(MIN_LENGTH=3, MAX_LENGTH=30)

USER_EMAIL_LENGTH_RULE_DATA = LengthRuleData(MIN_LENGTH=6, MAX_LENGTH=40)

USER_USERNAME_LENGTH_RULE_DATA = LengthRuleData(MIN_LENGTH=6, MAX_LENGTH=25)

USER_PASSWORD_LENGTH_RULE_DATA = LengthRuleData(MIN_LENGTH=8, MAX_LENGTH=40)
USER_PASSWORD_EMAIL_RULE_DATA = CustomValidationRuleData(
    EXC_CODE="contains_email", EXC_MESSAGE="Must not contains your email address"
)
# endregion

# region -------------------------- HTTPExceptionData -------------------------
USER_ALREADY_EXISTS_EXC_DATA = HTTPExceptionData(
    exc_code="users/already-exists",
    status_code=status.HTTP_409_CONFLICT,
    description="User already exists",
    context_model=UserAlreadyExistsExceptionDetailsContext,
)

USER_NOT_FOUND_EXC_DATA = HTTPExceptionData(
    exc_code="users/not-found",
    status_code=status.HTTP_404_NOT_FOUND,
    description="User not found",
    context_model=UserExceptionDetailsContext,
)

USER_TOO_MANY_REFRESH_TOKEN_EXC_DATA = HTTPExceptionData(
    exc_code="users/too-many-token",
    status_code=status.HTTP_400_BAD_REQUEST,
    description="Too much refresh token",
    context_model=UserExceptionDetailsContext,
)
# endregion

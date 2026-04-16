from typing import TYPE_CHECKING

import structlog
from fastapi import status

from src.core.domain.validators import contains_no_space, is_valid_ua
from src.core.logging.processors import drop_color_message_key
from src.core.rules import CustomValidationRule, CustomValidationRuleRegex
from src.core.types.internal import (
    CustomValidationRuleData,
    CustomValidationRuleRegexData,
    HTTPExceptionData,
    ResourceNotInitializedDetailsContext,
)


if TYPE_CHECKING:
    from structlog.typing import Processor


# region -------------------------- Rules -------------------------
USER_AGENT_FORMAT_RULE_DATA = CustomValidationRuleData(
    ERROR_CODE="invalid_user_agent_format", ERROR_MESSAGE="Invalid User-Agent format"
)

NO_SPACE_RULE_DATA = CustomValidationRuleData(
    ERROR_CODE="no_space", ERROR_MESSAGE="Must not contains space(s)"
)


ONE_UPPERCASE_RULE_DATA = CustomValidationRuleRegexData(
    ERROR_CODE="missing_uppercase",
    ERROR_MESSAGE="Must contains one capital letter",
    REGEX=r"[A-Z]",
)

ONE_LOWERCASE_RULE_DATA = CustomValidationRuleRegexData(
    ERROR_CODE="missing_lowercase",
    ERROR_MESSAGE="Must contains one lowercase letter",
    REGEX=r"[a-z]",
)

ONE_DIGIT_RULE_DATA = CustomValidationRuleRegexData(
    ERROR_CODE="missing_digit",
    ERROR_MESSAGE="Must contains one number",
    REGEX=r"[0-9]",
)

ONE_SPECIAL_CHAR_RULE_DATA = CustomValidationRuleRegexData(
    ERROR_CODE="missing_special_char",
    ERROR_MESSAGE="Must contains one special char",
    REGEX=r"[#?!@$%^&*-]",
)

USER_AGENT_FORMAT_RULE = CustomValidationRule(
    data=USER_AGENT_FORMAT_RULE_DATA, predicate_fn=is_valid_ua
)
NO_SPACE_RULE = CustomValidationRule(
    data=NO_SPACE_RULE_DATA, predicate_fn=contains_no_space
)

ONE_UPPERCASE_RULE = CustomValidationRuleRegex(data=ONE_UPPERCASE_RULE_DATA)

ONE_LOWERCASE_RULE = CustomValidationRuleRegex(data=ONE_LOWERCASE_RULE_DATA)

ONE_DIGIT_RULE = CustomValidationRuleRegex(data=ONE_DIGIT_RULE_DATA)

ONE_SPECIAL_CHAR_RULE = CustomValidationRuleRegex(data=ONE_SPECIAL_CHAR_RULE_DATA)

# endregion

# region -------------------------- HTTPExceptionData -------------------------
CLIENT_IP_NOT_FOUND_EXC_DATA = HTTPExceptionData(
    exc_code="ip-not-found",
    status_code=status.HTTP_404_NOT_FOUND,
    description="Client ip not found",
)

RESOURCE_NOT_INITIALIZED_EXC_DATA = HTTPExceptionData(
    exc_code="resource-not-initialized",
    status_code=status.HTTP_400_BAD_REQUEST,
    description="resource in the code was not initialized",
    context_model=ResourceNotInitializedDetailsContext,
)
# endregion

# region -------------------------- Logging -------------------------
FOREIGN_PRE_CHAIN: list[Processor] = [
    structlog.stdlib.ExtraAdder(),
]

PRE_CHAIN: list[Processor] = [
    structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
]
SHARED_PRE_CHAIN: list[Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
    structlog.processors.StackInfoRenderer(),
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.CallsiteParameterAdder(
        [
            structlog.processors.CallsiteParameter.FUNC_NAME,
            structlog.processors.CallsiteParameter.FILENAME,
            structlog.processors.CallsiteParameter.LINENO,
        ]
    ),
]

_SHARED_CHAIN: list[Processor] = [
    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
]

DEV_CHAIN: list[Processor] = [*_SHARED_CHAIN, structlog.dev.ConsoleRenderer()]
PROD_CHAIN: list[Processor] = [
    *_SHARED_CHAIN,
    structlog.processors.dict_tracebacks,
    drop_color_message_key,
    structlog.processors.EventRenamer("msg"),
    structlog.processors.JSONRenderer(),
]

LOGGERS_TO_CLEAR = [
    "uvicorn",
    "uvicorn.error",
    "uvicorn.asgi",
    "sqlalchemy.engine",
    "alembic",
]

# endregion
ENV_FILE = (".env.prod", ".env.stag", ".env")

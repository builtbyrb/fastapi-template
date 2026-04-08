from enum import IntEnum

import structlog
from structlog.typing import Processor

from src.core.logging.processors import drop_color_message_key


# region -------------------------- PreChain -------------------------
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
# endregion


# region -------------------------- Chain -------------------------
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
# endregion

# region -------------------------- Other -------------------------
LOGGERS_TO_CLEAR = [
    "uvicorn",
    "uvicorn.error",
    "uvicorn.asgi",
    "sqlalchemy.engine",
    "alembic",
]


class LogLevel(IntEnum):
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10


# endregion

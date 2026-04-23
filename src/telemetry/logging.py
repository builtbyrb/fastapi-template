import asyncio
import logging
import sys
from types import TracebackType

import structlog
from structlog.typing import EventDict, Processor, WrappedLogger

from src.config.settings import APP_ENV_SETTINGS, Environment


def drop_color_message_key(
    _: WrappedLogger, __: str, event_dict: EventDict
) -> EventDict:
    event_dict.pop("color_message", None)
    return event_dict


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

CHAIN = DEV_CHAIN if APP_ENV_SETTINGS.ENVIRONMENT == Environment.DEV else PROD_CHAIN

FORMATTER = structlog.stdlib.ProcessorFormatter(
    foreign_pre_chain=[*SHARED_PRE_CHAIN, *FOREIGN_PRE_CHAIN],
    processors=CHAIN,
)

LOGGERS_TO_CLEAR = [
    "uvicorn",
    "uvicorn.error",
    "uvicorn.asgi",
    "sqlalchemy.engine",
    "alembic",
]


def clear_logger_handler(loggers: list[str]) -> None:
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True


def config_logging(formatter: logging.Formatter) -> None:
    structlog.configure(
        processors=[*SHARED_PRE_CHAIN, *PRE_CHAIN],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(APP_ENV_SETTINGS.LOGGING_LEVEL.value)


def handle_uncaught_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType | None,
) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.getLogger("system.uncaught").critical(
        "Sync uncaught exception",
        extra={"type": "sync_uncaught_exception"},
        exc_info=(exc_type, exc_value, exc_traceback),
    )


def handle_async_uncaught_exception(
    _loop: asyncio.AbstractEventLoop, context: dict
) -> None:
    message = context["message"]
    exception = context.get("exception")

    logging.getLogger("system.async.uncaught").critical(
        "Async uncaught exception",
        extra={"type": "async_uncaught_exception", "async_msg": message},
        exc_info=exception,
    )


def setup_sync_uncaught_exception_handler() -> None:
    sys.excepthook = handle_uncaught_exception


def setup_async_uncaught_exception_handler() -> None:
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_async_uncaught_exception)


def setup_logging() -> None:
    setup_sync_uncaught_exception_handler()
    setup_async_uncaught_exception_handler()
    clear_logger_handler(LOGGERS_TO_CLEAR)
    config_logging(FORMATTER)

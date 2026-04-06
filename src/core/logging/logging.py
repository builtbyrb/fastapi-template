import logging

import structlog

from src.core.constants import Environment
from src.core.config.env import APP_ENV
from src.core.logging.constants import (
    DEV_CHAIN,
    FOREIGN_PRE_CHAIN,
    LOGGERS_TO_CLEAR,
    PRE_CHAIN,
    PROD_CHAIN,
    SHARED_PRE_CHAIN,
)


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
    root_logger.setLevel(APP_ENV.LOGGING_LEVEL.value)


def setup_logging() -> None:
    chain = DEV_CHAIN if APP_ENV.ENVIRONMENT == Environment.DEV else PROD_CHAIN

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[*SHARED_PRE_CHAIN, *FOREIGN_PRE_CHAIN],
        processors=chain,
    )

    clear_logger_handler(LOGGERS_TO_CLEAR)
    config_logging(formatter)

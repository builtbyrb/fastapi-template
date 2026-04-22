from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

from src.database.database import (
    PG_BOUNCER_URL,
    REDIS_URL,
    CreateRedisUrlParams,
    CreateSqlalchemyUrlParams,
    RedisManager,
    SqlDatabaseManager,
    create_redis_url,
    create_sqlalchemy_url,
)
from src.health.features.health_check import (
    Health,
    HealthValues,
    bool_to_health,
    check_redis_connectivity,
    check_sql_db_connectivity,
)


HEALTH_ARG_NAMES = ("status", "expected_value")
HEALTH_ARG_VALUES = [(False, "unhealthy"), (True, "healthy")]
HEALTH_ARG_IDS = ["unhealthy_when_false", "healthy_when_true"]


@pytest.mark.parametrize(
    HEALTH_ARG_NAMES,
    HEALTH_ARG_VALUES,
    ids=HEALTH_ARG_IDS,
)
def test_bool_to_health_returns_expected_value(
    *, status: bool, expected_value: HealthValues
) -> None:
    assert bool_to_health(status=status) == expected_value


HEALTH_ADAPTER = TypeAdapter[Health](Health)


@pytest.mark.parametrize(
    HEALTH_ARG_NAMES,
    HEALTH_ARG_VALUES,
    ids=HEALTH_ARG_IDS,
)
def test_health_type_returns_expected_value(
    *, status: bool, expected_value: HealthValues
) -> None:
    assert HEALTH_ADAPTER.validate_python(status) == expected_value


@pytest.mark.parametrize(
    ("value", "expected_exception"),
    [("test", ValidationError), (2, ValidationError)],
    ids=[
        "raises_validation_error_when_string_value",
        "raises_validation_error_when_number_value",
    ],
)
def test_health_type_raises_expected_exception(
    value: Any, expected_exception: type[Exception]
) -> None:
    with pytest.raises(expected_exception):
        HEALTH_ADAPTER.validate_python(value)


@pytest.mark.parametrize(
    ("init", "url", "expected_value"),
    [
        (
            False,
            REDIS_URL,
            False,
        ),
        (True, create_redis_url(CreateRedisUrlParams(redis_port=12)), False),
        (True, REDIS_URL, True),
    ],
    ids=[
        "false_when_not_init",
        "false_when_init_but_connection_failed",
        "true_when_init_and_connection_success",
    ],
)
@pytest.mark.asyncio
async def test_check_redis_con_returns_expected_value(
    *, init: bool, url: str, expected_value: bool
) -> None:
    redis_manager = RedisManager(
        url,
        client_kwargs={
            "protocol": 3,
            "socket_timeout": 1,
            "socket_connect_timeout": 1,
            "retry_on_timeout": False,
        },
    )
    if init:
        await redis_manager.init()
    assert await check_redis_connectivity(redis_manager) == expected_value
    if init:
        await redis_manager.close()


@pytest.mark.parametrize(
    ("init", "url", "expected_value"),
    [
        (False, PG_BOUNCER_URL, False),
        (True, create_sqlalchemy_url(CreateSqlalchemyUrlParams(port=12)), False),
        (True, PG_BOUNCER_URL, True),
    ],
    ids=[
        "false_when_not_init",
        "false_when_init_but_connection_failed",
        "true_when_init_and_connection_success",
    ],
)
@pytest.mark.asyncio
async def test_check_sql_db_con_returns_expected_value(
    *, init: bool, url: str, expected_value: bool
) -> None:
    sql_database_manager = SqlDatabaseManager(
        url,
        engine_kwargs={
            "pool_size": 50,
            "max_overflow": 20,
            "pool_timeout": 30,
            "pool_recycle": 1800,
            "pool_pre_ping": True,
        },
    )
    if init:
        await sql_database_manager.init()
    assert await check_sql_db_connectivity(sql_database_manager) == expected_value
    if init:
        await sql_database_manager.close()

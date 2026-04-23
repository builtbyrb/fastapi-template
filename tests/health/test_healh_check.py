from typing import Any

import pytest
from httpx import AsyncClient
from pydantic import TypeAdapter, ValidationError

from src.database.database import (
    PG_BOUNCER_URL,
    REDIS_MANGER,
    REDIS_URL,
    SQL_DATABASE_MANGER,
    CreateRedisUrlParams,
    CreateSqlalchemyUrlParams,
    create_redis_url,
    create_sqlalchemy_url,
)
from src.health.features.health_check import (
    Health,
    HealthStatus,
    HealthValues,
    bool_to_health,
    check_redis_connectivity,
    check_sql_db_connectivity,
)


HEALTH_ARG_NAMES = ("status", "expected_health_value")
HEALTH_ARG_VALUES = [(False, "unhealthy"), (True, "healthy")]
HEALTH_ARG_IDS = ["unhealthy_when_false", "healthy_when_true"]
BAD_REDIS_URL = create_redis_url(CreateRedisUrlParams(redis_port=12))
BAD_SQL_URL = create_sqlalchemy_url(CreateSqlalchemyUrlParams(port=12))


@pytest.mark.parametrize(
    HEALTH_ARG_NAMES,
    HEALTH_ARG_VALUES,
    ids=HEALTH_ARG_IDS,
)
def test_bool_to_health_returns_expected_health_value(
    *, status: bool, expected_health_value: HealthValues
) -> None:
    assert bool_to_health(status=status) == expected_health_value


HEALTH_ADAPTER = TypeAdapter[Health](Health)


@pytest.mark.parametrize(
    HEALTH_ARG_NAMES,
    HEALTH_ARG_VALUES,
    ids=HEALTH_ARG_IDS,
)
def test_health_type_returns_expected_health_value(
    *, status: bool, expected_health_value: HealthValues
) -> None:
    assert HEALTH_ADAPTER.validate_python(status) == expected_health_value


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
    ("init", "url", "expected_bool"),
    [
        (
            False,
            REDIS_URL,
            False,
        ),
        (True, BAD_REDIS_URL, False),
        (True, REDIS_URL, True),
    ],
    ids=[
        "false_when_not_init",
        "false_when_init_but_connection_failed",
        "true_when_init_and_connection_success",
    ],
)
@pytest.mark.asyncio
async def test_check_redis_con_returns_expected_bool(
    *, init: bool, url: str, expected_bool: bool
) -> None:
    REDIS_MANGER.url = url
    if init:
        await REDIS_MANGER.init()
    assert await check_redis_connectivity(REDIS_MANGER) == expected_bool
    if init:
        await REDIS_MANGER.close()


@pytest.mark.parametrize(
    ("init", "url", "expected_bool"),
    [
        (False, PG_BOUNCER_URL, False),
        (True, BAD_SQL_URL, False),
        (True, PG_BOUNCER_URL, True),
    ],
    ids=[
        "false_when_not_init",
        "false_when_init_but_connection_failed",
        "true_when_init_and_connection_success",
    ],
)
@pytest.mark.asyncio
async def test_check_sql_db_con_returns_expected_bool(
    *, init: bool, url: str, expected_bool: bool
) -> None:
    SQL_DATABASE_MANGER.url = url
    if init:
        await SQL_DATABASE_MANGER.init()
    assert await check_sql_db_connectivity(SQL_DATABASE_MANGER) == expected_bool
    if init:
        await SQL_DATABASE_MANGER.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "redis_url",
        "sql_url",
        "expected_payload",
        "expected_status_code",
    ),
    [
        (
            REDIS_URL,
            PG_BOUNCER_URL,
            HealthStatus(
                sql_db_health="healthy", redis_health="healthy", health="healthy"
            ),
            200,
        ),
        (
            BAD_REDIS_URL,
            PG_BOUNCER_URL,
            HealthStatus(
                sql_db_health="healthy", redis_health="unhealthy", health="unhealthy"
            ),
            503,
        ),
        (
            BAD_REDIS_URL,
            BAD_SQL_URL,
            HealthStatus(
                sql_db_health="unhealthy",
                redis_health="unhealthy",
                health="unhealthy",
            ),
            503,
        ),
    ],
    ids=[
        "healthy_200_when_all_service_functional",
        "unhealthy_503_when_one_service_fails",
        "unhealthy_503_when_all_services_fail",
    ],
)
async def test_health_route_returns_expected_payload_and_status_code(
    client: AsyncClient,
    redis_url: str,
    sql_url: str,
    expected_payload: HealthStatus,
    expected_status_code: int,
) -> None:
    REDIS_MANGER.url = redis_url
    SQL_DATABASE_MANGER.url = sql_url
    await REDIS_MANGER.init()
    await SQL_DATABASE_MANGER.init()
    response = await client.get("/health/")
    assert HealthStatus.model_validate(response.json()) == expected_payload
    assert response.status_code == expected_status_code

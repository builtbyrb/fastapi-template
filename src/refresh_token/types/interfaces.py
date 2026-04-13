from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Protocol

from src.refresh_token.models import RefreshToken


if TYPE_CHECKING:
    from src.refresh_token.types.schemas import (
        RefreshTokenJtiGetter,
        RefreshTokenUserIdGetter,
    )


class RefreshTokenReadByJtiPort(Protocol):
    async def get_by_jti(
        self, sql_session: Any, getter: RefreshTokenJtiGetter
    ) -> RefreshToken: ...


class RefreshTokenReadByUserIdPort(Protocol):
    async def get_by_user_id(
        self, sql_session: Any, getter: RefreshTokenUserIdGetter
    ) -> Sequence[RefreshToken]: ...


class RefreshTokenInsertPort(Protocol):
    async def insert_refresh_token(
        self, sql_session: Any, values: dict[str, Any]
    ) -> RefreshToken: ...


class RefreshTokenUpdatePort(Protocol):
    async def update_refresh_token(
        self, sql_session: Any, getter: RefreshTokenJtiGetter, values: dict[str, Any]
    ) -> RefreshToken: ...


class RefreshTokenDeletePort(Protocol):
    async def delete_refresh_token(
        self, sql_session: Any, getter: RefreshTokenJtiGetter
    ) -> RefreshToken: ...


class RefreshTokenDeleteAllByUserIdPort(Protocol):
    async def delete_all_refresh_token_by_user_id(
        self, sql_session: Any, getter: RefreshTokenUserIdGetter
    ) -> list[RefreshToken]: ...

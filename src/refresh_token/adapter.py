from typing import TYPE_CHECKING, Any

from sqlalchemy import delete, insert, select, update

from src.refresh_token.domain.exceptions import RefreshTokenNotFoundException
from src.refresh_token.models import RefreshToken
from src.refresh_token.types.schemas import (
    RefreshTokenJtiGetter,
    RefreshTokenUserIdGetter,
)


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyRefreshTokenRepo:
    @staticmethod
    async def get_by_jti(
        sql_session: AsyncSession, getter: RefreshTokenJtiGetter
    ) -> RefreshToken:
        stmt = select(RefreshToken).where(RefreshToken.jti == getter.jti)
        result = await sql_session.scalar(stmt)
        if not result:
            raise RefreshTokenNotFoundException(getter.identifier)
        return result

    @staticmethod
    async def get_by_user_id(
        sql_session: AsyncSession, getter: RefreshTokenUserIdGetter
    ) -> list[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.user_id == getter.user_id)
        result = await sql_session.execute(stmt)
        refresh_tokens = result.scalars().all()
        if not refresh_tokens:
            raise RefreshTokenNotFoundException(getter.identifier)
        return list(refresh_tokens)

    @staticmethod
    async def insert_refresh_token(
        sql_session: AsyncSession, values: dict[str, Any]
    ) -> RefreshToken:
        stmt = insert(RefreshToken).values(values).returning(RefreshToken)
        result = await sql_session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def update_refresh_token(
        sql_session: AsyncSession,
        getter: RefreshTokenJtiGetter,
        values: dict[str, Any],
    ) -> RefreshToken:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.jti == getter.jti)
            .values(values)
            .returning(RefreshToken)
        )
        refresh_token = await sql_session.scalar(stmt)
        if not refresh_token:
            raise RefreshTokenNotFoundException(getter.identifier)
        return refresh_token

    @staticmethod
    async def delete_refresh_token(
        sql_session: AsyncSession, getter: RefreshTokenJtiGetter
    ) -> RefreshToken:
        stmt = (
            delete(RefreshToken)
            .where(RefreshToken.jti == getter.jti)
            .returning(RefreshToken)
        )
        refresh_token = await sql_session.scalar(stmt)
        if not refresh_token:
            raise RefreshTokenNotFoundException(getter.identifier)
        return refresh_token

    @staticmethod
    async def delete_all_refresh_token_by_user_id(
        sql_session: AsyncSession, getter: RefreshTokenUserIdGetter
    ) -> list[RefreshToken]:
        stmt = (
            delete(RefreshToken)
            .where(RefreshToken.user_id == getter.user_id)
            .returning(RefreshToken)
        )
        result = await sql_session.execute(stmt)
        refresh_tokens = result.scalars().all()
        return list(refresh_tokens)


SQL_ALCHEMY_REFRESH_TOKEN_REPO = SqlAlchemyRefreshTokenRepo()

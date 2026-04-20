from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import TEXT, DateTime, ForeignKey, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.database import Base
from src.shared.exceptions import AppException
from src.shared.web import IpAnyAddress, UserAgent


if TYPE_CHECKING:
    from src.users.storage import User


# region -------------------------- Types -------------------------
class RefreshTokenReadByJtiPort(Protocol):
    async def get_by_jti(
        self, sql_session: Any, getter: RefreshTokenJtiGetter
    ) -> RefreshToken: ...


class RefreshTokenReadByUserIdPort(Protocol):
    async def get_by_user_id(
        self, sql_session: Any, getter: RefreshTokenUserIdGetter
    ) -> Sequence[RefreshToken]: ...


class RefreshTokenDeletePort(Protocol):
    async def delete_refresh_token(
        self, sql_session: Any, getter: RefreshTokenJtiGetter
    ) -> RefreshToken: ...


class RefreshTokenDeleteAllByUserIdPort(Protocol):
    async def delete_all_refresh_token_by_user_id(
        self, sql_session: Any, getter: RefreshTokenUserIdGetter
    ) -> list[RefreshToken]: ...


class RefreshTokenUserIdGetter(BaseModel):
    user_id: UUID

    @property
    def identifier(self) -> str:
        return str(self.user_id)


class RefreshTokenJtiGetter(BaseModel):
    jti: UUID

    @property
    def identifier(self) -> str:
        return str(self.jti)


# endregion


# region -------------------------- Exception -------------------------
class RefreshTokenException(AppException):
    pass


class RefreshTokenExceptionContext(BaseModel):
    refresh_token: str


class RefreshTokenNotFoundException(RefreshTokenException):
    def __init__(self, context: RefreshTokenExceptionContext) -> None:
        super().__init__(
            message=f"Refresh Token {context.refresh_token} not found",
            context=context,
        )


# endregion


# region -------------------------- Model -------------------------
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    jti: Mapped[UUID] = mapped_column(
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    user_agent: Mapped[UserAgent] = mapped_column(TEXT)
    ip: Mapped[IpAnyAddress] = mapped_column(TEXT)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    user: Mapped[User] = relationship("User", back_populates="refresh_tokens")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )


# endregion


# region -------------------------- Adapter -------------------------
class SqlAlchemyRefreshTokenRepo:
    @staticmethod
    async def get_by_jti(
        sql_session: AsyncSession, getter: RefreshTokenJtiGetter
    ) -> RefreshToken:
        stmt = select(RefreshToken).where(RefreshToken.jti == getter.jti)
        result = await sql_session.scalar(stmt)
        if not result:
            raise RefreshTokenNotFoundException(
                RefreshTokenExceptionContext(refresh_token=getter.identifier)
            )
        return result

    @staticmethod
    async def get_by_user_id(
        sql_session: AsyncSession, getter: RefreshTokenUserIdGetter
    ) -> list[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.user_id == getter.user_id)
        result = await sql_session.execute(stmt)
        refresh_tokens = result.scalars().all()
        if not refresh_tokens:
            raise RefreshTokenNotFoundException(
                RefreshTokenExceptionContext(refresh_token=getter.identifier)
            )
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
            raise RefreshTokenNotFoundException(
                RefreshTokenExceptionContext(refresh_token=getter.identifier)
            )
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
            raise RefreshTokenNotFoundException(
                RefreshTokenExceptionContext(refresh_token=getter.identifier)
            )
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

# endregion

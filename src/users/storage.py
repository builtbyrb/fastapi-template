import datetime
import uuid
from typing import Any, Protocol

from pydantic import EmailStr
from pydantic_core import Url
from sqlalchemy import (
    TEXT,
    DateTime,
    Enum,
    String,
    delete,
    insert,
    or_,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.database import Base
from src.users.exceptions import (
    UserException,
    UserExceptionContext,
)
from src.users.subdomains.refresh_token.storage import RefreshToken
from src.users.unique import UserUniqueFields
from src.users.validations import (
    USER_EMAIL_LENGTH_RULE_DATA,
    USER_FIRST_NAME_LENGTH_RULE_DATA,
    USER_LAST_NAME_LENGTH_RULE_DATA,
    USER_USERNAME_LENGTH_RULE_DATA,
    UserEmailGetter,
    UserGetter,
    UserIdGetter,
    UserRole,
    UserUsernameGetter,
)


class UserNotFoundException(UserException):
    def __init__(self, context: UserExceptionContext) -> None:
        super().__init__(
            message=f"User {context.user} not found",
            context=context,
        )


class UserReadPort(Protocol):
    async def get_model(self, sql_session: Any, getter: UserGetter) -> User: ...


class UserGetByUniqueFieldsPort(Protocol):
    async def get_by_unique_fields(
        self, sql_session: Any, unique_fields: UserUniqueFields
    ) -> User | None: ...


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)

    first_name: Mapped[str] = mapped_column(
        String(USER_FIRST_NAME_LENGTH_RULE_DATA.MAX_LENGTH)
    )
    last_name: Mapped[str] = mapped_column(
        String(USER_LAST_NAME_LENGTH_RULE_DATA.MAX_LENGTH)
    )
    username: Mapped[str] = mapped_column(
        String(USER_USERNAME_LENGTH_RULE_DATA.MAX_LENGTH),
        unique=True,
        index=True,
    )
    email: Mapped[EmailStr] = mapped_column(
        String(USER_EMAIL_LENGTH_RULE_DATA.MAX_LENGTH),
        unique=True,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(TEXT)
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        "RefreshToken",
        order_by="RefreshToken.created_at",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
    )
    updated_password_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    last_login_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
    login_notification: Mapped[bool]
    disabled: Mapped[bool]
    avatar_url: Mapped[Url | None] = mapped_column(TEXT)

    @property
    def identifier(self) -> str:
        return self.email


class SQLAlchemyUserRepo:
    @staticmethod
    async def get_by_email(
        sql_session: AsyncSession, getter: UserEmailGetter
    ) -> User:
        stmt = select(User).where(User.email == getter.email)
        result = await sql_session.scalar(stmt)
        if not result:
            raise UserNotFoundException(UserExceptionContext(user=getter.identifier))
        return result

    @staticmethod
    async def get_by_username(
        sql_session: AsyncSession, getter: UserUsernameGetter
    ) -> User:
        stmt = select(User).where(User.username == getter.username)
        result = await sql_session.scalar(stmt)
        if not result:
            raise UserNotFoundException(UserExceptionContext(user=getter.identifier))
        return result

    @staticmethod
    async def get_by_id(sql_session: AsyncSession, getter: UserIdGetter) -> User:
        result = await sql_session.get(User, getter.id)
        if not result:
            raise UserNotFoundException(UserExceptionContext(user=getter.identifier))
        return result

    @staticmethod
    async def get_by_unique_fields(
        sql_session: AsyncSession, unique_fields: UserUniqueFields
    ) -> User | None:
        stmt = select(User).where(
            or_(
                User.email == unique_fields.email,
                User.username == unique_fields.username,
            )
        )
        return await sql_session.scalar(stmt)

    @classmethod
    async def get_model(cls, sql_session: AsyncSession, getter: UserGetter) -> User:
        if isinstance(getter, UserEmailGetter):
            return await cls.get_by_email(sql_session, getter)
        if isinstance(getter, UserUsernameGetter):
            return await cls.get_by_username(sql_session, getter)
        if isinstance(getter, UserIdGetter):
            return await cls.get_by_id(sql_session, getter)
        return None

    @staticmethod
    async def insert_user(sql_session: AsyncSession, values: dict[str, Any]) -> User:
        stmt = insert(User).values(values).returning(User)
        result = await sql_session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def update_user(
        sql_session: AsyncSession, getter: UserIdGetter, values: dict[str, Any]
    ) -> User:
        stmt = (
            update(User).where(User.id == getter.id).values(values).returning(User)
        )
        user = await sql_session.scalar(stmt)
        if not user:
            raise UserNotFoundException(UserExceptionContext(user=getter.identifier))
        return user

    @staticmethod
    async def update_user_password(
        sql_session: AsyncSession, getter: UserIdGetter, values: dict[str, Any]
    ) -> User:
        stmt = (
            update(User).where(User.id == getter.id).values(values).returning(User)
        )
        user = await sql_session.scalar(stmt)
        if not user:
            raise UserNotFoundException(UserExceptionContext(user=getter.identifier))
        return user

    @staticmethod
    async def delete_user(sql_session: AsyncSession, getter: UserIdGetter) -> User:
        stmt = delete(User).where(User.id == getter.id).returning(User)
        user = await sql_session.scalar(stmt)
        if not user:
            raise UserNotFoundException(UserExceptionContext(user=getter.identifier))
        return user


SQL_ALCHEMY_USER_REPO = SQLAlchemyUserRepo()

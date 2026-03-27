from typing import Any

from sqlalchemy import delete, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.exceptions import UserNotFoundException
from src.users.models import User
from src.users.types.alias import UserGetter
from src.users.types.internal import UserUniqueFields
from src.users.types.schemas import (
    UserEmailGetter,
    UserIdGetter,
    UserUsernameGetter,
)


class SQLAlchemyUserRepo:
    @staticmethod
    async def get_by_email(session: AsyncSession, getter: UserEmailGetter) -> User:
        stmt = select(User).where(User.email == getter.email)
        result = await session.scalar(stmt)
        if not result:
            raise UserNotFoundException(getter)
        return result

    @staticmethod
    async def get_by_username(
        session: AsyncSession, getter: UserUsernameGetter
    ) -> User:
        stmt = select(User).where(User.username == getter.username)
        result = await session.scalar(stmt)
        if not result:
            raise UserNotFoundException(getter)
        return result

    @staticmethod
    async def get_by_id(session: AsyncSession, getter: UserIdGetter) -> User:
        result = await session.get(User, getter.id)
        if not result:
            raise UserNotFoundException(getter)
        return result

    @staticmethod
    async def get_by_unique_fields(
        session: AsyncSession, unique_fields: UserUniqueFields
    ) -> User | None:
        stmt = select(User).where(
            or_(
                User.email == unique_fields.email,
                User.username == unique_fields.username,
            )
        )
        return await session.scalar(stmt)

    @classmethod
    async def get_model(cls, session: AsyncSession, getter: UserGetter) -> User:
        if isinstance(getter, UserEmailGetter):
            return await cls.get_by_email(session, getter)
        if isinstance(getter, UserUsernameGetter):
            return await cls.get_by_username(session, getter)
        if isinstance(getter, UserIdGetter):
            return await cls.get_by_id(session, getter)
        return None

    @staticmethod
    async def insert_user(session: AsyncSession, values: dict[str, Any]) -> User:
        stmt = insert(User).values(values).returning(User)
        result = await session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def update_user(
        session: AsyncSession, getter: UserIdGetter, values: dict[str, Any]
    ) -> User:
        stmt = (
            update(User).where(User.id == getter.id).values(values).returning(User)
        )
        user = await session.scalar(stmt)
        if not user:
            raise UserNotFoundException(getter)
        return user

    @staticmethod
    async def update_user_password(
        session: AsyncSession, getter: UserIdGetter, values: dict[str, Any]
    ) -> User:
        stmt = (
            update(User).where(User.id == getter.id).values(values).returning(User)
        )
        user = await session.scalar(stmt)
        if not user:
            raise UserNotFoundException(getter)
        return user

    @staticmethod
    async def delete_user(session: AsyncSession, getter: UserIdGetter) -> User:
        stmt = delete(User).where(User.id == getter.id).returning(User)
        user = await session.scalar(stmt)
        if not user:
            raise UserNotFoundException(getter)
        return user


SQL_ALCHEMY_USER_REPO = SQLAlchemyUserRepo()

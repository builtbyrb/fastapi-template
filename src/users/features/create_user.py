import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Any, Protocol
from uuid import UUID

from fastapi import APIRouter, Body, status
from pydantic import BaseModel, Field
from pydantic_core import Url
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import SqlSessionDep
from src.shared.date import get_utc_datetime
from src.shared.security import hash_password
from src.users.responses import USER_ALREADY_EXISTS_OPENAPI_RESPONSE
from src.users.storage import (
    SQL_ALCHEMY_USER_REPO,
    User,
    UserGetByUniqueFieldsPort,
)
from src.users.unique import (
    UserUniqueFields,
    validate_user_unique_fields,
)
from src.users.validations import UserBase, UserEmailPassword, UserOut, UserRole


class UserCreate(UserBase, UserEmailPassword):
    pass


class UserCreateInternal(BaseModel):
    id: UUID = Field(default_factory=uuid.uuid4)

    role: UserRole = Field(default=UserRole.USER)
    login_notification: bool = Field(default=True)
    disabled: bool = Field(default=False)
    avatar_url: Url | None = Field(default=None)

    created_at: datetime = Field(default_factory=get_utc_datetime)
    updated_password_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)
    last_login_at: datetime | None = Field(default=None)


def create_user_dict(create: UserCreate) -> dict[str, Any]:
    return {
        **create.model_dump(),
        **UserCreateInternal().model_dump(),
        "password_hash": hash_password(create.password),
    }


class UserInsertPort(Protocol):
    async def insert_user(
        self, sql_session: Any, values: dict[str, Any]
    ) -> User: ...


class UserRepoCreateUserPort(
    UserInsertPort, UserGetByUniqueFieldsPort, Protocol
): ...


@dataclass(frozen=True, kw_only=True)
class UserCreateServiceParams:
    sql_session: AsyncSession
    user_repo: UserRepoCreateUserPort
    create: UserCreate


async def user_create_service(params: UserCreateServiceParams) -> UserOut:
    sql_session = params.sql_session
    unique_fields = UserUniqueFields(
        email=params.create.email, username=params.create.username
    )

    validate_user_unique_fields(
        await params.user_repo.get_by_unique_fields(
            sql_session, unique_fields=unique_fields
        ),
        unique_fields,
    )
    user = await params.user_repo.insert_user(
        sql_session, create_user_dict(params.create)
    )
    user_out = UserOut.model_validate(user)

    await sql_session.commit()
    return user_out


router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    response_description="The newly created user object (password excluded).",
    responses={
        **USER_ALREADY_EXISTS_OPENAPI_RESPONSE.openapi_response,
    },
)
async def create_user(
    user_create: Annotated[UserCreate, Body()], sql_session: SqlSessionDep
) -> UserOut:
    return await user_create_service(
        UserCreateServiceParams(
            sql_session=sql_session,
            user_repo=SQL_ALCHEMY_USER_REPO,
            create=user_create,
        )
    )

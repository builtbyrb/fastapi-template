from dataclasses import dataclass
from typing import Annotated, Any, Protocol

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field
from pydantic_core import Url
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import SqlSessionDep
from src.users.current_user import CurrentActiveUserDep
from src.users.responses import (
    CURRENT_ACTIVE_USER_RESPONSE,
    USER_ALREADY_EXISTS_OPENAPI_RESPONSE,
)
from src.users.storage import SQL_ALCHEMY_USER_REPO, User, UserGetByUniqueFieldsPort
from src.users.unique import (
    OptionalUserUniqueFields,
    RequiredUserUniqueFields,
    validate_user_unique_fields,
)
from src.users.validations import (
    UserEmail,
    UserFirstName,
    UserIdGetter,
    UserLastName,
    UserOut,
    UserUpdateTimestamp,
    UserUsername,
)


class UserUpdate(BaseModel):
    first_name: UserFirstName | None = Field(default=None)
    last_name: UserLastName | None = Field(default=None)
    username: UserUsername | None = Field(default=None)
    email: UserEmail | None = Field(default=None)
    avatar_url: Url | None = Field(default=None)
    login_notification: bool | None = Field(default=None)


def update_user_dict(update: UserUpdate) -> dict[str, Any]:
    update_timestamp_dict = UserUpdateTimestamp(
        last_login_at=None, updated_password_at=None
    ).model_dump(exclude_none=True)
    update_dict = update.model_dump(exclude_unset=True)
    return {
        **update_timestamp_dict,
        **update_dict,
    }


class UserUpdatePort(Protocol):
    async def update_user(
        self, sql_session: Any, getter: UserIdGetter, values: dict[str, Any]
    ) -> User: ...


class UserRepoUpdateUserPort(
    UserGetByUniqueFieldsPort, UserUpdatePort, Protocol
): ...


@dataclass(frozen=True, kw_only=True)
class UserUpdateServiceParams:
    sql_session: AsyncSession
    getter: UserIdGetter
    user_repo: UserRepoUpdateUserPort
    update: UserUpdate


async def user_update_service(
    params: UserUpdateServiceParams,
) -> UserOut:
    sql_session = params.sql_session

    unique_fields = OptionalUserUniqueFields(
        email=params.update.email, username=params.update.username
    )
    user = await params.user_repo.get_by_unique_fields(
        sql_session, unique_fields=unique_fields
    )
    user_unique_fields = (
        RequiredUserUniqueFields(email=user.email, username=user.username)
        if user
        else None
    )

    validate_user_unique_fields(
        user_unique_fields,
        unique_fields,
    )
    user = await params.user_repo.update_user(
        sql_session,
        getter=params.getter,
        values=update_user_dict(params.update),
    )
    user_out = UserOut.model_validate(user)

    await sql_session.commit()
    return user_out


router = APIRouter()


@router.patch(
    "/update",
    summary="Update current user profile",
    response_description="The updated user object with the new values.",
    responses={
        **CURRENT_ACTIVE_USER_RESPONSE,
        **USER_ALREADY_EXISTS_OPENAPI_RESPONSE.openapi_response,
    },
)
async def update_user(
    current_user: CurrentActiveUserDep,
    user_update: Annotated[UserUpdate, Body()],
    sql_session: SqlSessionDep,
) -> UserOut:
    return await user_update_service(
        UserUpdateServiceParams(
            sql_session=sql_session,
            getter=UserIdGetter(id=current_user.id),
            user_repo=SQL_ALCHEMY_USER_REPO,
            update=user_update,
        )
    )

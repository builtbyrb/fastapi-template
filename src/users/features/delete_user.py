from dataclasses import dataclass
from typing import Any, Protocol

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import SqlSessionDep
from src.users.current_user import CurrentActiveUserDep
from src.users.responses import CURRENT_ACTIVE_USER_RESPONSE
from src.users.storage import SQL_ALCHEMY_USER_REPO, User, UserReadPort
from src.users.validations import UserIdGetter, UserOut


class UserDeletePort(Protocol):
    async def delete_user(self, sql_session: Any, getter: UserIdGetter) -> User: ...


class UserRepoDeleteUserPort(UserReadPort, UserDeletePort, Protocol): ...


@dataclass(frozen=True, kw_only=True)
class UserDeleteServiceParams:
    sql_session: AsyncSession
    getter: UserIdGetter
    user_repo: UserRepoDeleteUserPort


async def user_delete_service(
    params: UserDeleteServiceParams,
) -> UserOut:
    sql_session = params.sql_session
    user = await params.user_repo.delete_user(params.sql_session, params.getter)
    user_out = UserOut.model_validate(user)

    await sql_session.commit()
    return user_out


router = APIRouter()


@router.delete(
    "/delete",
    summary="Delete current user account",
    response_description="The deleted user object.",
    responses={
        **CURRENT_ACTIVE_USER_RESPONSE,
    },
)
async def delete_user(
    current_user: CurrentActiveUserDep, sql_session: SqlSessionDep
) -> UserOut:
    return await user_delete_service(
        UserDeleteServiceParams(
            sql_session=sql_session,
            getter=UserIdGetter(id=current_user.id),
            user_repo=SQL_ALCHEMY_USER_REPO,
        )
    )

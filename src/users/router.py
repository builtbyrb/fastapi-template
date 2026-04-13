from typing import Annotated

from fastapi import APIRouter, Body, status

from src.auth.config.exceptions import AUTH_CURRENT_USER_RESPONSE
from src.auth.dependencies import CurrentActiveUserDep
from src.core.dependencies import SqlSessionDep
from src.users.adapter import SQL_ALCHEMY_USER_REPO
from src.users.exceptions import (
    USER_ALREADY_EXISTS_DEF,
)
from src.users.services import (
    user_create_service,
    user_delete_service,
    user_update_service,
)
from src.users.types.internal import (
    UserCreateServiceParams,
    UserDeleteServiceParams,
    UserUpdateServiceParams,
)
from src.users.types.schemas import (
    UserCreate,
    UserIdGetter,
    UserOut,
    UserUpdate,
)


user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    response_description="The newly created user object (password excluded).",
    responses={
        **USER_ALREADY_EXISTS_DEF.response,
    },
)
async def create_user(
    user_create: Annotated[UserCreate, Body()], sql_session: SqlSessionDep
) -> UserOut:
    return await user_create_service(
        UserCreateServiceParams(
            sql_session=sql_session, user_repo=SQL_ALCHEMY_USER_REPO, create=user_create
        )
    )


@user_router.patch(
    "/update",
    summary="Update current user profile",
    response_description="The updated user object with the new values.",
    responses={
        **AUTH_CURRENT_USER_RESPONSE,
        **USER_ALREADY_EXISTS_DEF.response,
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


@user_router.delete(
    "/delete",
    summary="Delete current user account",
    response_description="The deleted user object.",
    responses={
        **AUTH_CURRENT_USER_RESPONSE,
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


@user_router.get(
    "/profile",
    summary="Get current user profile",
    response_description="The current authenticated user object.",
    responses={**AUTH_CURRENT_USER_RESPONSE},
)
async def user_profile(
    current_user: CurrentActiveUserDep,
) -> UserOut:
    return current_user

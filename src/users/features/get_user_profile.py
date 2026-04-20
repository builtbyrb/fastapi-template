from fastapi import APIRouter

from src.users.current_user import CurrentActiveUserDep
from src.users.responses import CURRENT_ACTIVE_USER_RESPONSE
from src.users.validations import UserOut


# region -------------------------- Api -------------------------
router = APIRouter()


@router.get(
    "/profile",
    summary="Get current user profile",
    response_description="The current authenticated user object.",
    responses={**CURRENT_ACTIVE_USER_RESPONSE},
)
async def user_profile(
    current_user: CurrentActiveUserDep,
) -> UserOut:
    return current_user


# endregion

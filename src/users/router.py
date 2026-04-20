from fastapi import APIRouter

from src.users.features.create_user import router as create_user_router
from src.users.features.delete_user import router as delete_user_router
from src.users.features.get_user_profile import router as get_user_profile_router
from src.users.features.login_user import router as login_user_router
from src.users.features.refresh_user_token import router as refresh_user_token_router
from src.users.features.update_user import router as update_user_router


user_router = APIRouter(prefix="/users", tags=["Users"])

user_router.include_router(create_user_router)
user_router.include_router(delete_user_router)
user_router.include_router(get_user_profile_router)
user_router.include_router(login_user_router)
user_router.include_router(refresh_user_token_router)
user_router.include_router(update_user_router)

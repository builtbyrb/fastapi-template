from src.refresh_token.types.schemas import (
    RefreshTokenJtiGetter,
    RefreshTokenUserIdGetter,
)


type RefreshTokenGetter = RefreshTokenJtiGetter | RefreshTokenUserIdGetter

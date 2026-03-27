from src.refresh_token.domain import (
    create_refresh_token_dict,
    update_refresh_token_dict,
)
from src.refresh_token.models import RefreshToken
from src.refresh_token.types.internal import (
    RefreshTokenCreateServiceParams,
    RefreshTokenUpdateServiceParams,
)


async def refresh_token_create_service(
    params: RefreshTokenCreateServiceParams,
) -> RefreshToken:
    create_dict = create_refresh_token_dict(params.create)
    return await params.refresh_token_repo.insert_refresh_token(
        params.session, create_dict
    )


async def refresh_token_update_service(
    params: RefreshTokenUpdateServiceParams,
) -> RefreshToken:
    update_dict = update_refresh_token_dict(params.update)
    return await params.refresh_token_repo.update_refresh_token(
        params.session, params.getter, update_dict
    )

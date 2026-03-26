from src.users.domain import (
    create_user_dict,
    update_user_dict,
    validate_user_unique_fields,
)
from src.users.types.internal import (
    UserCreateServiceParams,
    UserDeleteServiceParams,
    UserUniqueFields,
    UserUpdateServiceParams,
)
from src.users.types.schemas import UserOut


async def user_create_service(params: UserCreateServiceParams) -> UserOut:
    session = params.session
    unique_fields = UserUniqueFields(
        email=params.create.email, username=params.create.username
    )

    validate_user_unique_fields(
        await params.user_repo.get_by_unique_fields(
            session, unique_fields=unique_fields
        ),
        unique_fields,
    )
    user = await params.user_repo.insert_user(
        session, create_user_dict(params.create)
    )
    user_out = UserOut.model_validate(user)

    await session.commit()
    return user_out


async def user_update_service(
    params: UserUpdateServiceParams,
) -> UserOut:
    session = params.session
    unique_fields = UserUniqueFields(
        email=params.update.email, username=params.update.username
    )

    validate_user_unique_fields(
        await params.user_repo.get_by_unique_fields(
            session, unique_fields=unique_fields
        ),
        unique_fields,
    )
    user = await params.user_repo.update_user(
        session,
        getter=params.getter,
        values=update_user_dict(params.update),
    )
    user_out = UserOut.model_validate(user)

    await session.commit()
    return user_out


async def user_delete_service(
    params: UserDeleteServiceParams,
) -> UserOut:
    session = params.session
    user = await params.user_repo.delete_user(params.session, params.getter)
    user_out = UserOut.model_validate(user)

    await session.commit()
    return user_out

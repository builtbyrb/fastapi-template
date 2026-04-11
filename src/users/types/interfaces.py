from typing import TYPE_CHECKING, Any, Protocol


if TYPE_CHECKING:
    from src.users.models import User
    from src.users.types.alias import UserGetter
    from src.users.types.internal import UserUniqueFields
    from src.users.types.schemas import UserIdGetter
    from src.users.types.typings import UserEmail, UserUsername


class UserUniqueFieldsPort(Protocol):
    @property
    def email(self) -> UserEmail | None: ...
    @property
    def username(self) -> UserUsername | None: ...


class UserReadPort(Protocol):
    async def get_model(self, session: Any, getter: UserGetter) -> User: ...


class UserInsertPort(Protocol):
    async def insert_user(self, session: Any, values: dict[str, Any]) -> User: ...


class UserUpdatePort(Protocol):
    async def update_user(
        self, session: Any, getter: UserIdGetter, values: dict[str, Any]
    ) -> User: ...


class UserUpdatePasswordPort(Protocol):
    async def update_user_password(
        self, session: Any, getter: UserIdGetter, values: dict[str, Any]
    ) -> User: ...


class UserDeletePort(Protocol):
    async def delete_user(self, session: Any, getter: UserIdGetter) -> User: ...


class UserGetByUniqueFieldsPort(Protocol):
    async def get_by_unique_fields(
        self, session: Any, unique_fields: UserUniqueFields
    ) -> User | None: ...


class UserRepoCreateUserPort(
    UserInsertPort, UserGetByUniqueFieldsPort, Protocol
): ...


class UserRepoUpdateUserPort(
    UserGetByUniqueFieldsPort, UserUpdatePort, Protocol
): ...


class UserRepoDeleteUserPort(UserReadPort, UserDeletePort, Protocol): ...

from src.users.types.schemas import (
    UserEmailGetter,
    UserIdGetter,
    UserUsernameGetter,
)


type UserGetter = UserEmailGetter | UserUsernameGetter | UserIdGetter

from typing import Annotated

from fastapi.params import Header

from src.core.types.typings import UserAgent


type UserAgentHeader = Annotated[
    UserAgent,
    Header(alias="User-Agent", description="User-Agent header from the client"),
]

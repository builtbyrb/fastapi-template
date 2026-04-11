import uuid
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Form
from pydantic import BaseModel, Field, field_serializer

from src.core.utils import to_seconds
from src.users.types.schemas import UserEmail


class OAuth2PasswordRequestFormStrictTypedData(BaseModel):
    grant_type: str = Field(pattern="^password$")
    username: UserEmail
    password: str
    scope: str = ""
    client_id: str | None = None
    client_secret: str | None = None


class OAuth2PasswordRequestFormStrictTyped:
    def __init__(
        self,
        data: Annotated[OAuth2PasswordRequestFormStrictTypedData, Form()],
    ) -> None:
        self.grant_type = data.grant_type
        self.username = data.username
        self.password = data.password
        self.scopes = data.scope.split()
        self.client_id = data.client_id
        self.client_secret = data.client_secret


class TokenDataCreate(BaseModel):
    email: UserEmail
    jti: uuid.UUID
    expiration: timedelta

    @property
    def expiration_in_seconds(self) -> int:
        return to_seconds(self.expiration)


class TokenData(BaseModel):
    jti: uuid.UUID
    sub: UserEmail
    exp: datetime

    @field_serializer("exp")
    def serialize_dt(self, dt: datetime) -> int:
        return int(dt.timestamp())


class UsersTokens(BaseModel):
    refresh_token: str
    refresh_token_data_create: TokenDataCreate
    access_token: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str

import datetime
import uuid
from typing import TYPE_CHECKING

from pydantic import EmailStr
from pydantic_core import Url
from sqlalchemy import TEXT, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models import Base
from src.users.constants import (
    USER_EMAIL_LENGTH_RULE_DATA,
    USER_FIRST_NAME_LENGTH_RULE_DATA,
    USER_LAST_NAME_LENGTH_RULE_DATA,
    USER_USERNAME_LENGTH_RULE_DATA,
    UserRole,
)


if TYPE_CHECKING:
    from src.refresh_token.models import RefreshToken


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)

    first_name: Mapped[str] = mapped_column(
        String(USER_FIRST_NAME_LENGTH_RULE_DATA.MAX_LENGTH)
    )
    last_name: Mapped[str] = mapped_column(
        String(USER_LAST_NAME_LENGTH_RULE_DATA.MAX_LENGTH)
    )
    username: Mapped[str] = mapped_column(
        String(USER_USERNAME_LENGTH_RULE_DATA.MAX_LENGTH),
        unique=True,
        index=True,
    )
    email: Mapped[EmailStr] = mapped_column(
        String(USER_EMAIL_LENGTH_RULE_DATA.MAX_LENGTH),
        unique=True,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(TEXT)
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        "RefreshToken",
        order_by="RefreshToken.created_at",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
    )
    updated_password_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    last_login_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
    login_notification: Mapped[bool]
    disabled: Mapped[bool]
    avatar_url: Mapped[Url | None] = mapped_column(TEXT)

    @property
    def identifier(self) -> str:
        return self.email

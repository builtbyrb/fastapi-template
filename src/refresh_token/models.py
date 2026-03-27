from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import TEXT, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models import Base
from src.core.types.typings import IpAnyAddress, UserAgent


if TYPE_CHECKING:
    from src.users.models import User


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    jti: Mapped[UUID] = mapped_column(
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    user_agent: Mapped[UserAgent] = mapped_column(TEXT)
    ip: Mapped[IpAnyAddress] = mapped_column(TEXT)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    user: Mapped[User] = relationship("User", back_populates="refresh_tokens")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )

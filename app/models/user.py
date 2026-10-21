from typing import Optional

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin

ROLE_ATHLETE = "athlete"
ROLE_ADMIN = "admin"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default=ROLE_ATHLETE, nullable=False)  # athlete | admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    athlete: Mapped[Optional["Athlete"]] = relationship(back_populates="user", uselist=False)  # noqa: F821

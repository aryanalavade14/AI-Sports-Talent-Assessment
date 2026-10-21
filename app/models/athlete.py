import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Athlete(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "athletes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)  # male | female | other
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sport: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship(back_populates="athlete")  # noqa: F821
    submissions: Mapped[list["TestSubmission"]] = relationship(  # noqa: F821
        back_populates="athlete", cascade="all, delete-orphan"
    )
    results: Mapped[list["TestResult"]] = relationship(  # noqa: F821
        back_populates="athlete", cascade="all, delete-orphan"
    )
    sync_records: Mapped[list["SyncRecord"]] = relationship(  # noqa: F821
        back_populates="athlete", cascade="all, delete-orphan"
    )

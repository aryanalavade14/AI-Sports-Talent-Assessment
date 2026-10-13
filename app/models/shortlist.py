"""Athletes an admin has shortlisted as promising (Part 4 dashboard)."""
import uuid

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Shortlist(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "shortlisted_athletes"

    athlete_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("athletes.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    shortlisted_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

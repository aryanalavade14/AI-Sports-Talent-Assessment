import uuid

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin

SYNC_SYNCED = "synced"
SYNC_FAILED = "failed"


class SyncRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One row per client_submission_id: tracks offline-sync attempts and outcome."""

    __tablename__ = "sync_records"

    client_submission_id: Mapped[uuid.UUID] = mapped_column(Uuid, unique=True, index=True, nullable=False)
    athlete_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("athletes.id", ondelete="CASCADE"), index=True, nullable=False
    )
    submission_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("test_submissions.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default=SYNC_FAILED, nullable=False)  # synced | failed
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    athlete: Mapped["Athlete"] = relationship(back_populates="sync_records")  # noqa: F821

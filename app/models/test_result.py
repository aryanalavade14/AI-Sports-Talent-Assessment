import uuid

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin

VERIFICATION_PENDING = "pending"
VERIFICATION_VERIFIED = "verified"
VERIFICATION_FLAGGED = "flagged"
VERIFICATION_REJECTED = "rejected"


class TestResult(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __test__ = False

    __tablename__ = "test_results"

    submission_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("test_submissions.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    athlete_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("athletes.id", ondelete="CASCADE"), index=True, nullable=False
    )
    test_type: Mapped[str] = mapped_column(String(30), nullable=False)

    # AI engine output
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    jump_height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)  # vertical_jump only
    rep_count: Mapped[int | None] = mapped_column(Integer, nullable=True)  # sit_up only
    raw_ai_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Benchmarking is done by another teammate; these fields are left for them to fill in.
    benchmark_percentile: Mapped[float | None] = mapped_column(Float, nullable=True)
    benchmark_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    norm_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

    verification_status: Mapped[str] = mapped_column(String(20), default=VERIFICATION_PENDING, nullable=False)

    submission: Mapped["TestSubmission"] = relationship(back_populates="result")  # noqa: F821
    athlete: Mapped["Athlete"] = relationship(back_populates="results")  # noqa: F821

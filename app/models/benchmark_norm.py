"""Age/gender performance norms used by the benchmarking module (Part 4).

One row = one test + gender + age band, stored as percentile anchor points.
Rows are created by the Alembic migration 0002 and can be edited in the database
(or replaced with official SAI / Khelo India tables) without touching any code.
"""
from sqlalchemy import Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin


class BenchmarkNorm(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "benchmark_norms"
    __table_args__ = (UniqueConstraint("test_type", "gender", "age_min", name="uq_norm_test_gender_age"),)

    test_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)  # vertical_jump | sit_up
    gender: Mapped[str] = mapped_column(String(20), nullable=False)  # male | female
    age_min: Mapped[int] = mapped_column(Integer, nullable=False)
    age_max: Mapped[int] = mapped_column(Integer, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)  # cm | reps

    # The score that an athlete of this age/gender needs to reach each percentile.
    p10: Mapped[float] = mapped_column(Float, nullable=False)
    p25: Mapped[float] = mapped_column(Float, nullable=False)
    p50: Mapped[float] = mapped_column(Float, nullable=False)
    p75: Mapped[float] = mapped_column(Float, nullable=False)
    p90: Mapped[float] = mapped_column(Float, nullable=False)

    source: Mapped[str] = mapped_column(String(255), nullable=False)

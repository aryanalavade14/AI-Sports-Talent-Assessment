"""benchmark norms + shortlisted athletes (Part 4: benchmarking & admin dashboard)

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-13
"""
import uuid
from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.data.default_norms import SOURCE, default_rows

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    norms = op.create_table(
        "benchmark_norms",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("test_type", sa.String(30), nullable=False),
        sa.Column("gender", sa.String(20), nullable=False),
        sa.Column("age_min", sa.Integer(), nullable=False),
        sa.Column("age_max", sa.Integer(), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("p10", sa.Float(), nullable=False),
        sa.Column("p25", sa.Float(), nullable=False),
        sa.Column("p50", sa.Float(), nullable=False),
        sa.Column("p75", sa.Float(), nullable=False),
        sa.Column("p90", sa.Float(), nullable=False),
        sa.Column("source", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("test_type", "gender", "age_min", name="uq_norm_test_gender_age"),
    )
    op.create_index("ix_benchmark_norms_test_type", "benchmark_norms", ["test_type"])

    now = datetime.now(timezone.utc)
    op.bulk_insert(
        norms,
        [
            {
                "id": uuid.uuid4(), "test_type": t, "gender": g, "unit": unit, "age_min": lo, "age_max": hi,
                "p10": p10, "p25": p25, "p50": p50, "p75": p75, "p90": p90,
                "source": SOURCE, "created_at": now, "updated_at": now,
            }
            for (t, g, unit, lo, hi, p10, p25, p50, p75, p90) in default_rows()
        ],
    )

    op.create_table(
        "shortlisted_athletes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("athlete_id", sa.Uuid(), nullable=False),
        sa.Column("shortlisted_by", sa.Uuid(), nullable=True),
        sa.Column("note", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["athlete_id"], ["athletes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["shortlisted_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("athlete_id"),
    )


def downgrade() -> None:
    op.drop_table("shortlisted_athletes")
    op.drop_index("ix_benchmark_norms_test_type", table_name="benchmark_norms")
    op.drop_table("benchmark_norms")

"""initial schema: users, athletes, test_submissions, test_results, sync_records

Revision ID: 0001
Revises:
Create Date: 2026-10-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _timestamps():
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "athletes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("gender", sa.String(20), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("sport", sa.String(100), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "test_submissions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_submission_id", sa.Uuid(), nullable=True),
        sa.Column("athlete_id", sa.Uuid(), nullable=False),
        sa.Column("test_type", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("video_path", sa.String(500), nullable=False),
        sa.Column("video_original_name", sa.String(255), nullable=True),
        sa.Column("video_content_type", sa.String(100), nullable=True),
        sa.Column("video_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("video_duration_seconds", sa.Float(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sensor_data", sa.JSON(), nullable=True),
        sa.Column("cheat_flag", sa.Boolean(), nullable=False),
        sa.Column("cheat_reasons", sa.JSON(), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["athlete_id"], ["athletes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_test_submissions_client_submission_id", "test_submissions", ["client_submission_id"], unique=True)
    op.create_index("ix_test_submissions_athlete_id", "test_submissions", ["athlete_id"])

    op.create_table(
        "test_results",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("submission_id", sa.Uuid(), nullable=False),
        sa.Column("athlete_id", sa.Uuid(), nullable=False),
        sa.Column("test_type", sa.String(30), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("jump_height_cm", sa.Float(), nullable=True),
        sa.Column("rep_count", sa.Integer(), nullable=True),
        sa.Column("raw_ai_response", sa.JSON(), nullable=True),
        sa.Column("benchmark_percentile", sa.Float(), nullable=True),
        sa.Column("benchmark_category", sa.String(50), nullable=True),
        sa.Column("norm_reference", sa.String(255), nullable=True),
        sa.Column("verification_status", sa.String(20), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["submission_id"], ["test_submissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["athlete_id"], ["athletes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("submission_id"),
    )
    op.create_index("ix_test_results_athlete_id", "test_results", ["athlete_id"])

    op.create_table(
        "sync_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_submission_id", sa.Uuid(), nullable=False),
        sa.Column("athlete_id", sa.Uuid(), nullable=False),
        sa.Column("submission_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["athlete_id"], ["athletes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["submission_id"], ["test_submissions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sync_records_client_submission_id", "sync_records", ["client_submission_id"], unique=True)
    op.create_index("ix_sync_records_athlete_id", "sync_records", ["athlete_id"])


def downgrade() -> None:
    op.drop_table("sync_records")
    op.drop_table("test_results")
    op.drop_table("test_submissions")
    op.drop_table("athletes")
    op.drop_table("users")

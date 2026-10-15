"""Creates a test submission: validate file -> store video -> cheat checks -> save -> AI analysis.

Used by both POST /api/tests/upload and the offline-sync endpoints, so both
behave identically (and both are idempotent when a client_submission_id is given).
"""
import json
import logging
import mimetypes
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.athlete import Athlete
from app.models.sync_record import SYNC_FAILED, SYNC_SYNCED, SyncRecord
from app.models.test_submission import TestSubmission
from app.services import ai_service
from app.services.cheat_detection_service import ALLOWED_EXTENSIONS, run_cheat_checks
from app.services.storage_service import FileTooLargeError, get_storage
from app.utils.errors import AppError

logger = logging.getLogger("app.submissions")


@dataclass
class VideoInput:
    filename: str
    content_type: str | None
    stream: BinaryIO


def guess_content_type(filename: str) -> str | None:
    return mimetypes.guess_type(filename)[0]


def parse_sensor_data(raw) -> tuple[dict | None, bool]:
    """Accept a dict or a JSON string. Returns (data, is_valid)."""
    if raw is None or raw == "":
        return None, True
    if isinstance(raw, dict):
        return raw, True
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError):
        return None, False
    return (parsed, True) if isinstance(parsed, dict) else (None, False)


def _validate_video(video: VideoInput) -> str:
    """Hard validation: reject files we can never process. Returns the extension."""
    extension = Path(video.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise AppError(400, f"Unsupported video type '{extension}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")
    if video.content_type and not (
        video.content_type.startswith("video/") or video.content_type == "application/octet-stream"
    ):
        raise AppError(400, f"Invalid content type '{video.content_type}'. A video file is required.")
    return extension


def find_by_client_id(db: Session, client_submission_id: uuid.UUID) -> TestSubmission | None:
    return db.scalar(select(TestSubmission).where(TestSubmission.client_submission_id == client_submission_id))


def get_sync_record(db: Session, client_submission_id: uuid.UUID) -> SyncRecord | None:
    return db.scalar(select(SyncRecord).where(SyncRecord.client_submission_id == client_submission_id))


def record_sync_failure(db: Session, athlete_id: uuid.UUID, client_submission_id: uuid.UUID, message: str) -> None:
    """Remember that a sync attempt failed, so GET /api/sync/status/{id} can report it."""
    db.rollback()
    record = get_sync_record(db, client_submission_id)
    if record is not None and record.athlete_id != athlete_id:
        return  # belongs to someone else; never touch it
    if record is None:
        record = SyncRecord(client_submission_id=client_submission_id, athlete_id=athlete_id, attempts=0)
        db.add(record)
    if record.status != SYNC_SYNCED:
        record.status = SYNC_FAILED
        record.error_message = message[:1000]
    record.attempts += 1
    db.commit()


def create_submission(
    db: Session,
    *,
    athlete: Athlete,
    test_type: str,
    video: VideoInput,
    recorded_at: datetime | None,
    duration_seconds: float | None,
    sensor_data_raw,
    client_submission_id: uuid.UUID | None = None,
) -> tuple[TestSubmission, bool]:
    """Returns (submission, created). created=False means it was a duplicate sync of the same UUID."""

    # --- Idempotency: the same client_submission_id must never create a second row ---
    if client_submission_id is not None:
        existing = find_by_client_id(db, client_submission_id)
        if existing is not None:
            if existing.athlete_id != athlete.id:
                raise AppError(409, "client_submission_id is already used by another athlete")
            record = get_sync_record(db, client_submission_id)
            if record is not None:
                record.attempts += 1
                db.commit()
            return existing, False

    settings = get_settings()
    storage = get_storage()
    extension = _validate_video(video)

    # --- Store the video (size is enforced while streaming to disk) ---
    try:
        relative_path, size = storage.save(
            athlete_id=athlete.id,
            test_type=test_type,
            extension=extension,
            stream=video.stream,
            max_bytes=settings.max_video_size_bytes,
        )
    except FileTooLargeError:
        raise AppError(400, f"Video is larger than the {settings.MAX_VIDEO_SIZE_MB} MB limit")

    # --- Basic cheat detection ---
    sensor_data, sensor_valid = parse_sensor_data(sensor_data_raw)
    cheat_flag, cheat_reasons = run_cheat_checks(
        file_path=storage.absolute_path(relative_path),
        file_size=size,
        test_type=test_type,
        recorded_at=recorded_at,
        duration_seconds=duration_seconds,
        sensor_data=sensor_data,
        sensor_data_valid=sensor_valid,
    )

    submission = TestSubmission(
        client_submission_id=client_submission_id,
        athlete_id=athlete.id,
        test_type=test_type,
        video_path=relative_path,
        video_original_name=(video.filename or "")[:255],
        video_content_type=video.content_type or guess_content_type(video.filename),
        video_size_bytes=size,
        video_duration_seconds=duration_seconds,
        recorded_at=recorded_at,
        sensor_data=sensor_data,
        cheat_flag=cheat_flag,
        cheat_reasons=cheat_reasons,
    )

    # --- Save to the database (submission + sync record in ONE transaction) ---
    try:
        db.add(submission)
        db.flush()
        if client_submission_id is not None:
            record = get_sync_record(db, client_submission_id)
            if record is None:
                record = SyncRecord(client_submission_id=client_submission_id, athlete_id=athlete.id, attempts=0)
                db.add(record)
            record.submission_id = submission.id
            record.status = SYNC_SYNCED
            record.error_message = None
            record.attempts += 1
        db.commit()
    except IntegrityError:
        # Two requests with the same UUID raced each other: keep the first, drop ours.
        db.rollback()
        storage.delete(relative_path)
        existing = find_by_client_id(db, client_submission_id) if client_submission_id else None
        if existing is not None:
            return existing, False
        raise

    # --- AI analysis (real or mock). A failure is stored on the submission, not lost. ---
    try:
        ai_service.run_analysis(db, submission)
    except ai_service.AIServiceError:
        pass  # submission.status == "failed"; client can call POST /api/tests/{id}/analyze to retry
    db.refresh(submission)
    return submission, True

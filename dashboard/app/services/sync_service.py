"""Offline sync helpers (idempotent, built on submission_service)."""
import base64
import binascii
import io
import logging
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.athlete import Athlete
from app.models.user import User
from app.schemas.sync import SyncItem, SyncItemResult
from app.services import submission_service
from app.services.submission_service import VideoInput
from app.utils.deps import get_athlete_for_user
from app.utils.errors import AppError

logger = logging.getLogger("app.sync")


def sync_one(
    db: Session,
    user: User,
    *,
    client_submission_id: uuid.UUID,
    athlete_id: uuid.UUID,
    test_type: str,
    recorded_at: datetime | None,
    duration_seconds: float | None,
    sensor_data_raw,
    video: VideoInput,
) -> SyncItemResult:
    """Sync a single submission. Raises AppError on failure (after remembering the failure)."""
    athlete: Athlete = get_athlete_for_user(db, user, athlete_id)  # 404 / 403
    try:
        submission, created = submission_service.create_submission(
            db,
            athlete=athlete,
            test_type=test_type,
            video=video,
            recorded_at=recorded_at,
            duration_seconds=duration_seconds,
            sensor_data_raw=sensor_data_raw,
            client_submission_id=client_submission_id,
        )
    except AppError as exc:
        submission_service.record_sync_failure(db, athlete.id, client_submission_id, exc.detail)
        raise
    except Exception as exc:  # unexpected: remember it, then let the global handler return 500
        logger.exception("Sync failed for %s", client_submission_id)
        submission_service.record_sync_failure(db, athlete.id, client_submission_id, f"Server error: {exc}")
        raise
    return SyncItemResult(
        client_submission_id=client_submission_id,
        success=True,
        status="created" if created else "duplicate",
        submission_id=submission.id,
        submission_status=submission.status,
    )


def sync_batch_item(db: Session, user: User, item: SyncItem) -> SyncItemResult:
    """Sync one item of a batch. Never raises: errors become a per-item 'failed' result."""
    try:
        try:
            content = base64.b64decode(item.video_base64, validate=True)
        except (binascii.Error, ValueError):
            raise AppError(400, "video_base64 is not valid base64")
        video = VideoInput(
            filename=item.video_filename,
            content_type=submission_service.guess_content_type(item.video_filename),
            stream=io.BytesIO(content),
        )
        return sync_one(
            db,
            user,
            client_submission_id=item.client_submission_id,
            athlete_id=item.athlete_id,
            test_type=item.test_type.value,
            recorded_at=item.recorded_at,
            duration_seconds=item.duration_seconds,
            sensor_data_raw=item.sensor_data,
            video=video,
        )
    except AppError as exc:
        db.rollback()
        return SyncItemResult(
            client_submission_id=item.client_submission_id, success=False, status="failed", error=exc.detail
        )
    except Exception:
        db.rollback()
        logger.exception("Unexpected batch sync error")
        return SyncItemResult(
            client_submission_id=item.client_submission_id,
            success=False,
            status="failed",
            error="Internal server error while syncing this item",
        )

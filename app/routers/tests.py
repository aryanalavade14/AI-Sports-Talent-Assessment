
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.test_submission import STATUS_PROCESSING, TestSubmission
from app.models.user import User
from app.schemas.test import SubmissionOut, TestType
from app.services import ai_service, submission_service
from app.services.submission_service import VideoInput
from app.utils.deps import get_athlete_for_user, get_current_user
from app.utils.errors import AppError

router = APIRouter(prefix="/api/tests", tags=["Tests & Videos"])


def _get_submission_for_user(
    db: Session, user: User, submission_id: uuid.UUID
) -> TestSubmission:
    submission = db.get(TestSubmission, submission_id)
    if submission is None:
        raise AppError(404, "Submission not found")

    get_athlete_for_user(db, user, submission.athlete_id)
    return submission


@router.post("/upload", response_model=SubmissionOut, status_code=201)
def upload_test(
    response: Response,
    athlete_id: uuid.UUID = Form(...),
    test_type: TestType = Form(...),
    height_cm: float | None = Form(None, ge=100, le=230),
    video: UploadFile = File(..., description="mp4 / mov / avi / mkv / webm"),
    recorded_at: datetime | None = Form(None),
    duration_seconds: float | None = Form(None),
    sensor_data: str | None = Form(None),
    client_submission_id: uuid.UUID | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload and store a test video."""
    athlete = get_athlete_for_user(db, current_user, athlete_id)

    if test_type.value == "vertical_jump" and height_cm is None:
        raise AppError(422, "height_cm is required for vertical-jump analysis")

    submission, created = submission_service.create_submission(
        db,
        athlete=athlete,
        test_type=test_type.value,
        video=VideoInput(
            filename=video.filename or "",
            content_type=video.content_type,
            stream=video.file,
        ),
        recorded_at=recorded_at,
        duration_seconds=duration_seconds,
        sensor_data_raw=sensor_data,
        client_submission_id=client_submission_id,
    )

    if not created:
        response.status_code = 200

    return submission


@router.get("/athlete/{athlete_id}", response_model=list[SubmissionOut])
def list_athlete_tests(
    athlete_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    athlete = get_athlete_for_user(db, current_user, athlete_id)

    stmt = (
        select(TestSubmission)
        .where(TestSubmission.athlete_id == athlete.id)
        .order_by(TestSubmission.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.scalars(stmt).all()


@router.get("/{submission_id}", response_model=SubmissionOut)
def get_test(
    submission_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_submission_for_user(db, current_user, submission_id)


@router.post("/{submission_id}/analyze", response_model=SubmissionOut)
def analyze_test(
    submission_id: uuid.UUID,
    height_cm: float | None = Form(None, ge=100, le=230),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run AI analysis for a stored video."""
    submission = _get_submission_for_user(db, current_user, submission_id)

    if submission.status == STATUS_PROCESSING:
        raise AppError(409, "Analysis is already running for this submission")

    if submission.test_type == "vertical_jump" and height_cm is None:
        raise AppError(422, "height_cm is required for vertical-jump analysis")

    try:
        ai_service.run_analysis(
            db, submission, height_cm=height_cm
        )
    except ai_service.AIServiceError as exc:
        raise AppError(502, f"AI engine error: {exc}")

    db.refresh(submission)
    return submission

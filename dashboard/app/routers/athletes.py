import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.athlete import Athlete
from app.models.test_result import TestResult
from app.models.test_submission import TestSubmission
from app.models.user import ROLE_ADMIN, User
from app.schemas.athlete import AthleteCreate, AthleteOut, AthleteUpdate
from app.schemas.test import SubmissionSummary, TestResultOut
from app.utils.deps import get_athlete_for_user, get_current_user, require_admin
from app.utils.errors import AppError

router = APIRouter(prefix="/api/athletes", tags=["Athletes"])


@router.post("", response_model=AthleteOut, status_code=201)
def create_athlete(
    data: AthleteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Create the athlete profile. Athletes create their own; admins must pass `user_id`."""
    if current_user.role == ROLE_ADMIN:
        if data.user_id is None:
            raise AppError(400, "Admins must provide user_id for the athlete profile")
        owner = db.get(User, data.user_id)
        if owner is None:
            raise AppError(404, "User not found")
        owner_id = owner.id
    else:
        if data.user_id is not None and data.user_id != current_user.id:
            raise AppError(403, "You can only create your own profile")
        owner_id = current_user.id

    if db.scalar(select(Athlete).where(Athlete.user_id == owner_id)):
        raise AppError(409, "This user already has an athlete profile")

    athlete = Athlete(user_id=owner_id, **data.model_dump(exclude={"user_id"}))
    db.add(athlete)
    db.commit()
    db.refresh(athlete)
    return athlete


@router.get("", response_model=list[AthleteOut])
def list_athletes(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Admin only: list all athletes (handy for the dashboard)."""
    return db.scalars(select(Athlete).order_by(Athlete.created_at.desc()).limit(limit).offset(offset)).all()


@router.get("/{athlete_id}", response_model=AthleteOut)
def get_athlete(
    athlete_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return get_athlete_for_user(db, current_user, athlete_id)


@router.put("/{athlete_id}", response_model=AthleteOut)
def update_athlete(
    athlete_id: uuid.UUID,
    data: AthleteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    athlete = get_athlete_for_user(db, current_user, athlete_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(athlete, field, value)
    db.commit()
    db.refresh(athlete)
    return athlete


@router.get("/{athlete_id}/history", response_model=list[SubmissionSummary])
def athlete_history(
    athlete_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Test history: every submission (newest first) with its status, cheat flag and result."""
    athlete = get_athlete_for_user(db, current_user, athlete_id)
    stmt = (
        select(TestSubmission)
        .where(TestSubmission.athlete_id == athlete.id)
        .order_by(TestSubmission.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.scalars(stmt).all()


@router.get("/{athlete_id}/results", response_model=list[TestResultOut])
def athlete_results(
    athlete_id: uuid.UUID,
    test_type: str | None = Query(None, description="Filter: vertical_jump or sit_up"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    athlete = get_athlete_for_user(db, current_user, athlete_id)
    stmt = select(TestResult).where(TestResult.athlete_id == athlete.id)
    if test_type:
        stmt = stmt.where(TestResult.test_type == test_type)
    stmt = stmt.order_by(TestResult.created_at.desc()).limit(limit).offset(offset)
    return db.scalars(stmt).all()

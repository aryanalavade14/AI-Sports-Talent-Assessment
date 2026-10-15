"""Admin / SAI dashboard API (Part 4). Every endpoint here is admin-only."""
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.athlete import Athlete
from app.models.shortlist import Shortlist
from app.models.user import User
from app.schemas.dashboard import (
    AthleteRow,
    FilterOptions,
    LeaderboardRow,
    ShortlistIn,
    ShortlistOut,
    Summary,
)
from app.services import dashboard_service as svc
from app.utils.deps import require_admin
from app.utils.errors import AppError

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"], dependencies=[Depends(require_admin)])


def filters(
    region: str | None = Query(None, description="State (or city if no state)"),
    sport: str | None = None,
    gender: Literal["male", "female", "other"] | None = None,
    age_min: int | None = Query(None, ge=0, le=120),
    age_max: int | None = Query(None, ge=0, le=120),
) -> svc.Filters:
    return svc.Filters(region=region, sport=sport, gender=gender, age_min=age_min, age_max=age_max)


@router.get("/filters", response_model=FilterOptions)
def filter_options(db: Session = Depends(get_db)):
    """Values for the filter drop-downs, taken from the real athlete records."""
    return svc.filter_options(db)


@router.get("/summary", response_model=Summary)
def summary(f: svc.Filters = Depends(filters), db: Session = Depends(get_db)):
    return svc.summary(db, f)


@router.get("/athletes", response_model=list[AthleteRow])
def athletes(f: svc.Filters = Depends(filters), db: Session = Depends(get_db)):
    """Athlete table: scores, age, gender, sport, region, percentile, shortlist flag."""
    return svc.athlete_rows(db, f)


@router.get("/leaderboard", response_model=list[LeaderboardRow])
def leaderboard(
    test: Literal["overall", "vertical_jump", "sit_up"] = "overall",
    limit: int = Query(50, ge=1, le=500),
    f: svc.Filters = Depends(filters),
    db: Session = Depends(get_db),
):
    """Athletes ranked by percentile (fair across ages and genders); ties broken by raw score."""
    return svc.leaderboard(db, f, test, limit)


@router.get("/shortlist", response_model=list[ShortlistOut])
def list_shortlist(db: Session = Depends(get_db)):
    entries = list(db.scalars(select(Shortlist).order_by(Shortlist.created_at.desc())))
    if not entries:
        return []
    by_id = {r["athlete_id"]: r for r in svc.athlete_rows(db, svc.Filters())}
    return [
        {"athlete": by_id[e.athlete_id], "note": e.note, "shortlisted_at": e.created_at}
        for e in entries
        if e.athlete_id in by_id
    ]


@router.put("/shortlist/{athlete_id}", response_model=ShortlistOut)
def add_to_shortlist(
    athlete_id: uuid.UUID,
    data: ShortlistIn | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Shortlist an athlete (or update the note if already shortlisted)."""
    if db.get(Athlete, athlete_id) is None:
        raise AppError(404, "Athlete not found")
    entry = db.scalar(select(Shortlist).where(Shortlist.athlete_id == athlete_id))
    if entry is None:
        entry = Shortlist(athlete_id=athlete_id, shortlisted_by=admin.id)
        db.add(entry)
    if data is not None and data.note is not None:
        entry.note = data.note.strip() or None
    db.commit()
    db.refresh(entry)
    row = svc.athlete_rows(db, svc.Filters(athlete_id=athlete_id))[0]
    return {"athlete": row, "note": entry.note, "shortlisted_at": entry.created_at}


@router.delete("/shortlist/{athlete_id}", status_code=204)
def remove_from_shortlist(athlete_id: uuid.UUID, db: Session = Depends(get_db)):
    entry = db.scalar(select(Shortlist).where(Shortlist.athlete_id == athlete_id))
    if entry is not None:
        db.delete(entry)
        db.commit()

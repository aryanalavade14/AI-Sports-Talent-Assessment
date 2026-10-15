"""Benchmark norms and percentile calculation (Part 4)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.athlete import Athlete
from app.models.test_result import TestResult
from app.models.user import User
from app.schemas.dashboard import EvaluateOut, NormOut, RecalculateOut
from app.schemas.test import TestType
from app.services.benchmark_service import NormTable, apply_benchmark
from app.utils.deps import get_current_user, require_admin
from app.utils.errors import AppError

router = APIRouter(prefix="/api/benchmarks", tags=["Benchmarking"])


@router.get("/norms", response_model=list[NormOut])
def list_norms(
    test_type: TestType | None = None, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    """The age/gender norm table (score needed for the 10th/25th/50th/75th/90th percentile)."""
    rows = NormTable.load(db).all_rows()
    return [n for n in rows if test_type is None or n.test_type == test_type.value]


@router.get("/evaluate", response_model=EvaluateOut)
def evaluate(
    test_type: TestType,
    gender: str = Query(pattern="^(male|female|other)$"),
    age: int = Query(ge=5, le=100),
    value: float = Query(ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Percentile + performance level for one score. Also usable from the mobile app."""
    result = NormTable.load(db).evaluate(test_type.value, gender, age, value)
    if result is None:
        raise AppError(404, "No benchmark norm found for this test, gender and age")
    return {"test_type": test_type.value, "gender": gender, "age": age, "value": value, **result}


@router.post("/recalculate", response_model=RecalculateOut)
def recalculate(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """Admin: save percentile/level/norm into test_results.benchmark_* for every existing result."""
    norms = NormTable.load(db)
    updated = skipped = 0
    rows = db.execute(select(TestResult, Athlete).join(Athlete, Athlete.id == TestResult.athlete_id))
    for result, athlete in rows:
        if apply_benchmark(db, result, athlete, norms):
            updated += 1
        else:
            skipped += 1
    db.commit()
    return {"updated": updated, "skipped_no_norm": skipped}


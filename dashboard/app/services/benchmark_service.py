"""Benchmarking: turn a raw score into a percentile and a performance level.

How it works (simple on purpose):
  1. Find the norm row for the athlete's test + gender + age.
  2. The row stores the score needed for the 10th/25th/50th/75th/90th percentile.
  3. The athlete's score is placed between those anchor points by straight-line interpolation.
     Below the 10th / above the 90th anchor, the nearest segment's slope is continued.
  4. The percentile is clamped to 1..99 and mapped to a performance level.

Athletes with gender "other" are compared to the average of the male and female norms.
"""
from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.benchmark_norm import BenchmarkNorm

TEST_LABELS = {"vertical_jump": "Vertical Jump", "sit_up": "Sit-ups"}

# (minimum percentile, level name) - highest first
LEVELS = [(80, "Excellent"), (60, "Good"), (40, "Average"), (20, "Developing"), (0, "Needs Improvement")]
LEVEL_ORDER = [name for _, name in reversed(LEVELS)]


@dataclass
class Anchors:
    p10: float
    p25: float
    p50: float
    p75: float
    p90: float
    reference: str  # human-readable, saved in test_results.norm_reference


def age_on(dob: date, today: date | None = None) -> int:
    today = today or date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def level_for(percentile: float) -> str:
    for minimum, name in LEVELS:
        if percentile >= minimum:
            return name
    return LEVELS[-1][1]


def percentile_from_anchors(value: float, a: Anchors) -> float:
    points = [(a.p10, 10.0), (a.p25, 25.0), (a.p50, 50.0), (a.p75, 75.0), (a.p90, 90.0)]
    if value <= points[0][0]:
        (x0, y0), (x1, y1) = points[0], points[1]
    elif value >= points[-1][0]:
        (x0, y0), (x1, y1) = points[-2], points[-1]
    else:
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            if x0 <= value <= x1:
                break
    if x1 == x0:
        pct = y1 if value >= x1 else y0
    else:
        pct = y0 + (value - x0) * (y1 - y0) / (x1 - x0)
    return round(min(99.0, max(1.0, pct)), 1)


def _band_label(norm: BenchmarkNorm) -> str:
    return f"{norm.age_min}-{norm.age_max}" if norm.age_max < 100 else f"{norm.age_min}+"


class NormTable:
    """All norms loaded once per request (the table is tiny) so many athletes can be scored quickly."""

    def __init__(self, norms: list[BenchmarkNorm]):
        self._norms = norms

    @classmethod
    def load(cls, db: Session) -> "NormTable":
        return cls(list(db.scalars(select(BenchmarkNorm))))

    def _row(self, test_type: str, gender: str, age: int) -> BenchmarkNorm | None:
        rows = [n for n in self._norms if n.test_type == test_type and n.gender == gender]
        for n in rows:
            if n.age_min <= age <= n.age_max:
                return n
        if rows:  # age outside every band: use the closest band
            return min(rows, key=lambda n: min(abs(age - n.age_min), abs(age - n.age_max)))
        return None

    def anchors(self, test_type: str, gender: str, age: int) -> Anchors | None:
        if gender in ("male", "female"):
            n = self._row(test_type, gender, age)
            if n is None:
                return None
            return Anchors(n.p10, n.p25, n.p50, n.p75, n.p90,
                           f"{TEST_LABELS.get(test_type, test_type)} norm, {gender}, age {_band_label(n)}")
        m, f = self._row(test_type, "male", age), self._row(test_type, "female", age)
        if m is None or f is None:
            return None
        avg = lambda k: round((getattr(m, k) + getattr(f, k)) / 2, 2)  # noqa: E731
        return Anchors(avg("p10"), avg("p25"), avg("p50"), avg("p75"), avg("p90"),
                       f"{TEST_LABELS.get(test_type, test_type)} norm, male/female average, age {_band_label(m)}")

    def evaluate(self, test_type: str, gender: str, age: int, value: float) -> dict | None:
        """Returns {percentile, level, norm_reference, median} or None when no norm exists."""
        a = self.anchors(test_type, gender, age)
        if a is None:
            return None
        pct = percentile_from_anchors(value, a)
        return {"percentile": pct, "level": level_for(pct), "norm_reference": a.reference, "median": a.p50}

    def all_rows(self) -> list[BenchmarkNorm]:
        return sorted(self._norms, key=lambda n: (n.test_type, n.gender, n.age_min))


def apply_benchmark(db: Session, result, athlete, norms: "NormTable | None" = None) -> bool:
    """Fill the benchmark_* columns of one TestResult row. Returns False when no norm exists.

    Optional hook for the AI/upload flow: call it right after a result is saved,
    e.g. in ai_service.run_analysis:   apply_benchmark(db, result, submission.athlete)
    (The admin endpoint POST /api/benchmarks/recalculate does the same for existing rows.)
    """
    norms = norms or NormTable.load(db)
    evaluation = norms.evaluate(result.test_type, athlete.gender, age_on(athlete.date_of_birth), result.value)
    if evaluation is None:
        return False
    result.benchmark_percentile = evaluation["percentile"]
    result.benchmark_category = evaluation["level"]
    result.norm_reference = evaluation["norm_reference"][:255]
    return True

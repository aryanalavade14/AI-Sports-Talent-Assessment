"""Admin/SAI dashboard logic: filtered athlete rows, summary, leaderboard, shortlist.

All numbers come from the real tables (athletes, test_results, benchmark_norms, shortlisted_athletes).
Percentiles are calculated on the fly from the norm table, so editing a norm updates the dashboard.

Rules worth knowing:
  * An athlete's score for a test is their BEST result for that test.
  * Results marked "flagged" (cheat detection) or "rejected" are NOT used for scores or ranking;
    they are only counted in `flagged_results` so admins can see them.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.athlete import Athlete
from app.models.shortlist import Shortlist
from app.models.test_result import VERIFICATION_FLAGGED, VERIFICATION_REJECTED, TestResult
from app.services.benchmark_service import LEVEL_ORDER, NormTable, age_on, level_for

TESTS = ("vertical_jump", "sit_up")
EXCLUDED = (VERIFICATION_FLAGGED, VERIFICATION_REJECTED)


@dataclass
class Filters:
    region: str | None = None
    sport: str | None = None
    gender: str | None = None
    age_min: int | None = None
    age_max: int | None = None
    athlete_id: object = None  # internal: score a single athlete only


def _clean(text: str | None) -> str | None:
    text = (text or "").strip()
    return text.title() if text else None


def _years_ago(years: int) -> date:
    today = date.today()
    try:
        return today.replace(year=today.year - years)
    except ValueError:  # 29 Feb
        return today.replace(year=today.year - years, day=28)


def _athlete_query(f: Filters):
    q = select(Athlete)
    if f.athlete_id:
        q = q.where(Athlete.id == f.athlete_id)
    if f.region:
        q = q.where(func.lower(func.trim(func.coalesce(Athlete.state, Athlete.city))) == f.region.strip().lower())
    if f.sport:
        q = q.where(func.lower(func.trim(Athlete.sport)) == f.sport.strip().lower())
    if f.gender:
        q = q.where(Athlete.gender == f.gender)
    if f.age_min is not None:  # at least N years old -> born on/before this date
        q = q.where(Athlete.date_of_birth <= _years_ago(f.age_min))
    if f.age_max is not None:  # at most N years old -> born after this date
        q = q.where(Athlete.date_of_birth > _years_ago(f.age_max + 1))
    return q


def athlete_rows(db: Session, f: Filters) -> list[dict]:
    athletes = list(db.scalars(_athlete_query(f).order_by(Athlete.name)))
    if not athletes:
        return []
    ids = [a.id for a in athletes]
    results = defaultdict(list)
    for r in db.scalars(select(TestResult).where(TestResult.athlete_id.in_(ids))):
        results[r.athlete_id].append(r)
    shortlisted = set(db.scalars(select(Shortlist.athlete_id).where(Shortlist.athlete_id.in_(ids))))
    norms = NormTable.load(db)

    rows = []
    for a in athletes:
        age = age_on(a.date_of_birth)
        row = {
            "athlete_id": a.id, "name": a.name, "age": age, "gender": a.gender, "sport": _clean(a.sport),
            "state": _clean(a.state), "city": _clean(a.city), "region": _clean(a.state) or _clean(a.city),
            "vertical_jump": None, "sit_up": None, "tests_taken": 0, "overall_percentile": None,
            "overall_level": None, "shortlisted": a.id in shortlisted,
            "flagged_results": sum(1 for r in results[a.id] if r.verification_status in EXCLUDED),
        }
        percentiles = []
        for test in TESTS:
            valid = [r for r in results[a.id] if r.test_type == test and r.verification_status not in EXCLUDED]
            if not valid:
                continue
            best = max(valid, key=lambda r: r.value)
            ev = norms.evaluate(test, a.gender, age, best.value)
            row[test] = {
                "result_id": best.id, "value": best.value, "unit": best.unit, "tested_at": best.created_at,
                "percentile": ev["percentile"] if ev else None, "level": ev["level"] if ev else None,
                "norm_reference": ev["norm_reference"] if ev else None, "norm_median": ev["median"] if ev else None,
            }
            row["tests_taken"] += 1
            if ev:
                percentiles.append(ev["percentile"])
        if percentiles:
            row["overall_percentile"] = round(sum(percentiles) / len(percentiles), 1)
            row["overall_level"] = level_for(row["overall_percentile"])
        rows.append(row)
    return rows


def _mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 1) if values else None


def summary(db: Session, f: Filters) -> dict:
    rows = athlete_rows(db, f)
    ids = [r["athlete_id"] for r in rows]
    total_results = (
        db.scalar(select(func.count()).select_from(TestResult).where(TestResult.athlete_id.in_(ids))) if ids else 0
    )
    scored = [r for r in rows if r["overall_percentile"] is not None]

    levels = Counter(r["overall_level"] for r in scored)
    regions = Counter(r["region"] or "Unknown" for r in rows)
    genders = Counter(r["gender"].title() for r in rows)

    sport_pcts = defaultdict(list)
    for r in scored:
        sport_pcts[r["sport"] or "Unspecified"].append(r["overall_percentile"])

    return {
        "total_athletes": len(rows),
        "athletes_tested": sum(1 for r in rows if r["tests_taken"] > 0),
        "total_results": total_results or 0,
        "shortlisted": sum(1 for r in rows if r["shortlisted"]),
        "flagged_results": sum(r["flagged_results"] for r in rows),
        "average_percentile": _mean([r["overall_percentile"] for r in scored]),
        "average_vertical_jump_cm": _mean([r["vertical_jump"]["value"] for r in rows if r["vertical_jump"]]),
        "average_sit_ups": _mean([r["sit_up"]["value"] for r in rows if r["sit_up"]]),
        "levels": [{"label": name, "count": levels.get(name, 0)} for name in LEVEL_ORDER],
        "by_region": [{"label": k, "count": v} for k, v in regions.most_common(8)],
        "by_sport": sorted(
            ({"label": k, "average_percentile": _mean(v), "athletes": len(v)} for k, v in sport_pcts.items()),
            key=lambda x: -x["average_percentile"],
        )[:8],
        "by_gender": [{"label": k, "count": v} for k, v in genders.most_common()],
    }


def leaderboard(db: Session, f: Filters, test: str = "overall", limit: int = 50) -> list[dict]:
    rows = athlete_rows(db, f)
    if test == "overall":
        ranked = [r for r in rows if r["overall_percentile"] is not None]
        ranked.sort(key=lambda r: (-r["overall_percentile"], -r["tests_taken"], r["name"]))
    else:
        ranked = [r for r in rows if r[test] and r[test]["percentile"] is not None]
        ranked.sort(key=lambda r: (-r[test]["percentile"], -r[test]["value"], r["name"]))
    return [{**r, "rank": i} for i, r in enumerate(ranked[:limit], start=1)]


def filter_options(db: Session) -> dict:
    athletes = list(db.execute(select(Athlete.state, Athlete.city, Athlete.sport, Athlete.gender, Athlete.date_of_birth)))
    ages = [age_on(a.date_of_birth) for a in athletes]
    return {
        "regions": sorted({_clean(a.state) or _clean(a.city) for a in athletes} - {None}),
        "sports": sorted({_clean(a.sport) for a in athletes} - {None}),
        "genders": sorted({a.gender for a in athletes}),
        "age_min": min(ages) if ages else None,
        "age_max": max(ages) if ages else None,
    }

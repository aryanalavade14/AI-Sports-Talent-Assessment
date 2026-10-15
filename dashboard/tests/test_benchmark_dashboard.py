"""Tests for Part 4: benchmarking, percentile, dashboard endpoints, filters, leaderboard, shortlist.

Norm rows come from migration 0002's default table, so the tests load them into the in-memory DB first.
"""
import uuid
from datetime import date, datetime, timezone

import pytest

from app.data.default_norms import SOURCE, default_rows
from app.models.athlete import Athlete
from app.models.benchmark_norm import BenchmarkNorm
from app.models.test_result import TestResult
from app.models.test_submission import TestSubmission
from app.models.user import User
from app.services.benchmark_service import Anchors, level_for, percentile_from_anchors
from app.utils.security import hash_password
from tests.conftest import PASSWORD, make_admin_headers, register_and_login


# ---------- pure percentile maths ----------
A = Anchors(20, 25, 30, 36, 42, "x")


def test_percentile_hits_anchor_points():
    assert percentile_from_anchors(20, A) == 10
    assert percentile_from_anchors(30, A) == 50
    assert percentile_from_anchors(42, A) == 90


def test_percentile_interpolates_and_clamps():
    assert percentile_from_anchors(27.5, A) == 37.5  # halfway between p25 and p50
    assert percentile_from_anchors(0, A) == 1  # never below 1
    assert percentile_from_anchors(500, A) == 99  # never above 99


def test_levels():
    assert [level_for(p) for p in (1, 20, 40, 60, 80, 99)] == [
        "Needs Improvement", "Developing", "Average", "Good", "Excellent", "Excellent"]


# ---------- helpers ----------
@pytest.fixture()
def seeded(session_factory):
    with session_factory() as db:
        for (t, g, unit, lo, hi, p10, p25, p50, p75, p90) in default_rows():
            db.add(BenchmarkNorm(test_type=t, gender=g, unit=unit, age_min=lo, age_max=hi,
                                 p10=p10, p25=p25, p50=p50, p75=p75, p90=p90, source=SOURCE))
        db.commit()
    return session_factory


def born(age: int) -> date:
    """A birth date that makes the athlete exactly `age` today (tests must not depend on the calendar year)."""
    t = date.today()
    return t.replace(year=t.year - age, day=1) if t.day > 28 else t.replace(year=t.year - age)


def add_athlete(sf, name, gender="male", dob=None, state="Maharashtra", city="Pune", sport="athletics"):
    dob = dob or born(17)
    with sf() as db:
        user = User(email=f"{uuid.uuid4().hex[:8]}@example.com", hashed_password=hash_password(PASSWORD))
        db.add(user)
        db.flush()
        a = Athlete(user_id=user.id, name=name, gender=gender, date_of_birth=dob, state=state, city=city, sport=sport)
        db.add(a)
        db.commit()
        return str(a.id)


def add_result(sf, athlete_id, test_type, value, status="pending"):
    unit = "cm" if test_type == "vertical_jump" else "reps"
    with sf() as db:
        sub = TestSubmission(athlete_id=uuid.UUID(athlete_id), test_type=test_type, status="completed",
                             video_path="x.mp4", video_size_bytes=1)
        db.add(sub)
        db.flush()
        db.add(TestResult(submission_id=sub.id, athlete_id=uuid.UUID(athlete_id), test_type=test_type,
                          value=value, unit=unit, verification_status=status,
                          jump_height_cm=value if test_type == "vertical_jump" else None,
                          rep_count=int(value) if test_type == "sit_up" else None))
        db.commit()


@pytest.fixture()
def admin(client, seeded):
    return make_admin_headers(client, seeded)


# ---------- access control ----------
def test_dashboard_is_admin_only(client, seeded):
    assert client.get("/api/admin/athletes").status_code == 401
    athlete_headers = register_and_login(client)
    assert client.get("/api/admin/athletes", headers=athlete_headers).status_code == 403
    assert client.get("/api/admin/summary", headers=athlete_headers).status_code == 403
    assert client.put(f"/api/admin/shortlist/{uuid.uuid4()}", headers=athlete_headers).status_code == 403
    assert client.post("/api/benchmarks/recalculate", headers=athlete_headers).status_code == 403


# ---------- benchmarking ----------
def test_norms_and_evaluate_endpoints(client, seeded):
    h = register_and_login(client)
    norms = client.get("/api/benchmarks/norms", headers=h).json()
    assert len(norms) == 24  # 2 tests x 2 genders x 6 age bands
    assert all(n["test_type"] == "sit_up" for n in client.get("/api/benchmarks/norms?test_type=sit_up", headers=h).json())

    r = client.get("/api/benchmarks/evaluate", headers=h,
                   params={"test_type": "vertical_jump", "gender": "male", "age": 17, "value": 45})
    assert r.status_code == 200
    assert r.json()["percentile"] == 50 and r.json()["level"] == "Average"

    other = client.get("/api/benchmarks/evaluate", headers=h,
                       params={"test_type": "vertical_jump", "gender": "other", "age": 17, "value": 41.5}).json()
    assert other["median"] == 38.5 and "average" in other["norm_reference"]  # mean of 45 and 32


def test_same_score_different_percentile_by_gender_and_age(client, seeded):
    h = register_and_login(client)
    get = lambda **p: client.get("/api/benchmarks/evaluate", headers=h, params={  # noqa: E731
        "test_type": "sit_up", "value": 30, **p}).json()["percentile"]
    assert get(gender="female", age=17) > get(gender="male", age=17)   # same reps, higher vs. female norm
    assert get(gender="male", age=11) > get(gender="male", age=17)     # same reps, higher vs. younger norm


def test_evaluate_validation(client, seeded):
    h = register_and_login(client)
    base = {"test_type": "sit_up", "gender": "male", "age": 17, "value": 30}
    assert client.get("/api/benchmarks/evaluate", headers=h, params={**base, "gender": "robot"}).status_code == 422
    assert client.get("/api/benchmarks/evaluate", headers=h, params={**base, "test_type": "swim"}).status_code == 422
    assert client.get("/api/benchmarks/evaluate", params=base).status_code == 401


# ---------- athlete rows ----------
def test_athlete_rows_use_best_clean_result(client, seeded, admin):
    a = add_athlete(seeded, "Asha Patil", gender="female", dob=born(16))
    add_result(seeded, a, "vertical_jump", 28)
    add_result(seeded, a, "vertical_jump", 33)                    # best clean
    add_result(seeded, a, "vertical_jump", 80, status="flagged")  # cheat-flagged: must be ignored
    add_result(seeded, a, "sit_up", 24)
    rows = client.get("/api/admin/athletes", headers=admin).json()
    assert len(rows) == 1
    row = rows[0]
    assert row["vertical_jump"]["value"] == 33 and row["sit_up"]["value"] == 24
    assert row["flagged_results"] == 1 and row["tests_taken"] == 2
    assert row["vertical_jump"]["percentile"] is not None and row["overall_percentile"] is not None
    assert row["region"] == "Maharashtra" and row["gender"] == "female"


def test_athlete_without_results_is_listed_but_unranked(client, seeded, admin):
    add_athlete(seeded, "No Tests")
    row = client.get("/api/admin/athletes", headers=admin).json()[0]
    assert row["tests_taken"] == 0 and row["overall_percentile"] is None
    assert client.get("/api/admin/leaderboard", headers=admin).json() == []


# ---------- filters ----------
def make_cohort(sf):
    ids = {
        "ravi": add_athlete(sf, "Ravi", "male", born(18), "Maharashtra", "Pune", "Athletics"),
        "asha": add_athlete(sf, "Asha", "female", born(15), "Gujarat", "Surat", "Kabaddi"),
        "kiran": add_athlete(sf, "Kiran", "male", born(26), "maharashtra", "Mumbai", "athletics"),
    }
    add_result(sf, ids["ravi"], "vertical_jump", 50)
    add_result(sf, ids["asha"], "vertical_jump", 25)
    add_result(sf, ids["kiran"], "sit_up", 30)
    return ids


def names(r):
    return sorted(x["name"] for x in r.json())


def test_filters(client, seeded, admin):
    make_cohort(seeded)
    get = lambda **p: client.get("/api/admin/athletes", headers=admin, params=p)  # noqa: E731
    assert names(get()) == ["Asha", "Kiran", "Ravi"]
    assert names(get(region="Maharashtra")) == ["Kiran", "Ravi"]        # case-insensitive, one region
    assert names(get(region="maharashtra")) == ["Kiran", "Ravi"]
    assert names(get(sport="kabaddi")) == ["Asha"]
    assert names(get(gender="female")) == ["Asha"]
    assert names(get(age_min=20)) == ["Kiran"]
    assert names(get(age_max=16)) == ["Asha"]
    assert names(get(age_min=16, age_max=20)) == ["Ravi"]
    assert names(get(age_min=15, age_max=18)) == ["Asha", "Ravi"]  # both ends inclusive
    assert names(get(region="Maharashtra", gender="male", sport="Athletics", age_max=18)) == ["Ravi"]
    assert get(gender="robot").status_code == 422

    opts = client.get("/api/admin/filters", headers=admin).json()
    assert opts["regions"] == ["Gujarat", "Maharashtra"]   # case variants merged
    assert opts["sports"] == ["Athletics", "Kabaddi"] and opts["genders"] == ["female", "male"]
    assert opts["age_min"] < opts["age_max"]


# ---------- summary + charts ----------
def test_summary(client, seeded, admin):
    ids = make_cohort(seeded)
    add_result(seeded, ids["ravi"], "vertical_jump", 99, status="flagged")
    s = client.get("/api/admin/summary", headers=admin).json()
    assert s["total_athletes"] == 3 and s["athletes_tested"] == 3
    assert s["total_results"] == 4 and s["flagged_results"] == 1
    assert sum(x["count"] for x in s["levels"]) == 3
    assert {x["label"]: x["count"] for x in s["by_region"]} == {"Maharashtra": 2, "Gujarat": 1}
    assert s["average_vertical_jump_cm"] == 37.5 and s["average_sit_ups"] == 30
    assert {x["label"] for x in s["by_sport"]} == {"Athletics", "Kabaddi"}
    assert s["average_percentile"] is not None

    filtered = client.get("/api/admin/summary", headers=admin, params={"gender": "female"}).json()
    assert filtered["total_athletes"] == 1 and filtered["total_results"] == 1


def test_summary_empty_database(client, seeded, admin):
    s = client.get("/api/admin/summary", headers=admin).json()
    assert s["total_athletes"] == 0 and s["average_percentile"] is None and s["by_region"] == []


# ---------- leaderboard ----------
def test_leaderboard_ranks_by_percentile(client, seeded, admin):
    ids = make_cohort(seeded)
    add_result(seeded, ids["kiran"], "vertical_jump", 40)
    lb = client.get("/api/admin/leaderboard", headers=admin).json()
    assert [r["rank"] for r in lb] == [1, 2, 3]
    pcts = [r["overall_percentile"] for r in lb]
    assert pcts == sorted(pcts, reverse=True)

    jump = client.get("/api/admin/leaderboard", headers=admin, params={"test": "vertical_jump"}).json()
    assert {r["name"] for r in jump} == {"Ravi", "Asha", "Kiran"}
    p = [r["vertical_jump"]["percentile"] for r in jump]
    assert p == sorted(p, reverse=True)

    situp = client.get("/api/admin/leaderboard", headers=admin, params={"test": "sit_up"}).json()
    assert [r["name"] for r in situp] == ["Kiran"]
    assert len(client.get("/api/admin/leaderboard", headers=admin, params={"limit": 1}).json()) == 1
    only_f = client.get("/api/admin/leaderboard", headers=admin, params={"gender": "female"}).json()
    assert [r["name"] for r in only_f] == ["Asha"] and only_f[0]["rank"] == 1


# ---------- shortlist ----------
def test_shortlist_add_note_list_remove(client, seeded, admin):
    ids = make_cohort(seeded)
    r = client.put(f"/api/admin/shortlist/{ids['ravi']}", headers=admin, json={"note": "Great explosive power"})
    assert r.status_code == 200 and r.json()["athlete"]["shortlisted"] is True
    assert r.json()["note"] == "Great explosive power"

    assert client.put(f"/api/admin/shortlist/{ids['ravi']}", headers=admin).status_code == 200  # idempotent
    listed = client.get("/api/admin/shortlist", headers=admin).json()
    assert len(listed) == 1 and listed[0]["note"] == "Great explosive power"

    rows = {x["name"]: x for x in client.get("/api/admin/athletes", headers=admin).json()}
    assert rows["Ravi"]["shortlisted"] and not rows["Asha"]["shortlisted"]
    assert client.get("/api/admin/summary", headers=admin).json()["shortlisted"] == 1

    assert client.delete(f"/api/admin/shortlist/{ids['ravi']}", headers=admin).status_code == 204
    assert client.delete(f"/api/admin/shortlist/{ids['ravi']}", headers=admin).status_code == 204  # idempotent
    assert client.get("/api/admin/shortlist", headers=admin).json() == []


def test_shortlist_unknown_athlete(client, seeded, admin):
    assert client.put(f"/api/admin/shortlist/{uuid.uuid4()}", headers=admin).status_code == 404


# ---------- saving percentiles into test_results ----------
def test_recalculate_fills_result_columns(client, seeded, admin):
    ids = make_cohort(seeded)
    assert client.post("/api/benchmarks/recalculate", headers=admin).json() == {"updated": 3, "skipped_no_norm": 0}
    h = register_and_login(client, "viewer@example.com")  # athlete accounts can't read others, so check via DB
    with seeded() as db:
        res = db.query(TestResult).filter(TestResult.athlete_id == uuid.UUID(ids["ravi"])).one()
        assert res.benchmark_percentile is not None and res.benchmark_category
        assert "Vertical Jump norm, male" in res.norm_reference
    assert h  # silence unused

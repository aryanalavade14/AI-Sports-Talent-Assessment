"""Response models for the benchmarking + admin dashboard endpoints."""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TestScore(BaseModel):
    __test__ = False
    result_id: uuid.UUID
    value: float
    unit: str
    percentile: float | None = None  # None when no norm exists for this athlete
    level: str | None = None
    norm_reference: str | None = None
    norm_median: float | None = None  # typical (50th percentile) score for this athlete's age/gender
    tested_at: datetime


class AthleteRow(BaseModel):
    athlete_id: uuid.UUID
    name: str
    age: int
    gender: str
    sport: str | None
    state: str | None
    city: str | None
    region: str | None
    vertical_jump: TestScore | None = None
    sit_up: TestScore | None = None
    tests_taken: int
    overall_percentile: float | None = None
    overall_level: str | None = None
    flagged_results: int = 0
    shortlisted: bool = False


class LeaderboardRow(AthleteRow):
    rank: int


class CountItem(BaseModel):
    label: str
    count: int


class AvgItem(BaseModel):
    label: str
    average_percentile: float
    athletes: int


class Summary(BaseModel):
    total_athletes: int
    athletes_tested: int
    total_results: int
    shortlisted: int
    flagged_results: int
    average_percentile: float | None
    average_vertical_jump_cm: float | None
    average_sit_ups: float | None
    levels: list[CountItem]
    by_region: list[CountItem]
    by_sport: list[AvgItem]
    by_gender: list[CountItem]


class FilterOptions(BaseModel):
    regions: list[str]
    sports: list[str]
    genders: list[str]
    age_min: int | None
    age_max: int | None


class ShortlistIn(BaseModel):
    note: str | None = Field(default=None, max_length=500)


class ShortlistOut(BaseModel):
    athlete: AthleteRow
    note: str | None
    shortlisted_at: datetime


class NormOut(BaseModel):
    test_type: str
    gender: str
    age_min: int
    age_max: int
    unit: str
    p10: float
    p25: float
    p50: float
    p75: float
    p90: float
    source: str


class EvaluateOut(BaseModel):
    test_type: str
    gender: str
    age: int
    value: float
    percentile: float
    level: str
    norm_reference: str
    median: float


class RecalculateOut(BaseModel):
    updated: int
    skipped_no_norm: int

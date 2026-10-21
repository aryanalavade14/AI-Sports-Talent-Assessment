import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TestType(str, Enum):
    vertical_jump = "vertical_jump"
    sit_up = "sit_up"


class TestResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    submission_id: uuid.UUID
    athlete_id: uuid.UUID
    test_type: str
    value: float
    unit: str
    confidence: float | None
    jump_height_cm: float | None
    rep_count: int | None
    benchmark_percentile: float | None
    benchmark_category: str | None
    norm_reference: str | None
    verification_status: str
    created_at: datetime


class SubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_submission_id: uuid.UUID | None
    athlete_id: uuid.UUID
    test_type: str
    status: str
    error_message: str | None
    video_path: str
    video_original_name: str | None
    video_content_type: str | None
    video_size_bytes: int
    video_duration_seconds: float | None
    recorded_at: datetime | None
    sensor_data: dict | None
    cheat_flag: bool
    cheat_reasons: list[str] | None
    created_at: datetime
    updated_at: datetime
    result: TestResultOut | None = None


class SubmissionSummary(BaseModel):
    """Compact row used in the athlete history list."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    test_type: str
    status: str
    cheat_flag: bool
    cheat_reasons: list[str] | None
    recorded_at: datetime | None
    created_at: datetime
    result: TestResultOut | None = None


# ---- What the AI engine must return (validated before saving) ----
class VerticalJumpAIResult(BaseModel):
    jump_height_cm: float = Field(ge=0, le=300)
    value: float = Field(ge=0)
    unit: str = "cm"
    confidence: float = Field(ge=0, le=1)
    benchmark_percentile: float | None = Field(default=None, ge=0, le=100)
    benchmark_category: str | None = None
    norm_reference: str | None = None


class SitUpAIResult(BaseModel):
    rep_count: int = Field(ge=0, le=500)
    value: float = Field(ge=0)
    unit: str = "reps"
    confidence: float = Field(ge=0, le=1)
    benchmark_percentile: float | None = Field(default=None, ge=0, le=100)
    benchmark_category: str | None = None
    norm_reference: str | None = None

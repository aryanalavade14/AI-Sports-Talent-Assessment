import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.test import TestResultOut, TestType


class SyncItem(BaseModel):
    """One offline-recorded test, sent as JSON inside a batch."""

    client_submission_id: uuid.UUID
    athlete_id: uuid.UUID
    test_type: TestType
    recorded_at: datetime | None = None
    duration_seconds: float | None = None
    sensor_data: dict | None = None
    video_filename: str = Field(description="e.g. jump1.mp4")
    video_base64: str = Field(description="Video file content, base64 encoded")


class SyncBatchRequest(BaseModel):
    items: list[SyncItem] = Field(min_length=1, max_length=50)


class SyncItemResult(BaseModel):
    client_submission_id: uuid.UUID
    success: bool
    status: Literal["created", "duplicate", "failed"]
    submission_id: uuid.UUID | None = None
    submission_status: str | None = None
    error: str | None = None


class SyncBatchResponse(BaseModel):
    total: int
    succeeded: int
    duplicates: int
    failed: int
    results: list[SyncItemResult]


class SyncStatusOut(BaseModel):
    client_submission_id: uuid.UUID
    status: Literal["synced", "failed"]
    attempts: int
    submission_id: uuid.UUID | None
    submission_status: str | None
    cheat_flag: bool | None
    error_message: str | None
    last_attempt_at: datetime
    result: TestResultOut | None = None

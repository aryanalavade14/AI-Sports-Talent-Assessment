"""Interface to the AI / computer-vision engine (built by a teammate with MediaPipe Pose).

The backend does NOT run MediaPipe. It only:
  1. sends the video + test info to the AI engine (or generates a MOCK result), and
  2. validates and stores whatever the engine returns.

--- Contract with the AI engine (when MOCK_AI=false) ---
POST {AI_ENGINE_URL}   (multipart/form-data)
    file          the video file
    test_type     "vertical_jump" | "sit_up"
    submission_id UUID string
    sensor_data   JSON string (may be empty)
Response 200 JSON:
    vertical_jump -> {"jump_height_cm": 42.5, "value": 42.5, "unit": "cm", "confidence": 0.91}
    sit_up        -> {"rep_count": 28, "value": 28, "unit": "reps", "confidence": 0.88}
Optional extra keys the benchmarking teammate may add:
    benchmark_percentile, benchmark_category, norm_reference
"""
import json
import logging
import random

import httpx
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.test_result import (
    VERIFICATION_FLAGGED,
    VERIFICATION_PENDING,
    TestResult,
)
from app.models.test_submission import (
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_PROCESSING,
    TestSubmission,
)
from app.schemas.test import SitUpAIResult, VerticalJumpAIResult
from app.services.storage_service import get_storage

logger = logging.getLogger("app.ai")
AI_TIMEOUT_SECONDS = 120


class AIServiceError(Exception):
    pass


# ---------- Mock AI (MOCK_AI=true) ----------
def _mock_result(submission: TestSubmission) -> dict:
    # Seeded by the submission id so the same submission gives the same fake result.
    rng = random.Random(str(submission.id))
    confidence = round(rng.uniform(0.80, 0.98), 2)
    if submission.test_type == "vertical_jump":
        height = round(rng.uniform(25, 60), 1)
        return {"jump_height_cm": height, "value": height, "unit": "cm", "confidence": confidence}
    reps = rng.randint(15, 45)
    return {"rep_count": reps, "value": reps, "unit": "reps", "confidence": confidence}


# ---------- Real AI engine call ----------

def _call_ai_engine(
    submission: TestSubmission,
    height_cm: float,
) -> dict:
    settings = get_settings()
    video_path = get_storage().absolute_path(submission.video_path)

    try:
        with open(video_path, "rb") as video:
            response = httpx.post(
                settings.AI_ENGINE_URL,
                files={
                    "video": (
                        submission.video_original_name or "video.mp4",
                        video,
                    )
                },
                data={"height_cm": str(height_cm)},
                timeout=AI_TIMEOUT_SECONDS,
            )

        response.raise_for_status()
        payload = response.json()

        if payload.get("status") != "ok":
            raise AIServiceError(
                payload.get("message", "CV engine analysis failed")
            )

        jump_cm = float(payload["jump_cm"])

        return {
            "jump_height_cm": jump_cm,
            "value": jump_cm,
            "unit": "cm",
            "confidence": 1.0,
        }

    except FileNotFoundError:
        raise AIServiceError("Video file not found on disk")
    except httpx.HTTPError as exc:
        raise AIServiceError(f"AI engine request failed: {exc}")
    except (ValueError, TypeError, KeyError) as exc:
        raise AIServiceError(f"Invalid CV engine response: {exc}")



def parse_ai_response(test_type: str, payload: dict):
    """Validate the AI engine output. Returns a validated pydantic object."""
    model = VerticalJumpAIResult if test_type == "vertical_jump" else SitUpAIResult
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise AIServiceError(f"AI engine returned an unexpected response: {exc.errors()[:3]}")


def run_analysis(
    db: Session,
    submission: TestSubmission,
    height_cm: float | None = None,
) -> TestResult:
    """Run (or mock) the AI analysis and save the result. Raises AIServiceError on failure."""
    settings = get_settings()
    submission.status = STATUS_PROCESSING
    submission.error_message = None
    db.commit()

    try:
        payload = (
            _mock_result(submission)
            if settings.MOCK_AI
            else _call_ai_engine(submission, height_cm)
        )
        parsed = parse_ai_response(submission.test_type, payload)
    except AIServiceError as exc:
        logger.warning("AI analysis failed for %s: %s", submission.id, exc)
        submission.status = STATUS_FAILED
        submission.error_message = str(exc)
        db.commit()
        raise

    # Create or update the single result row for this submission
    result = submission.result or TestResult(
        submission_id=submission.id, athlete_id=submission.athlete_id, test_type=submission.test_type
    )
    result.value = parsed.value
    result.unit = parsed.unit
    result.confidence = parsed.confidence
    result.jump_height_cm = getattr(parsed, "jump_height_cm", None)
    result.rep_count = getattr(parsed, "rep_count", None)
    result.benchmark_percentile = parsed.benchmark_percentile
    result.benchmark_category = parsed.benchmark_category
    result.norm_reference = parsed.norm_reference
    result.raw_ai_response = payload
    result.verification_status = VERIFICATION_FLAGGED if submission.cheat_flag else VERIFICATION_PENDING

    submission.status = STATUS_COMPLETED
    db.add(result)
    db.commit()
    db.refresh(submission)
    return result

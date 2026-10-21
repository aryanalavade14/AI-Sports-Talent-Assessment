"""Basic cheat detection.

This is simple rule-based validation, NOT advanced forensic fraud detection.
It only raises a flag (and stores human-readable reason codes) so a person
can review suspicious submissions later.
"""
import math
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.models.test_submission import TEST_TYPES

# ---- Tunable thresholds ----
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
MIN_VIDEO_BYTES = 10 * 1024  # smaller than 10 KB is almost certainly not a real video
MIN_DURATION_SECONDS = 1.0
MAX_DURATION_SECONDS = 180.0
MAX_FUTURE_SKEW = timedelta(minutes=5)  # allow small phone clock errors
MAX_AGE = timedelta(days=30)  # offline tests older than this look suspicious
MIN_SENSOR_SAMPLES = 5
MAX_ACCEL_STD = 30.0  # m/s^2, standard deviation of acceleration magnitude
MAX_GYRO_STD = 15.0  # rad/s, standard deviation of rotation-rate magnitude


def _to_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def _looks_like_video(header: bytes, extension: str) -> bool:
    """Check the first bytes of the file against the expected container signature."""
    if extension in {".mp4", ".mov"}:
        return header[4:8] == b"ftyp"
    if extension in {".mkv", ".webm"}:
        return header[:4] == b"\x1a\x45\xdf\xa3"
    if extension == ".avi":
        return header[:4] == b"RIFF" and header[8:12] == b"AVI "
    return False


def _magnitudes(samples) -> list[float]:
    """Accepts [{"x":..,"y":..,"z":..}, ...] or [[x, y, z], ...]."""
    result = []
    if not isinstance(samples, list):
        return result
    for sample in samples:
        if isinstance(sample, dict):
            values = [sample.get("x"), sample.get("y"), sample.get("z")]
        elif isinstance(sample, (list, tuple)) and len(sample) >= 3:
            values = list(sample[:3])
        else:
            continue
        try:
            x, y, z = (float(v) for v in values)
        except (TypeError, ValueError):
            continue
        result.append(math.sqrt(x * x + y * y + z * z))
    return result


def check_sensor_data(sensor_data) -> list[str]:
    reasons = []
    if not isinstance(sensor_data, dict) or not sensor_data:
        return ["missing_sensor_data"]
    accel = _magnitudes(sensor_data.get("accelerometer"))
    gyro = _magnitudes(sensor_data.get("gyroscope"))
    if len(accel) < MIN_SENSOR_SAMPLES and len(gyro) < MIN_SENSOR_SAMPLES:
        return ["missing_sensor_data"]
    if len(accel) >= MIN_SENSOR_SAMPLES and statistics.pstdev(accel) > MAX_ACCEL_STD:
        reasons.append("excessive_accelerometer_variation")
    if len(gyro) >= MIN_SENSOR_SAMPLES and statistics.pstdev(gyro) > MAX_GYRO_STD:
        reasons.append("excessive_gyroscope_variation")
    return reasons


def run_cheat_checks(
    *,
    file_path: Path | None,
    file_size: int,
    test_type: str,
    recorded_at: datetime | None,
    duration_seconds: float | None,
    sensor_data,
    sensor_data_valid: bool = True,
) -> tuple[bool, list[str]]:
    """Return (cheat_flag, reasons)."""
    reasons: list[str] = []

    # 1. File checks: unsupported / invalid / empty / tiny
    if file_path is not None:
        ext = file_path.suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            reasons.append("unsupported_file_type")
        else:
            try:
                with open(file_path, "rb") as f:
                    header = f.read(16)
            except OSError:
                header = b""
            if file_size > 0 and not _looks_like_video(header, ext):
                reasons.append("invalid_video_file")
    if file_size == 0:
        reasons.append("empty_file")
    elif file_size < MIN_VIDEO_BYTES:
        reasons.append("tiny_file")

    # 2. Metadata checks: missing / invalid
    if test_type not in TEST_TYPES:
        reasons.append("invalid_metadata")
    if recorded_at is None or duration_seconds is None:
        reasons.append("missing_metadata")
    if not sensor_data_valid:
        reasons.append("invalid_metadata")

    # 3. Suspicious timestamp
    if recorded_at is not None:
        now = datetime.now(timezone.utc)
        ts = _to_utc(recorded_at)
        if ts > now + MAX_FUTURE_SKEW:
            reasons.append("timestamp_in_future")
        elif ts < now - MAX_AGE:
            reasons.append("timestamp_too_old")

    # 4. Invalid duration
    if duration_seconds is not None and (
        math.isnan(duration_seconds)
        or duration_seconds < MIN_DURATION_SECONDS
        or duration_seconds > MAX_DURATION_SECONDS
    ):
        reasons.append("invalid_duration")

    # 5. Sensor data: missing / excessive variation
    reasons.extend(check_sensor_data(sensor_data))

    unique = list(dict.fromkeys(reasons))  # remove duplicates, keep order
    return bool(unique), unique

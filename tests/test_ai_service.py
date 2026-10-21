import pytest

from app.services.ai_service import AIServiceError, parse_ai_response


def test_parse_vertical_jump_ok():
    parsed = parse_ai_response(
        "vertical_jump", {"jump_height_cm": 41.2, "value": 41.2, "unit": "cm", "confidence": 0.9}
    )
    assert parsed.jump_height_cm == 41.2


def test_parse_sit_up_ok():
    parsed = parse_ai_response("sit_up", {"rep_count": 30, "value": 30, "unit": "reps", "confidence": 0.8})
    assert parsed.rep_count == 30


def test_parse_rejects_bad_payloads():
    with pytest.raises(AIServiceError):
        parse_ai_response("vertical_jump", {"jump_height_cm": -5, "value": 1, "confidence": 0.5})
    with pytest.raises(AIServiceError):
        parse_ai_response("sit_up", {"value": 10})
    with pytest.raises(AIServiceError):
        parse_ai_response("sit_up", {"rep_count": 10, "value": 10, "confidence": 7})

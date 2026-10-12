import uuid

from tests.conftest import (
    FAKE_MP4,
    create_athlete,
    good_sensor_data,
    new_uuid,
    register_and_login,
    upload,
)


def setup_athlete(client, email="athlete@example.com"):
    headers = register_and_login(client, email)
    return headers, create_athlete(client, headers)


def test_upload_vertical_jump_with_mock_ai(client):
    headers, athlete_id = setup_athlete(client)
    r = upload(client, headers, athlete_id)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "completed"
    assert body["cheat_flag"] is False
    assert body["video_path"].startswith(f"athletes/{athlete_id}/vertical_jump/")
    assert body["result"]["unit"] == "cm"
    assert body["result"]["jump_height_cm"] > 0
    assert 0 <= body["result"]["confidence"] <= 1
    # benchmark fields exist for the benchmarking teammate
    assert "benchmark_percentile" in body["result"]


def test_upload_sit_up_returns_rep_count(client):
    headers, athlete_id = setup_athlete(client)
    r = upload(client, headers, athlete_id, test_type="sit_up", filename="situp.mp4")
    assert r.status_code == 201
    assert r.json()["result"]["unit"] == "reps"
    assert r.json()["result"]["rep_count"] > 0


def test_results_and_history_after_upload(client):
    headers, athlete_id = setup_athlete(client)
    upload(client, headers, athlete_id)
    upload(client, headers, athlete_id, test_type="sit_up")

    results = client.get(f"/api/athletes/{athlete_id}/results", headers=headers).json()
    assert len(results) == 2
    only_jump = client.get(f"/api/athletes/{athlete_id}/results?test_type=vertical_jump", headers=headers).json()
    assert len(only_jump) == 1

    history = client.get(f"/api/athletes/{athlete_id}/history", headers=headers).json()
    assert len(history) == 2
    assert history[0]["result"] is not None


def test_get_submission_and_list_by_athlete(client):
    headers, athlete_id = setup_athlete(client)
    sid = upload(client, headers, athlete_id).json()["id"]
    assert client.get(f"/api/tests/{sid}", headers=headers).json()["id"] == sid
    assert len(client.get(f"/api/tests/athlete/{athlete_id}", headers=headers).json()) == 1
    assert client.get(f"/api/tests/{uuid.uuid4()}", headers=headers).status_code == 404


def test_upload_requires_auth_and_ownership(client):
    h1, a1 = setup_athlete(client, "one@example.com")
    h2, _ = setup_athlete(client, "two@example.com")
    no_auth = client.post(
        "/api/tests/upload",
        data={"athlete_id": a1, "test_type": "sit_up"},
        files={"video": ("a.mp4", FAKE_MP4, "video/mp4")},
    )
    assert no_auth.status_code == 401
    assert upload(client, h2, a1).status_code == 403  # cannot upload for someone else
    sid = upload(client, h1, a1).json()["id"]
    assert client.get(f"/api/tests/{sid}", headers=h2).status_code == 403  # cannot read it either


def test_unsupported_file_type_rejected(client):
    headers, athlete_id = setup_athlete(client)
    r = upload(client, headers, athlete_id, video=b"hello", filename="notes.txt", content_type="text/plain")
    assert r.status_code == 400


def test_oversized_file_rejected(client):
    headers, athlete_id = setup_athlete(client)  # MAX_VIDEO_SIZE_MB=1 in tests
    big = FAKE_MP4 + b"\x00" * (1024 * 1024 + 10)
    assert upload(client, headers, athlete_id, video=big).status_code == 400


def test_invalid_test_type_is_422(client):
    headers, athlete_id = setup_athlete(client)
    assert upload(client, headers, athlete_id, test_type="long_jump").status_code == 422


def test_analyze_endpoint(client):
    headers, athlete_id = setup_athlete(client)
    sid = upload(client, headers, athlete_id).json()["id"]
    r = client.post(f"/api/tests/{sid}/analyze", headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "completed"
    # still exactly one result row
    assert len(client.get(f"/api/athletes/{athlete_id}/results", headers=headers).json()) == 1


def test_duplicate_client_submission_id_does_not_duplicate(client):
    headers, athlete_id = setup_athlete(client)
    cid = new_uuid()
    first = upload(client, headers, athlete_id, client_submission_id=cid)
    second = upload(client, headers, athlete_id, client_submission_id=cid)
    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    assert len(client.get(f"/api/tests/athlete/{athlete_id}", headers=headers).json()) == 1


# ---------------- cheat detection ----------------
def reasons(response):
    assert response.status_code == 201, response.text
    return response.json()["cheat_reasons"], response.json()["cheat_flag"]


def test_cheat_tiny_file(client):
    headers, athlete_id = setup_athlete(client)
    tiny = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 50
    found, flag = reasons(upload(client, headers, athlete_id, video=tiny))
    assert flag and "tiny_file" in found


def test_cheat_empty_file(client):
    headers, athlete_id = setup_athlete(client)
    found, flag = reasons(upload(client, headers, athlete_id, video=b""))
    assert flag and "empty_file" in found


def test_cheat_fake_video_content(client):
    headers, athlete_id = setup_athlete(client)
    found, flag = reasons(upload(client, headers, athlete_id, video=b"A" * 20000))
    assert flag and "invalid_video_file" in found


def test_cheat_missing_sensor_data_and_metadata(client):
    headers, athlete_id = setup_athlete(client)
    data = {"athlete_id": athlete_id, "test_type": "vertical_jump"}
    r = client.post("/api/tests/upload", headers=headers, data=data, files={"video": ("a.mp4", FAKE_MP4, "video/mp4")})
    found, flag = reasons(r)
    assert flag
    assert "missing_sensor_data" in found
    assert "missing_metadata" in found


def test_cheat_invalid_sensor_json(client):
    headers, athlete_id = setup_athlete(client)
    found, flag = reasons(upload(client, headers, athlete_id, sensor_data="{not json"))
    assert flag and "invalid_metadata" in found


def test_cheat_suspicious_timestamp(client):
    headers, athlete_id = setup_athlete(client)
    future, _ = reasons(upload(client, headers, athlete_id, recorded_at="2999-01-01T00:00:00+00:00"))
    assert "timestamp_in_future" in future
    old, _ = reasons(upload(client, headers, athlete_id, recorded_at="2001-01-01T00:00:00+00:00"))
    assert "timestamp_too_old" in old


def test_cheat_invalid_duration(client):
    headers, athlete_id = setup_athlete(client)
    found, _ = reasons(upload(client, headers, athlete_id, duration="0"))
    assert "invalid_duration" in found
    found, _ = reasons(upload(client, headers, athlete_id, duration="9999"))
    assert "invalid_duration" in found


def test_cheat_excessive_sensor_variation(client):
    import json

    headers, athlete_id = setup_athlete(client)
    wild = json.dumps(
        {
            "accelerometer": [{"x": 0, "y": 0 if i % 2 else 200, "z": 0} for i in range(20)],
            "gyroscope": [{"x": 0, "y": 0 if i % 2 else 100, "z": 0} for i in range(20)],
        }
    )
    found, flag = reasons(upload(client, headers, athlete_id, sensor_data=wild))
    assert flag
    assert "excessive_accelerometer_variation" in found
    assert "excessive_gyroscope_variation" in found


def test_flagged_result_is_marked_flagged(client):
    headers, athlete_id = setup_athlete(client)
    body = upload(client, headers, athlete_id, duration="0").json()
    assert body["result"]["verification_status"] == "flagged"

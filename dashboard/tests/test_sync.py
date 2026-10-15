import base64
import uuid
from datetime import datetime, timezone

from tests.conftest import FAKE_MP4, create_athlete, good_sensor_data, new_uuid, register_and_login


def sync_single(client, headers, athlete_id, cid, test_type="sit_up"):
    return client.post(
        "/api/sync/submissions",
        headers=headers,
        data={
            "client_submission_id": cid,
            "athlete_id": athlete_id,
            "test_type": test_type,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": "30",
            "sensor_data": good_sensor_data(),
        },
        files={"video": ("situp.mp4", FAKE_MP4, "video/mp4")},
    )


def batch_item(athlete_id, cid, filename="jump.mp4", content=FAKE_MP4):
    return {
        "client_submission_id": cid,
        "athlete_id": athlete_id,
        "test_type": "vertical_jump",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": 5.0,
        "sensor_data": {"accelerometer": [{"x": 0, "y": 9.8, "z": 0}] * 10},
        "video_filename": filename,
        "video_base64": base64.b64encode(content).decode(),
    }


def setup(client, email="athlete@example.com"):
    headers = register_and_login(client, email)
    return headers, create_athlete(client, headers)


def test_sync_single_is_idempotent(client):
    headers, athlete_id = setup(client)
    cid = new_uuid()
    first = sync_single(client, headers, athlete_id, cid)
    second = sync_single(client, headers, athlete_id, cid)
    third = sync_single(client, headers, athlete_id, cid)

    assert first.status_code == 201 and first.json()["status"] == "created"
    assert second.status_code == 200 and second.json()["status"] == "duplicate"
    assert third.json()["submission_id"] == first.json()["submission_id"]

    assert len(client.get(f"/api/tests/athlete/{athlete_id}", headers=headers).json()) == 1
    assert len(client.get(f"/api/athletes/{athlete_id}/results", headers=headers).json()) == 1


def test_sync_status(client):
    headers, athlete_id = setup(client)
    cid = new_uuid()
    sync_single(client, headers, athlete_id, cid)
    sync_single(client, headers, athlete_id, cid)

    r = client.get(f"/api/sync/status/{cid}", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "synced"
    assert body["attempts"] == 2
    assert body["submission_status"] == "completed"
    assert body["result"] is not None

    assert client.get(f"/api/sync/status/{uuid.uuid4()}", headers=headers).status_code == 404


def test_sync_status_is_private(client):
    h1, a1 = setup(client, "one@example.com")
    h2, _ = setup(client, "two@example.com")
    cid = new_uuid()
    sync_single(client, h1, a1, cid)
    assert client.get(f"/api/sync/status/{cid}", headers=h2).status_code == 403


def test_sync_batch_per_item_results(client):
    headers, athlete_id = setup(client)
    ok_id, dup_id, bad_id = new_uuid(), new_uuid(), new_uuid()
    payload = {
        "items": [
            batch_item(athlete_id, ok_id),
            batch_item(athlete_id, dup_id),
            batch_item(athlete_id, dup_id),  # same UUID twice in one batch
            batch_item(athlete_id, bad_id, filename="notes.txt", content=b"not a video"),
        ]
    }
    r = client.post("/api/sync/batch", headers=headers, json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert (body["total"], body["succeeded"], body["duplicates"], body["failed"]) == (4, 2, 1, 1)
    statuses = [item["status"] for item in body["results"]]
    assert statuses == ["created", "created", "duplicate", "failed"]
    assert body["results"][3]["error"]

    assert len(client.get(f"/api/tests/athlete/{athlete_id}", headers=headers).json()) == 2

    # the failed item is reported by the status endpoint
    status = client.get(f"/api/sync/status/{bad_id}", headers=headers).json()
    assert status["status"] == "failed"
    assert status["error_message"]


def test_failed_item_can_be_retried_successfully(client):
    headers, athlete_id = setup(client)
    cid = new_uuid()
    bad = client.post("/api/sync/batch", headers=headers,
                      json={"items": [batch_item(athlete_id, cid, filename="x.txt", content=b"zzz")]})
    assert bad.json()["failed"] == 1
    good = client.post("/api/sync/batch", headers=headers, json={"items": [batch_item(athlete_id, cid)]})
    assert good.json()["succeeded"] == 1
    assert client.get(f"/api/sync/status/{cid}", headers=headers).json()["status"] == "synced"


def test_sync_batch_rejects_other_athletes_and_bad_base64(client):
    h1, a1 = setup(client, "one@example.com")
    h2, a2 = setup(client, "two@example.com")
    item_other = batch_item(a1, new_uuid())
    item_b64 = batch_item(a2, new_uuid())
    item_b64["video_base64"] = "***not-base64***"
    r = client.post("/api/sync/batch", headers=h2, json={"items": [item_other, item_b64]})
    assert r.status_code == 200
    assert [i["status"] for i in r.json()["results"]] == ["failed", "failed"]


def test_sync_batch_validation_and_auth(client):
    headers, _ = setup(client)
    assert client.post("/api/sync/batch", headers=headers, json={"items": []}).status_code == 422
    assert client.post("/api/sync/batch", json={"items": []}).status_code == 401


def test_same_uuid_cannot_be_used_by_two_athletes(client):
    h1, a1 = setup(client, "one@example.com")
    h2, a2 = setup(client, "two@example.com")
    cid = new_uuid()
    assert sync_single(client, h1, a1, cid).status_code == 201
    assert sync_single(client, h2, a2, cid).status_code == 409

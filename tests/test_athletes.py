import uuid

from tests.conftest import create_athlete, make_admin_headers, register_and_login


def test_create_get_update_profile(client):
    headers = register_and_login(client)
    athlete_id = create_athlete(client, headers)

    r = client.get(f"/api/athletes/{athlete_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Ravi Kumar"

    r = client.put(f"/api/athletes/{athlete_id}", headers=headers, json={"city": "Pune", "sport": "football"})
    assert r.status_code == 200
    assert r.json()["city"] == "Pune"
    assert r.json()["name"] == "Ravi Kumar"  # untouched fields stay


def test_one_profile_per_user(client):
    headers = register_and_login(client)
    create_athlete(client, headers)
    r = client.post(
        "/api/athletes", headers=headers,
        json={"name": "Again", "date_of_birth": "2004-05-10", "gender": "male"},
    )
    assert r.status_code == 409


def test_profile_validation(client):
    headers = register_and_login(client)
    base = {"name": "Test Name", "date_of_birth": "2004-05-10", "gender": "male"}
    assert client.post("/api/athletes", headers=headers, json={**base, "gender": "robot"}).status_code == 422
    assert client.post("/api/athletes", headers=headers, json={**base, "date_of_birth": "2999-01-01"}).status_code == 422
    assert client.post("/api/athletes", headers=headers, json={**base, "phone": "abc"}).status_code == 422


def test_athlete_cannot_access_other_athlete(client):
    h1 = register_and_login(client, "one@example.com")
    h2 = register_and_login(client, "two@example.com")
    a1 = create_athlete(client, h1, "One")
    create_athlete(client, h2, "Two")

    assert client.get(f"/api/athletes/{a1}", headers=h2).status_code == 403
    assert client.put(f"/api/athletes/{a1}", headers=h2, json={"city": "X"}).status_code == 403
    assert client.get(f"/api/athletes/{a1}/history", headers=h2).status_code == 403
    assert client.get(f"/api/athletes/{a1}/results", headers=h2).status_code == 403


def test_unauthenticated_and_missing(client):
    assert client.get(f"/api/athletes/{uuid.uuid4()}").status_code == 401
    headers = register_and_login(client)
    assert client.get(f"/api/athletes/{uuid.uuid4()}", headers=headers).status_code == 404


def test_admin_can_access_everything(client, session_factory):
    h1 = register_and_login(client, "one@example.com")
    a1 = create_athlete(client, h1)
    admin = make_admin_headers(client, session_factory)

    assert client.get(f"/api/athletes/{a1}", headers=admin).status_code == 200
    assert client.get(f"/api/athletes/{a1}/history", headers=admin).status_code == 200
    assert client.get("/api/athletes", headers=admin).status_code == 200
    # athletes cannot list everyone
    assert client.get("/api/athletes", headers=h1).status_code == 403


def test_history_and_results_empty(client):
    headers = register_and_login(client)
    athlete_id = create_athlete(client, headers)
    assert client.get(f"/api/athletes/{athlete_id}/history", headers=headers).json() == []
    assert client.get(f"/api/athletes/{athlete_id}/results", headers=headers).json() == []

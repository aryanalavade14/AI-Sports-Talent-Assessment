from tests.conftest import PASSWORD, login, register_and_login


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_register_login_and_me(client):
    r = client.post("/api/auth/register", json={"email": "a@example.com", "password": PASSWORD})
    assert r.status_code == 201
    assert r.json()["role"] == "athlete"
    assert "hashed_password" not in r.json()

    headers = login(client, "a@example.com")
    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "a@example.com"


def test_duplicate_email_conflict(client):
    register_and_login(client, "dup@example.com")
    r = client.post("/api/auth/register", json={"email": "DUP@example.com", "password": PASSWORD})
    assert r.status_code == 409


def test_weak_password_and_bad_email_rejected(client):
    assert client.post("/api/auth/register", json={"email": "a@example.com", "password": "short"}).status_code == 422
    assert client.post("/api/auth/register", json={"email": "not-an-email", "password": PASSWORD}).status_code == 422


def test_wrong_password_and_unknown_user(client):
    register_and_login(client, "b@example.com")
    assert client.post("/api/auth/login", json={"email": "b@example.com", "password": "WrongPass999"}).status_code == 401
    assert client.post("/api/auth/login", json={"email": "nobody@example.com", "password": PASSWORD}).status_code == 401


def test_me_requires_valid_token(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_register_cannot_create_admin(client):
    r = client.post(
        "/api/auth/register", json={"email": "sneaky@example.com", "password": PASSWORD, "role": "admin"}
    )
    assert r.status_code == 201
    assert r.json()["role"] == "athlete"

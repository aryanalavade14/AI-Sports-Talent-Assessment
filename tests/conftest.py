"""Test setup: in-memory SQLite database, temp upload folder, MOCK_AI on.

Environment variables are set BEFORE the app is imported so the tests never
touch your real PostgreSQL database or your real uploads/ folder.
"""
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"
os.environ["MOCK_AI"] = "true"
os.environ["UPLOAD_DIR"] = tempfile.mkdtemp(prefix="uploads_test_")
os.environ["MAX_VIDEO_SIZE_MB"] = "1"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import ROLE_ADMIN, User  # noqa: E402
from app.utils.security import hash_password  # noqa: E402

# A minimal fake MP4: a valid "ftyp" header followed by padding (bigger than the 10 KB "tiny" limit).
FAKE_MP4 = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 20000
PASSWORD = "StrongPass123"


@pytest.fixture()
def session_factory():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def client(session_factory):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------- helpers ----------
def register_and_login(client, email="athlete@example.com") -> dict:
    r = client.post("/api/auth/register", json={"email": email, "password": PASSWORD})
    assert r.status_code == 201, r.text
    return login(client, email)


def login(client, email, password=PASSWORD) -> dict:
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def create_athlete(client, headers, name="Ravi Kumar") -> str:
    r = client.post(
        "/api/athletes",
        headers=headers,
        json={
            "name": name,
            "date_of_birth": "2004-05-10",
            "gender": "male",
            "phone": "+919876543210",
            "city": "Mumbai",
            "state": "Maharashtra",
            "sport": "athletics",
        },
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def make_admin_headers(client, session_factory, email="admin@example.com") -> dict:
    with session_factory() as db:
        db.add(User(email=email, hashed_password=hash_password(PASSWORD), role=ROLE_ADMIN))
        db.commit()
    return login(client, email)


def good_sensor_data() -> str:
    return json.dumps(
        {
            "accelerometer": [{"x": 0.0, "y": 9.8 + 0.1 * i, "z": 0.2} for i in range(20)],
            "gyroscope": [{"x": 0.1, "y": 0.05 * i, "z": 0.0} for i in range(20)],
        }
    )


def upload(client, headers, athlete_id, *, test_type="vertical_jump", video=FAKE_MP4, filename="jump.mp4",
           content_type="video/mp4", sensor_data=None, recorded_at=None, duration="5.0",
           client_submission_id=None):
    data = {"athlete_id": athlete_id, "test_type": test_type}
    data["sensor_data"] = good_sensor_data() if sensor_data is None else sensor_data
    data["recorded_at"] = recorded_at or datetime.now(timezone.utc).isoformat()
    if duration is not None:
        data["duration_seconds"] = duration
    if client_submission_id:
        data["client_submission_id"] = client_submission_id
    return client.post(
        "/api/tests/upload", headers=headers, data=data, files={"video": (filename, video, content_type)}
    )


def new_uuid() -> str:
    return str(uuid.uuid4())

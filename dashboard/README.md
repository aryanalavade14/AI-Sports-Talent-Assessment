# AI-Powered Mobile Platform for Democratising Sports Talent Assessment — Backend + Database

FastAPI + PostgreSQL backend: authentication, athlete profiles, test video upload, test history/results,
AI-engine integration (with a mock), basic cheat detection and idempotent offline sync.

**MVP tests supported:** `vertical_jump` and `sit_up`.

```
Mobile App  →  FastAPI  →  AI/CV Engine (teammate, MediaPipe Pose)  →  PostgreSQL  →  Dashboard
```

> MediaPipe is **not** implemented here. `app/services/ai_service.py` is the clean interface to the AI engine.
> With `MOCK_AI=true` the backend creates realistic fake results, so everything works without the AI engine.

---

## 1. Installation

Requirements: **Python 3.11+**, **PostgreSQL 14+**, Git.

```bash
git clone <your-team-repo-url>
cd <repo>
git checkout feature/backend-database      # see "Git workflow" at the bottom
```

## 2. Python virtual environment

```bash
python -m venv venv
# Windows:   venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

## 3. PostgreSQL / database setup

Create a database (names below are examples):

```bash
psql -U postgres
```
```sql
CREATE DATABASE sports_talent;
-- optional dedicated user:
CREATE USER sports_user WITH PASSWORD 'choose_a_password';
GRANT ALL PRIVILEGES ON DATABASE sports_talent TO sports_user;
\c sports_talent
GRANT ALL ON SCHEMA public TO sports_user;
\q
```

## 4. Environment file (`.env`)

```bash
cp .env.example .env          # Windows: copy .env.example .env
```
Edit `.env`:

| Variable | Meaning |
|---|---|
| `DATABASE_URL` | e.g. `postgresql+psycopg2://sports_user:choose_a_password@localhost:5432/sports_talent` |
| `SECRET_KEY` | long random string. Generate: `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT lifetime, e.g. `60` |
| `AI_ENGINE_URL` | AI teammate's endpoint, e.g. `http://localhost:9000/analyze` |
| `MOCK_AI` | `true` = fake results, `false` = call the real AI engine |
| `UPLOAD_DIR` | folder for videos (default `uploads`) |
| `MAX_VIDEO_SIZE_MB` | upload size limit |

`.env` is in `.gitignore`. **Never commit it.** The app refuses to start if `DATABASE_URL` or `SECRET_KEY` is missing.

## 5. Alembic migrations

The tables are created by Alembic (the app never calls `create_all`).

```bash
alembic upgrade head          # create / update all tables
alembic current               # show current version
```

When you change a model later:
```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Create an admin user (admins cannot self-register through the API):
```bash
python -m app.utils.create_admin admin@example.com "StrongPassword123"
```

## 6. Running FastAPI

```bash
uvicorn app.main:app --reload
```
- API: http://127.0.0.1:8000
- Health: http://127.0.0.1:8000/health
- To let a phone on the same Wi-Fi connect: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

## 7. Swagger docs

Open **http://127.0.0.1:8000/docs**.
1. Call `POST /api/auth/register`, then `POST /api/auth/login`.
2. Copy `access_token`, click **Authorize** (top right), paste the token (no "Bearer" prefix needed).
3. All protected endpoints now work from the browser.

## 8. Testing the APIs (manual walkthrough)

```bash
# 1. register + login
curl -X POST localhost:8000/api/auth/register -H "Content-Type: application/json" \
     -d '{"email":"ravi@example.com","password":"StrongPass123"}'
curl -X POST localhost:8000/api/auth/login -H "Content-Type: application/json" \
     -d '{"email":"ravi@example.com","password":"StrongPass123"}'
TOKEN=<paste access_token>

# 2. athlete profile
curl -X POST localhost:8000/api/athletes -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
     -d '{"name":"Ravi Kumar","date_of_birth":"2004-05-10","gender":"male","city":"Mumbai","state":"Maharashtra","sport":"athletics"}'
ATHLETE=<paste id>

# 3. upload a video
curl -X POST localhost:8000/api/tests/upload -H "Authorization: Bearer $TOKEN" \
     -F athlete_id=$ATHLETE -F test_type=vertical_jump -F video=@jump.mp4 \
     -F recorded_at=2026-10-07T10:00:00Z -F duration_seconds=6 \
     -F 'sensor_data={"accelerometer":[{"x":0,"y":9.8,"z":0.1}, ...],"gyroscope":[...]}'

# 4. read results
curl localhost:8000/api/athletes/$ATHLETE/results -H "Authorization: Bearer $TOKEN"
curl localhost:8000/api/athletes/$ATHLETE/history -H "Authorization: Bearer $TOKEN"
```

### All endpoints

| Method | Path | Notes |
|---|---|---|
| GET | `/health` | liveness + DB check |
| POST | `/api/auth/register` | creates an **athlete** account |
| POST | `/api/auth/login` | returns JWT |
| GET | `/api/auth/me` | current user |
| POST | `/api/athletes` | create profile (athlete: own; admin: pass `user_id`) |
| GET | `/api/athletes` | admin only: list athletes |
| GET / PUT | `/api/athletes/{id}` | owner or admin |
| GET | `/api/athletes/{id}/history` | all submissions with status/cheat flag/result |
| GET | `/api/athletes/{id}/results` | results (`?test_type=` filter) |
| POST | `/api/tests/upload` | multipart video upload |
| GET | `/api/tests/{submission_id}` | one submission + result |
| GET | `/api/tests/athlete/{athlete_id}` | submissions of an athlete |
| POST | `/api/tests/{submission_id}/analyze` | (re-)run AI/mock analysis |
| POST | `/api/sync/submissions` | sync one offline test (multipart) |
| POST | `/api/sync/batch` | sync many (JSON, base64 videos) |
| GET | `/api/sync/status/{client_submission_id}` | sync state |

Roles: an **athlete** can only access their own data; an **admin** can access everything.
Error codes used: 400 bad input/file, 401 not logged in, 403 not allowed, 404 not found, 409 duplicate/conflict,
422 validation, 500 server error (502 if the real AI engine fails on `/analyze`).

## 9. Mock AI

With `MOCK_AI=true` (default in `.env.example`) the backend fabricates results (seeded by the submission id, so the
same submission always gets the same fake result):

- vertical_jump → `{"jump_height_cm", "value", "unit": "cm", "confidence"}`
- sit_up → `{"rep_count", "value", "unit": "reps", "confidence"}`

Results are saved in `test_results`. Benchmark columns (`benchmark_percentile`, `benchmark_category`,
`norm_reference`) are left `NULL` for the benchmarking teammate (or filled if the AI response includes them).

## 10. Offline sync

The mobile app generates a **UUID `client_submission_id`** for every test recorded offline and sends it when online.

- Sending the **same UUID again never creates a duplicate** (DB unique constraint + check). You get the original back with `status: "duplicate"`.
- `POST /api/sync/batch` returns **per-item** `created | duplicate | failed` plus an error message for failed items. One bad item never breaks the others.
- A failed item can be re-sent with the same UUID later; `GET /api/sync/status/{id}` shows `synced` / `failed`, attempts and the result.
- The batch endpoint carries videos as base64 (simple, but heavy). For big videos, use `POST /api/sync/submissions` one at a time.

## 11. pytest

```bash
pytest -v
```
Tests use an in-memory SQLite database, a temp upload folder and `MOCK_AI=true`, so they never touch PostgreSQL or `uploads/`.
They cover: registration/login/JWT, athlete profile, authorization, video upload, duplicate UUID, cheat detection,
mock AI + results, offline sync.

## 12. Common errors

| Error | Fix |
|---|---|
| `Missing required environment variable(s)` | create `.env` from `.env.example` |
| `connection refused` / `could not connect to server` | PostgreSQL not running or wrong `DATABASE_URL` |
| `password authentication failed` | wrong user/password in `DATABASE_URL` |
| `relation "users" does not exist` | run `alembic upgrade head` |
| `Form data requires "python-multipart"` | `pip install -r requirements.txt` |
| `401 Not authenticated` | send `Authorization: Bearer <token>`; token may have expired |
| `403` | athlete is touching another athlete's data / non-admin on admin route |
| `400 Video is larger than ...` | raise `MAX_VIDEO_SIZE_MB` or compress |
| `502 AI engine error` | `MOCK_AI=false` but the AI engine is down, or returned the wrong JSON shape |
| `ModuleNotFoundError: app` | run commands from the project root folder |

## 13. Mobile-app integration (for the app teammate)

1. `POST /api/auth/login` → store `access_token`; send `Authorization: Bearer <token>` on every request.
2. Create the profile once (`POST /api/athletes`), store the athlete `id`.
3. Record a test and upload with `multipart/form-data`: `athlete_id`, `test_type`, `video`, `recorded_at` (ISO 8601),
   `duration_seconds`, `sensor_data` (JSON string), and optionally `client_submission_id`.
4. `sensor_data` format: `{"accelerometer":[{"x":0,"y":9.8,"z":0.1},...], "gyroscope":[{"x":..,"y":..,"z":..},...]}`
   (arrays `[x,y,z]` also accepted).
5. Offline: save everything locally with a fresh UUID; when online call `/api/sync/submissions` or `/api/sync/batch`.
   Treat `created` **and** `duplicate` as success; retry `failed` later.
6. Show `result` from the response, or fetch `/api/athletes/{id}/results` and `/history`.
7. Check `cheat_flag` / `cheat_reasons` if you want to warn the user (e.g. "recording too short").

## 14. AI-engine integration (for the AI teammate)

Set `MOCK_AI=false` and `AI_ENGINE_URL=<your endpoint>`. The backend sends a `multipart/form-data` POST:
`file` (video), `test_type`, `submission_id`, `sensor_data` (JSON string). Your service must reply with JSON:

```json
{"jump_height_cm": 42.5, "value": 42.5, "unit": "cm", "confidence": 0.91}      // vertical_jump
{"rep_count": 28, "value": 28, "unit": "reps", "confidence": 0.88}             // sit_up
```
Optional extra keys: `benchmark_percentile` (0–100), `benchmark_category`, `norm_reference`.
Invalid/missing fields mark the submission `failed` (with `error_message`); retry via `POST /api/tests/{id}/analyze`.
The call is synchronous with a 120 s timeout (constant `AI_TIMEOUT_SECONDS` in `ai_service.py`).

## Cheat detection (basic only)

Rule-based checks in `cheat_detection_service.py`; sets `cheat_flag` and `cheat_reasons`. This is **not** advanced
forensic fraud detection. Reason codes: `unsupported_file_type`, `invalid_video_file`, `empty_file`, `tiny_file`,
`missing_metadata`, `invalid_metadata`, `timestamp_in_future`, `timestamp_too_old`, `invalid_duration`,
`missing_sensor_data`, `excessive_accelerometer_variation`, `excessive_gyroscope_variation`.
Thresholds are constants at the top of that file. Flagged results get `verification_status = "flagged"`.
Clearly unsupported file types and files over the size limit are rejected outright (400) instead.

## Video storage

Videos are saved to `uploads/athletes/{athlete_id}/{test_type}/<random>.<ext>`. All file access goes through
`app/services/storage_service.py` — to move to S3/GCS later, add another `StorageBackend` class and return it from `get_storage()`.

## Project structure

```
app/
  main.py  config.py  database.py
  models/    users, athletes, test_submissions, test_results, sync_records
  schemas/   Pydantic v2 request/response models
  routers/   auth, athletes, tests, sync
  services/  ai_service, storage_service, cheat_detection_service, submission_service, sync_service
  utils/     security (bcrypt+JWT), deps (auth/ownership), errors, create_admin
tests/  alembic/  uploads/  requirements.txt  .env.example  .gitignore  README.md
```
(Your spec spelled the helper folder `utlis/`; I named it `utils/`. Rename it if your team wants the original spelling and update the imports.)

## 15. Git workflow

The team repository uses separate branches; yours is **`feature/backend-database`**. Do not change repo settings.

```bash
git checkout -b feature/backend-database      # first time (or: git checkout feature/backend-database)
git add .
git status                                    # make sure .env is NOT listed
git commit -m "feat: backend API, database models, auth, sync"
git push -u origin feature/backend-database
```
Then open a Pull Request into the team's main/develop branch. Pull teammates' changes with
`git fetch origin && git merge origin/main`.

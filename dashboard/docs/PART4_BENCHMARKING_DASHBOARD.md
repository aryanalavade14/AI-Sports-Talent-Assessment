# Part 4 – Benchmarking & Admin/SAI Dashboard

Backend (FastAPI, same project) + web dashboard (`dashboard/`, React + TypeScript + Vite) that reuses the mobile app's colours.
All dashboard numbers come from the real database (`athletes`, `test_results`). Nothing is hard-coded or sample data.

## Run it (3 terminals-worth of steps)

Backend (from the project root, venv active, `.env` filled in as in the main README):
```bash
pip install -r requirements.txt
python -m alembic upgrade head                      # adds benchmark_norms + shortlisted_athletes (migration 0002)
python -m app.utils.create_admin admin@example.com "StrongPassword123"   # once
uvicorn app.main:app --reload                       # http://127.0.0.1:8000
```
Dashboard:
```bash
cd dashboard
npm install
npm run dev                                         # http://localhost:5173  (log in with the admin account)
```
Backend on another address? create `dashboard/.env` with `VITE_API_URL=http://<host>:8000`.
Tests: `pytest tests/test_benchmark_dashboard.py -v`

The dashboard fills up as athletes register, create a profile and complete tests (Part 1/2/3 flow).

## How benchmarking works
* Norms live in table `benchmark_norms`: per test + gender + age band, the score needed for the 10/25/50/75/90th percentile.
* A score is placed between those points by straight-line interpolation (clamped to 1–99).
* Levels: 80+ Excellent, 60–79 Good, 40–59 Average, 20–39 Developing, <20 Needs Improvement.
* Gender "other" uses the average of male and female norms. Ages outside all bands use the closest band.
* Athlete score per test = best result that is not `flagged`/`rejected`. Overall percentile = mean of the test percentiles.
* **The seeded norm values are indicative MVP numbers, not an official dataset.** Replace them with SAI/Khelo India
  tables by editing the `benchmark_norms` rows (or `app/data/default_norms.py` before running the migration). No code change needed.

## API (new)
| Method | Path | Who |
|---|---|---|
| GET | `/api/benchmarks/norms?test_type=` | any logged-in user |
| GET | `/api/benchmarks/evaluate?test_type&gender&age&value` | any logged-in user (usable by the mobile app) |
| POST | `/api/benchmarks/recalculate` | admin – saves percentile/level/norm into `test_results.benchmark_*` |
| GET | `/api/admin/filters`, `/summary`, `/athletes`, `/leaderboard?test=overall\|vertical_jump\|sit_up` | admin; filters: `region, sport, gender, age_min, age_max` |
| GET / PUT / DELETE | `/api/admin/shortlist[/{athlete_id}]` | admin |

Optional hook so new results get their percentile saved automatically (one line, in `ai_service.run_analysis` after the result is built):
`from app.services.benchmark_service import apply_benchmark` … `apply_benchmark(db, result, submission.athlete)`.

## Files
New: `app/models/benchmark_norm.py`, `app/models/shortlist.py`, `app/data/default_norms.py`, `app/services/benchmark_service.py`,
`app/services/dashboard_service.py`, `app/routers/benchmarks.py`, `app/routers/dashboard.py`, `app/schemas/dashboard.py`,
`alembic/versions/0002_benchmark_and_shortlist.py`, `tests/test_benchmark_dashboard.py`, `dashboard/` (whole folder), this doc.
Modified (additive only): `app/main.py` (2 imports/includes), `app/models/__init__.py` (2 imports).

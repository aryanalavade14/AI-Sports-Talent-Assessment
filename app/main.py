"""FastAPI entry point.  Run with:  uvicorn app.main:app --reload"""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.database import engine
from app.routers import athletes, auth, sync, tests
from app.utils.errors import register_exception_handlers

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="AI-Powered Mobile Platform for Democratising Sports Talent Assessment",
    description="Backend + database: auth, athlete profiles, test videos/results, AI-engine hook, offline sync.",
    version="1.0.0",
    lifespan=lifespan,
)

# Comma-separated list in CORS_ORIGINS; "*" (default) is fine for local development.
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(athletes.router)
app.include_router(tests.router)
app.include_router(sync.router)


@app.get("/health", tags=["Health"])
def health():
    """Liveness check; also reports whether the database answers."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        database = "up"
    except Exception:
        database = "down"
    return {"status": "ok" if database == "up" else "degraded", "database": database, "mock_ai": settings.MOCK_AI}

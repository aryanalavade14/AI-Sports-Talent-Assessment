"""Application settings, read from environment variables (and a local .env file).

No secrets live in code: SECRET_KEY and DATABASE_URL must come from the environment.
"""
import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    AI_ENGINE_URL: str
    MOCK_AI: bool
    UPLOAD_DIR: str
    MAX_VIDEO_SIZE_MB: int
    ALGORITHM: str = "HS256"

    @property
    def max_video_size_bytes(self) -> int:
        return self.MAX_VIDEO_SIZE_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    database_url = os.getenv("DATABASE_URL")
    secret_key = os.getenv("SECRET_KEY")
    missing = [
        name
        for name, value in (("DATABASE_URL", database_url), ("SECRET_KEY", secret_key))
        if not value
    ]
    if missing:
        raise RuntimeError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Copy .env.example to .env and fill them in."
        )
    return Settings(
        DATABASE_URL=database_url,
        SECRET_KEY=secret_key,
        ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        AI_ENGINE_URL=os.getenv("AI_ENGINE_URL", "http://localhost:9000/analyze"),
        MOCK_AI=_as_bool(os.getenv("MOCK_AI"), default=True),
        UPLOAD_DIR=os.getenv("UPLOAD_DIR", "uploads"),
        MAX_VIDEO_SIZE_MB=int(os.getenv("MAX_VIDEO_SIZE_MB", "50")),
    )

"""File storage abstraction.

Today videos go to the local `uploads/` folder. To move to cloud storage later
(S3, Google Cloud Storage, ...) write another class with the same methods
(`save`, `delete`, `absolute_path`) and return it from `get_storage()`.
Nothing else in the project needs to change.
"""
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO

from app.config import get_settings


class FileTooLargeError(Exception):
    pass


class StorageBackend(ABC):
    @abstractmethod
    def save(self, *, athlete_id: uuid.UUID, test_type: str, extension: str, stream: BinaryIO, max_bytes: int):
        """Save the stream. Returns (relative_path, size_in_bytes)."""

    @abstractmethod
    def delete(self, relative_path: str) -> None: ...

    @abstractmethod
    def absolute_path(self, relative_path: str) -> Path: ...


class LocalStorage(StorageBackend):
    CHUNK = 1024 * 1024  # 1 MB

    def __init__(self, base_dir: str):
        self.base = Path(base_dir).resolve()
        self.base.mkdir(parents=True, exist_ok=True)

    def save(self, *, athlete_id, test_type, extension, stream, max_bytes):
        # Layout: uploads/athletes/{athlete_id}/{test_type}/{random}.ext
        relative = Path("athletes") / str(athlete_id) / test_type / f"{uuid.uuid4().hex}{extension}"
        target = self.base / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        size = 0
        try:
            with open(target, "wb") as out:
                while True:
                    chunk = stream.read(self.CHUNK)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > max_bytes:
                        raise FileTooLargeError()
                    out.write(chunk)
        except Exception:
            target.unlink(missing_ok=True)  # never leave half-written files behind
            raise
        return relative.as_posix(), size

    def delete(self, relative_path: str) -> None:
        try:
            (self.base / relative_path).unlink(missing_ok=True)
        except OSError:
            pass

    def absolute_path(self, relative_path: str) -> Path:
        return self.base / relative_path


def get_storage() -> StorageBackend:
    return LocalStorage(get_settings().UPLOAD_DIR)

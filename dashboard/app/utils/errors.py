"""Shared error type + global exception handlers (consistent JSON errors)."""
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger("app")


class AppError(Exception):
    """Raise this from services; it becomes a clean JSON error response.

    Use: 400 bad input, 401 not logged in, 403 not allowed, 404 not found,
    409 conflict/duplicate, 422 validation, 500 server error.
    """

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(_: Request, exc: IntegrityError):
        logger.warning("Integrity error: %s", exc)
        return JSONResponse(
            status_code=409, content={"detail": "Conflict: this record already exists or is invalid."}
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception):
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

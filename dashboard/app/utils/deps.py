"""FastAPI dependencies: current user, role checks and ownership checks."""
import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.athlete import Athlete
from app.models.user import User
from app.utils.errors import AppError
from app.utils.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AppError(401, "Not authenticated")
    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise AppError(401, "Invalid or expired token")
    try:
        user_id = uuid.UUID(payload["sub"])
    except ValueError:
        raise AppError(401, "Invalid token")
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise AppError(401, "User not found or inactive")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise AppError(403, "Admin access required")
    return user


def get_athlete_for_user(db: Session, user: User, athlete_id: uuid.UUID) -> Athlete:
    """Load an athlete, enforcing: athletes only see their own data, admins see all."""
    athlete = db.get(Athlete, athlete_id)
    if athlete is None:
        raise AppError(404, "Athlete not found")
    if user.role != "admin" and athlete.user_id != user.id:
        raise AppError(403, "You can only access your own data")
    return athlete

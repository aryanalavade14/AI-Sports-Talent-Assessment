from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import ROLE_ATHLETE, User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.utils.deps import get_current_user
from app.utils.errors import AppError
from app.utils.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Create an athlete account. (Admins are created with `python -m app.utils.create_admin`.)"""
    email = data.email.lower()
    if db.scalar(select(User).where(func.lower(User.email) == email)):
        raise AppError(409, "An account with this email already exists")
    user = User(email=email, hashed_password=hash_password(data.password), role=ROLE_ATHLETE)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(func.lower(User.email) == data.email.lower()))
    # Same message for "no such user" and "wrong password" so attackers can't probe emails.
    if user is None or not verify_password(data.password, user.hashed_password):
        raise AppError(401, "Incorrect email or password")
    if not user.is_active:
        raise AppError(403, "This account is disabled")
    token, expires_in = create_access_token(str(user.id), user.role)
    return TokenResponse(access_token=token, expires_in=expires_in, user=user)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user

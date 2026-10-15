"""Create an admin user from the command line.

Usage:  python -m app.utils.create_admin admin@example.com "StrongPassword123"
"""
import sys

from sqlalchemy import select

from app.database import SessionLocal
from app.models.user import ROLE_ADMIN, User
from app.utils.security import hash_password


def main() -> None:
    if len(sys.argv) != 3:
        print('Usage: python -m app.utils.create_admin <email> "<password>"')
        raise SystemExit(1)
    email, password = sys.argv[1].lower(), sys.argv[2]
    if len(password) < 8:
        print("Password must be at least 8 characters.")
        raise SystemExit(1)
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == email)):
            print("A user with this email already exists.")
            raise SystemExit(1)
        db.add(User(email=email, hashed_password=hash_password(password), role=ROLE_ADMIN))
        db.commit()
    print(f"Admin created: {email}")


if __name__ == "__main__":
    main()

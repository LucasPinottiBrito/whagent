from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models import User


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.db.scalar(select(User).where(User.email == email))
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

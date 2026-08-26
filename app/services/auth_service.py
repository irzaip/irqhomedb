from datetime import datetime, timedelta

from itsdangerous import URLSafeTimedSerializer as Serializer
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.config import SECRET_KEY
from app.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = Serializer(SECRET_KEY, salt="auth")
COOKIE_NAME = "irq_session"
SESSION_MAX_AGE = 7 * 24 * 3600  # 7 days


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_session(user_id: int) -> str:
    data = {"user_id": user_id, "exp": (datetime.utcnow() + timedelta(days=7)).isoformat()}
    return serializer.dumps(data)


def get_session_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        data = serializer.loads(token, max_age=SESSION_MAX_AGE)
        user = db.query(User).filter(User.id == data["user_id"]).first()
        return user if user and user.is_active else None
    except Exception:
        return None


def require_user(user: User = Depends(get_session_user)) -> User:
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    return user
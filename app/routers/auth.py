from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth_service import (
    hash_password, verify_password, create_session,
    get_session_user, require_user, COOKIE_NAME, SESSION_MAX_AGE
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    display_name: str = ""


@router.post("/login")
def login(req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Username atau password salah")

    token = create_session(user.id)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
    )
    return {"success": True, "data": {"id": user.id, "username": user.username, "display_name": user.display_name}}


@router.post("/logout")
def logout(response: Response, user: User = Depends(require_user)):
    response.delete_cookie(COOKIE_NAME)
    return {"success": True, "data": {"message": "Logged out"}}


@router.get("/me")
def me(user: User = Depends(get_session_user)):
    if not user:
        return {"success": True, "data": None}
    return {
        "success": True,
        "data": {"id": user.id, "username": user.username, "display_name": user.display_name},
    }


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username sudah ada")

    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        display_name=req.display_name or req.username,
    )
    db.add(user)
    db.commit()
    return {"success": True, "data": {"id": user.id, "username": user.username}}
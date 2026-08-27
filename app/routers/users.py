"""User administration API (admin-only). Create happens via /api/auth/register
(also admin-only); this router covers the remaining user-management actions."""
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth_service import require_admin, hash_password

router = APIRouter(prefix="/api/users", tags=["users"])


def _public(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "is_admin": user.is_admin,
        "is_active": user.is_active,
    }


def _get_target(user_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    return user


@router.get("")
def list_users(_admin=Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id).all()
    return {"success": True, "data": [_public(u) for u in users]}


@router.post("/{user_id}/reset-password")
def reset_password(
    user_id: int,
    new_password: str = Form(...),
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    if not new_password:
        raise HTTPException(status_code=400, detail="Password baru tidak boleh kosong")
    target = _get_target(user_id, db)
    target.password_hash = hash_password(new_password)
    db.commit()
    return {"success": True, "data": {"message": f"Password {target.username} berhasil direset"}}


@router.patch("/{user_id}")
def update_user(
    user_id: int,
    is_active: bool | None = Form(None),
    display_name: str = Form(None),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    target = _get_target(user_id, db)
    if is_active is not None:
        # Don't let an admin lock themselves out of their own account.
        if target.id == admin.id and not is_active:
            raise HTTPException(status_code=400, detail="Tidak bisa menonaktifkan akun sendiri")
        target.is_active = is_active
    if display_name is not None:
        target.display_name = display_name.strip() or target.username
    db.commit()
    return {"success": True, "data": _public(target)}


@router.delete("/{user_id}")
def delete_user(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    target = _get_target(user_id, db)
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="Tidak bisa menghapus akun sendiri")
    db.delete(target)
    db.commit()
    return {"success": True, "data": {"message": f"User {target.username} dihapus"}}
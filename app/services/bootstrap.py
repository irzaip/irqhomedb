"""Startup bootstrap: additive column migrations + first-run admin seeding.

Kept separate from main.py so the logic is testable and the lifespan stays a
readable two-liner. All operations are idempotent and safe to run on every boot.
"""
from sqlalchemy import text

from app.database import engine, SessionLocal
from app.models.user import User
from app.services.auth_service import hash_password

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin"


def run_migrations() -> None:
    """Best-effort additive migrations for databases created by older builds.

    SQLAlchemy's create_all never alters an existing table, so any column added
    to a model after a DB already exists needs an explicit ALTER here. Fresh
    databases already have the column and the statement simply fails silently.
    """
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN"))
    except Exception:
        pass  # column already exists, or brand-new table — nothing to do


def seed_admin() -> None:
    """Guarantee at least one admin account exists.

    - Empty DB  -> create the default admin (avoids a fresh install being
      locked out now that /register is admin-only).
    - Existing DB with no admin -> promote the first account, so pre-seeding
      installs can still reach Settings. Irza's own account is id 1.
    - Already have an admin -> no-op.
    """
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(
                username=DEFAULT_ADMIN_USERNAME,
                password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
                display_name="Irza (Admin)",
                is_admin=True,
            )
            db.add(admin)
            db.commit()
            print(
                "🎉 First run — default admin created.\n"
                f"   username: {DEFAULT_ADMIN_USERNAME}   "
                f"password: {DEFAULT_ADMIN_PASSWORD}\n"
                "   ⚠️  Change this password from ⚙️ Settings → My Account."
            )
        elif not db.query(User).filter(User.is_admin == True).first():
            first = db.query(User).order_by(User.id).first()
            if first:
                first.is_admin = True
                db.commit()
                print(f"👑 Promoted '{first.username}' to admin (existing DB).")
    finally:
        db.close()
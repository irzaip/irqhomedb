from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def database_file_path() -> str:
    """Expand DATABASE_URL to an on-disk file path (for backup/restore)."""
    url = str(DATABASE_URL)
    if url.startswith("sqlite:///"):
        return url[len("sqlite:///"):]
    return url


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    # create_all won't alter an existing table — apply columns added later.
    from app.services.bootstrap import run_migrations
    run_migrations()

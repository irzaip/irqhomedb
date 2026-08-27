"""Backup & restore.

Backup  -> stream everything (SQLite DB + all uploaded photos) as a single zip
           named `irqhomedb-backup-<date-time>-<identifier>.zip`. The identifier
           is the first item/box name (or "manual") so files are recognizable.
Restore -> upload one of those zips; the DB and uploads are swapped in and the
           app continues on the restored data.

Admin-only. Restore keeps a pre-restore safety copy of the current DB before it
touches anything, so a bad restore isn't destructive.
"""
import io
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.config import DATA_DIR, UPLOAD_DIR
from app.database import SessionLocal, database_file_path, init_db
from app.models.box import Box
from app.models.item import Item
from app.services.auth_service import require_admin

router = APIRouter(prefix="/api", tags=["backup"])

_DB_FILENAME = "irqhomedb.db"
_UPLOAD_SUBDIRS = ("items", "boxes", "locations")


def _sanitize(name: str) -> str:
    name = re.sub(r"[^A-Za-z0-9_-]+", "-", name or "").strip("-")
    return name[:40] or "manual"


def _backup_identifier() -> str:
    db = SessionLocal()
    try:
        first = db.query(Item).filter(Item.name.isnot(None)).order_by(Item.created_at).first()
        if first and first.name:
            return _sanitize(first.name)
        box = db.query(Box).filter(Box.name.isnot(None)).order_by(Box.created_at).first()
        if box and box.name:
            return _sanitize(box.name)
        return "manual"
    finally:
        db.close()


def _walk_files(root: Path):
    if root.is_dir():
        for f in sorted(root.rglob("*")):
            if f.is_file():
                yield f


@router.get("/backup")
def download_backup(_admin=Depends(require_admin)):
    """Stream a zip of the database + all photos."""
    db_path = Path(database_file_path())
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="Database file not found")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(db_path, _DB_FILENAME)  # database at the zip root

        for sub in _UPLOAD_SUBDIRS:
            root = Path(UPLOAD_DIR) / sub
            for file in _walk_files(root):
                zf.write(file, f"uploads/{sub}/{file.relative_to(root)}")

    buf.seek(0)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"irqhomedb-backup-{ts}-{_backup_identifier()}.zip"
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _safe_extract(zf: zipfile.ZipFile, target: Path):
    """Extract a zip into target, refusing any path that escapes it (zip-slip)."""
    target = target.resolve()
    for info in zf.infolist():
        dest = (target / info.filename).resolve()
        if not dest.is_relative_to(target):
            raise HTTPException(status_code=400, detail=f"Illegal path in archive: {info.filename}")
    for info in zf.infolist():
        if info.is_dir():
            continue
        dest = (target / info.filename).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(info) as src, open(dest, "wb") as out:
            shutil.copyfileobj(src, out)


@router.post("/restore")
async def restore_backup(file: UploadFile, _admin=Depends(require_admin)):
    """Replace the current DB + photos with those from an uploaded backup zip."""
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Harus berupa file .zip")

    work = Path(DATA_DIR) / ".restore-work"
    work.mkdir(parents=True, exist_ok=True)
    zip_path = work / ("upload-" + Path(file.filename).name)
    try:
        with open(zip_path, "wb") as out:
            shutil.copyfileobj(file.file, out)

        try:
            zf = zipfile.ZipFile(zip_path)
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="File .zip tidak valid")

        with zf:
            if _DB_FILENAME not in zf.namelist():
                raise HTTPException(status_code=400, detail="Zip tidak berisi database (irqhomedb.db)")
            extracted = work / "extracted"
            if extracted.exists():
                shutil.rmtree(extracted)
            _safe_extract(zf, extracted)

        # Release any pooled connection so the SQLite file can be swapped.
        from app.database import engine
        engine.dispose()

        db_path = Path(database_file_path())
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(db_path, DATA_DIR / f"irqhomedb.pre-restore-{ts}.db")  # safety copy

        shutil.copy2(extracted / _DB_FILENAME, db_path)  # swap database

        for sub in _UPLOAD_SUBDIRS:  # swap photos
            target_dir = Path(UPLOAD_DIR) / sub
            shutil.rmtree(target_dir, ignore_errors=True)
            target_dir.mkdir(parents=True, exist_ok=True)
            src_dir = extracted / "uploads" / sub
            if src_dir.is_dir():
                for f in src_dir.rglob("*"):
                    if f.is_file():
                        rel = f.relative_to(src_dir)
                        (target_dir / rel).parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(f, target_dir / rel)

        init_db()  # guarantee a compatible schema on the restored DB
    finally:
        shutil.rmtree(work, ignore_errors=True)

    return {"success": True, "data": {"message": "Backup berhasil direstore. Muat ulang halaman."}}
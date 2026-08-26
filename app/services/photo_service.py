"""Generic photo storage helpers.

The add/delete photo logic used to live copy-pasted across item/box/location
endpoints in app/routers/photos.py. These helpers take the photo model and its
entity-FK column name, so one implementation serves all three entity types.
"""
import io
import os
import uuid

from fastapi import HTTPException, UploadFile
from PIL import Image
from sqlalchemy.orm import Session

from app.config import THUMBNAIL_SIZE, ALLOWED_EXTENSIONS, MAX_PHOTO_SIZE


def ensure_dir(d: str) -> str:
    os.makedirs(d, exist_ok=True)
    return d


def save_photo(upload_dir: str, file: UploadFile) -> str:
    """Store one upload under upload_dir (uuid filename) and generate a thumbnail.

    Validates extension, size, and image content before touching disk.
    Returns the generated filename.
    """
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Format tidak didukung: {ext}")
    content = file.file.read()
    if len(content) > MAX_PHOTO_SIZE:
        raise HTTPException(status_code=400, detail="File terlalu besar (max 10MB)")
    # Verify it's actually an image before writing to disk
    # (prevents HTML/EXE masquerading as .jpg)
    try:
        Image.open(io.BytesIO(content)).verify()
    except Exception:
        raise HTTPException(status_code=400, detail="File bukan gambar valid")
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(content)
    try:
        img = Image.open(filepath)
        img.thumbnail(THUMBNAIL_SIZE)
        img.save(os.path.join(upload_dir, f"thumb_{filename}"))
    except Exception:
        pass  # thumbnail is best-effort
    return filename


def next_sort_order(db: Session, photo_model, fk_field: str, entity_id) -> int:
    """sort_order to assign to the next appended photo (max + 1, or 0)."""
    fk = getattr(photo_model, fk_field)
    row = (
        db.query(photo_model.sort_order)
        .filter(fk == entity_id)
        .order_by(photo_model.sort_order.desc())
        .first()
    )
    return (row[0] + 1) if row else 0


def add_photos(
    db: Session,
    photo_model,
    fk_field: str,
    entity_id,
    base_dir: str,
    files: list[UploadFile],
) -> list[dict]:
    """Save uploads to base_dir/<entity_id>/ and add photo rows. Caller commits."""
    upload_dir = ensure_dir(os.path.join(base_dir, str(entity_id)))
    start = next_sort_order(db, photo_model, fk_field, entity_id)
    results = []
    for i, file in enumerate(files):
        filename = save_photo(upload_dir, file)
        photo = photo_model(sort_order=start + i, filename=filename)
        setattr(photo, fk_field, entity_id)
        db.add(photo)
        results.append({"filename": filename})
    return results


def delete_photo(
    db: Session,
    photo_model,
    fk_field: str,
    entity_id,
    photo_id: int,
    base_dir: str,
) -> None:
    """Delete one photo row + its files (original and thumbnail).

    Raises 404 if the photo doesn't exist or belongs to a different entity.
    """
    fk = getattr(photo_model, fk_field)
    photo = db.query(photo_model).filter(photo_model.id == photo_id, fk == entity_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    upload_dir = os.path.join(base_dir, str(entity_id))
    for name in (photo.filename, f"thumb_{photo.filename}"):
        path = os.path.join(upload_dir, name)
        if os.path.exists(path):
            os.remove(path)
    db.delete(photo)
    db.commit()

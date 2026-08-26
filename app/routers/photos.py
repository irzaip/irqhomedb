import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from PIL import Image

from app.config import ITEM_PHOTO_DIR, BOX_PHOTO_DIR, LOCATION_PHOTO_DIR, THUMBNAIL_SIZE, ALLOWED_EXTENSIONS, MAX_PHOTO_SIZE
from app.database import get_db
from app.models.item import Item
from app.models.item_photo import ItemPhoto
from app.models.box import Box
from app.models.box_photo import BoxPhoto
from app.models.location import Location
from app.models.location_photo import LocationPhoto
from app.services.auth_service import get_session_user

router = APIRouter(prefix="/api", tags=["photos"])


def save_photo(upload_dir: str, file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Format tidak didukung: {ext}")
    content = file.file.read()
    if len(content) > MAX_PHOTO_SIZE:
        raise HTTPException(status_code=400, detail="File terlalu besar (max 10MB)")
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(content)
    try:
        img = Image.open(filepath)
        img.thumbnail(THUMBNAIL_SIZE)
        thumb_path = os.path.join(upload_dir, f"thumb_{filename}")
        img.save(thumb_path)
    except Exception:
        pass
    return filename


def ensure_dir(d: str) -> str:
    os.makedirs(d, exist_ok=True)
    return d


@router.post("/upload")
async def upload_photos(
    files: list[UploadFile] = File(...),
    box_id: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(get_session_user),
):
    """1 foto = 1 item. Bisa link ke box_id."""
    if not files:
        raise HTTPException(status_code=400, detail="Tidak ada file")
    user_id = user.id if user else None
    results = []
    for file in files:
        item = Item(status="unidentified", box_id=box_id or None, upload_session_id=str(uuid.uuid4()), created_by=user_id)
        db.add(item)
        db.flush()
        upload_dir = ensure_dir(os.path.join(ITEM_PHOTO_DIR, item.id))
        filename = save_photo(upload_dir, file)
        db.add(ItemPhoto(item_id=item.id, filename=filename, sort_order=0))
        results.append({"item_id": item.id, "filename": filename})
    db.commit()
    return {"success": True, "data": results, "total": len(results)}


@router.post("/items/{item_id}/photos")
async def add_item_photos(item_id: str, files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    if not db.query(Item).filter(Item.id == item_id).first():
        raise HTTPException(status_code=404, detail="Item not found")
    upload_dir = ensure_dir(os.path.join(ITEM_PHOTO_DIR, item_id))
    results = []
    max_order = db.query(ItemPhoto.sort_order).filter(ItemPhoto.item_id == item_id).order_by(ItemPhoto.sort_order.desc()).first()
    next_order = (max_order[0] + 1) if max_order else 0
    for i, file in enumerate(files):
        filename = save_photo(upload_dir, file)
        db.add(ItemPhoto(item_id=item_id, filename=filename, sort_order=next_order + i))
        results.append({"filename": filename})
    db.commit()
    return {"success": True, "data": results}


@router.post("/boxes/{box_id}/photos")
async def add_box_photos(box_id: str, files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    if not db.query(Box).filter(Box.id == box_id).first():
        raise HTTPException(status_code=404, detail="Box not found")
    upload_dir = ensure_dir(os.path.join(BOX_PHOTO_DIR, box_id))
    results = []
    max_order = db.query(BoxPhoto.sort_order).filter(BoxPhoto.box_id == box_id).order_by(BoxPhoto.sort_order.desc()).first()
    next_order = (max_order[0] + 1) if max_order else 0
    for i, file in enumerate(files):
        filename = save_photo(upload_dir, file)
        db.add(BoxPhoto(box_id=box_id, filename=filename, sort_order=next_order + i))
        results.append({"filename": filename})
    db.commit()
    return {"success": True, "data": results}


@router.post("/locations/{location_id}/photos")
async def add_location_photos(location_id: int, files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    if not db.query(Location).filter(Location.id == location_id).first():
        raise HTTPException(status_code=404, detail="Location not found")
    upload_dir = ensure_dir(os.path.join(LOCATION_PHOTO_DIR, str(location_id)))
    results = []
    max_order = db.query(LocationPhoto.sort_order).filter(LocationPhoto.location_id == location_id).order_by(LocationPhoto.sort_order.desc()).first()
    next_order = (max_order[0] + 1) if max_order else 0
    for i, file in enumerate(files):
        filename = save_photo(upload_dir, file)
        db.add(LocationPhoto(location_id=location_id, filename=filename, sort_order=next_order + i))
        results.append({"filename": filename})
    db.commit()
    return {"success": True, "data": results}


@router.delete("/items/{item_id}/photos/{photo_id}")
def delete_item_photo(item_id: str, photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(ItemPhoto).filter(ItemPhoto.id == photo_id, ItemPhoto.item_id == item_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    filepath = os.path.join(ITEM_PHOTO_DIR, item_id, photo.filename)
    if os.path.exists(filepath): os.remove(filepath)
    db.delete(photo); db.commit()
    return {"success": True, "data": {"message": "Photo deleted"}}


@router.delete("/boxes/{box_id}/photos/{photo_id}")
def delete_box_photo(box_id: str, photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(BoxPhoto).filter(BoxPhoto.id == photo_id, BoxPhoto.box_id == box_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    filepath = os.path.join(BOX_PHOTO_DIR, box_id, photo.filename)
    if os.path.exists(filepath): os.remove(filepath)
    db.delete(photo); db.commit()
    return {"success": True, "data": {"message": "Photo deleted"}}
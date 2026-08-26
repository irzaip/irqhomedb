import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.config import ITEM_PHOTO_DIR, BOX_PHOTO_DIR, LOCATION_PHOTO_DIR
from app.database import get_db
from app.models.item import Item
from app.models.item_photo import ItemPhoto
from app.models.box import Box
from app.models.box_photo import BoxPhoto
from app.models.location import Location
from app.models.location_photo import LocationPhoto
from app.services.auth_service import require_user
from app.services.photo_service import (
    add_photos,
    delete_photo,
    ensure_dir,
    save_photo,
)

router = APIRouter(prefix="/api", tags=["photos"])


@router.post("/upload")
async def upload_photos(
    files: list[UploadFile] = File(...),
    box_id: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(require_user),
):
    """1 foto = 1 item. Bisa link ke box_id."""
    if not files:
        raise HTTPException(status_code=400, detail="Tidak ada file")
    results = []
    for file in files:
        item = Item(
            status="unidentified",
            box_id=box_id or None,
            upload_session_id=str(uuid.uuid4()),
            created_by=user.id,
        )
        db.add(item)
        db.flush()
        upload_dir = ensure_dir(os.path.join(ITEM_PHOTO_DIR, item.id))
        filename = save_photo(upload_dir, file)
        db.add(ItemPhoto(item_id=item.id, filename=filename, sort_order=0))
        results.append({"item_id": item.id, "filename": filename})
    db.commit()
    return {"success": True, "data": results, "total": len(results)}


@router.post("/items/{item_id}/photos")
async def add_item_photos(item_id: str, files: list[UploadFile] = File(...), _user=Depends(require_user), db: Session = Depends(get_db)):
    if not db.query(Item).filter(Item.id == item_id).first():
        raise HTTPException(status_code=404, detail="Item not found")
    results = add_photos(db, ItemPhoto, "item_id", item_id, ITEM_PHOTO_DIR, files)
    db.commit()
    return {"success": True, "data": results}


@router.post("/boxes/{box_id}/photos")
async def add_box_photos(box_id: str, files: list[UploadFile] = File(...), _user=Depends(require_user), db: Session = Depends(get_db)):
    if not db.query(Box).filter(Box.id == box_id).first():
        raise HTTPException(status_code=404, detail="Box not found")
    results = add_photos(db, BoxPhoto, "box_id", box_id, BOX_PHOTO_DIR, files)
    db.commit()
    return {"success": True, "data": results}


@router.post("/locations/{location_id}/photos")
async def add_location_photos(location_id: int, files: list[UploadFile] = File(...), _user=Depends(require_user), db: Session = Depends(get_db)):
    if not db.query(Location).filter(Location.id == location_id).first():
        raise HTTPException(status_code=404, detail="Location not found")
    results = add_photos(db, LocationPhoto, "location_id", location_id, LOCATION_PHOTO_DIR, files)
    db.commit()
    return {"success": True, "data": results}


@router.delete("/items/{item_id}/photos/{photo_id}")
def delete_item_photo(item_id: str, photo_id: int, _user=Depends(require_user), db: Session = Depends(get_db)):
    delete_photo(db, ItemPhoto, "item_id", item_id, photo_id, ITEM_PHOTO_DIR)
    return {"success": True, "data": {"message": "Photo deleted"}}


@router.delete("/boxes/{box_id}/photos/{photo_id}")
def delete_box_photo(box_id: str, photo_id: int, _user=Depends(require_user), db: Session = Depends(get_db)):
    delete_photo(db, BoxPhoto, "box_id", box_id, photo_id, BOX_PHOTO_DIR)
    return {"success": True, "data": {"message": "Photo deleted"}}

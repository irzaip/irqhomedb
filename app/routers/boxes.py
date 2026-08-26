from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.box import Box
from app.models.item import Item
from app.services.auth_service import require_user
from app.services.entity_service import apply_box_fields, list_unidentified

router = APIRouter(prefix="/api/boxes", tags=["boxes"])


@router.get("")
def list_boxes(
    search: str = "",
    location_id: int = 0,
    status: str = "",
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(Box)
    if status:
        query = query.filter(Box.status == status)
    if location_id:
        query = query.filter(Box.location_id == location_id)
    if search:
        like = f"%{search}%"
        query = query.filter(Box.name.ilike(like) | Box.description.ilike(like))
    total = query.count()
    boxes = query.order_by(Box.created_at.desc()).offset(skip).limit(limit).all()
    return {"success": True, "data": boxes, "total": total}


@router.get("/{box_id}")
def get_box(box_id: str, db: Session = Depends(get_db)):
    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        raise HTTPException(status_code=404, detail="Box not found")
    items = db.query(Item).filter(Item.box_id == box_id).order_by(Item.name).all()
    return {"success": True, "data": box, "items": items}


@router.delete("/{box_id}")
def delete_box(box_id: str, _user=Depends(require_user), db: Session = Depends(get_db)):
    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        raise HTTPException(status_code=404, detail="Box not found")
    db.delete(box)
    db.commit()
    return {"success": True, "data": {"message": "Box deleted"}}


@router.post("/{box_id}/edit")
def edit_box(
    box_id: str,
    name: str = "",
    location_id: int = 0,
    description: str = "",
    _user=Depends(require_user),
    db: Session = Depends(get_db),
):
    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        raise HTTPException(status_code=404, detail="Box not found")
    apply_box_fields(box, name=name, location_id=location_id, description=description)
    db.commit()
    db.refresh(box)
    return {"success": True, "data": box}


@router.post("/{box_id}/identify")
def identify_box(
    box_id: str,
    name: str = "",
    location_id: int = 0,
    description: str = "",
    _user=Depends(require_user),
    db: Session = Depends(get_db),
):
    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        raise HTTPException(status_code=404, detail="Box not found")
    apply_box_fields(
        box, name=name, location_id=location_id, description=description,
        make_identified=True,
    )
    db.commit()
    db.refresh(box)
    return {"success": True, "data": box}


@router.get("/unidentified/all")
def list_unidentified_boxes(db: Session = Depends(get_db)):
    boxes = list_unidentified(db, Box)
    return {"success": True, "data": boxes, "total": len(boxes)}


@router.get("/{box_id}/items")
def get_box_items(box_id: str, db: Session = Depends(get_db)):
    items = db.query(Item).filter(Item.box_id == box_id).order_by(Item.name).all()
    return {"success": True, "data": items, "total": len(items)}


@router.post("/create-with-photos")
async def create_box_with_photos(
    name: str = Form(""),
    location_id: int = Form(0),
    description: str = Form(""),
    _user=Depends(require_user),
    db: Session = Depends(get_db),
):
    """Create a box (unidentified). Photos uploaded separately via later POST."""
    box = Box(
        status="identified" if name else "unidentified",
        name=name or None,
        location_id=location_id if location_id else None,
        description=description or None,
    )
    db.add(box)
    db.commit()
    db.refresh(box)
    return {"success": True, "data": {"id": box.id, "name": box.name}}

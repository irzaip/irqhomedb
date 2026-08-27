from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.item import Item
from app.models.box import Box
from app.models.item_category import ItemCategory
from app.services.auth_service import require_user
from app.services.entity_service import apply_item_fields, list_unidentified

router = APIRouter(prefix="/api/items", tags=["items"])


@router.get("")
def list_items(
    search: str = "",
    box_id: str = "",
    category_id: int = 0,
    location_id: int = 0,
    status: str = "",
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(Item)
    if status:
        query = query.filter(Item.status == status)
    if box_id:
        query = query.filter(Item.box_id == box_id)
    if location_id:
        query = query.join(Box).filter(Box.location_id == location_id)
    if category_id:
        query = query.join(ItemCategory).filter(ItemCategory.category_id == category_id)
    if search:
        like = f"%{search}%"
        query = query.filter(
            Item.name.ilike(like) | Item.description.ilike(like) | Item.notes.ilike(like) | Item.tags.ilike(like)
        )
    total = query.count()
    items = query.order_by(Item.created_at.desc()).offset(skip).limit(limit).all()
    return {"success": True, "data": items, "total": total, "skip": skip, "limit": limit}


@router.delete("/{item_id}")
def delete_item(item_id: str, _user=Depends(require_user), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"success": True, "data": {"message": "Item deleted"}}


@router.post("/{item_id}/identify")
def identify_item(
    item_id: str,
    name: str = Form(""),
    box_id: str = Form(""),
    description: str = Form(""),
    notes: str = Form(""),
    unit: str = Form("pcs"),
    quantity: str = Form("1"),
    category_ids: str = Form(""),
    _user=Depends(require_user),
    db: Session = Depends(get_db),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    apply_item_fields(
        item, db,
        name=name, box_id=box_id, description=description, notes=notes,
        unit=unit, quantity=quantity, category_ids=category_ids,
        make_identified=True,
    )
    db.commit()
    db.refresh(item)
    return {"success": True, "data": item}


@router.post("/{item_id}/edit")
def edit_item(
    item_id: str,
    name: str = Form(""),
    box_id: str = Form(""),
    description: str = Form(""),
    notes: str = Form(""),
    unit: str = Form("pcs"),
    quantity: str = Form("1"),
    category_ids: str = Form(""),
    _user=Depends(require_user),
    db: Session = Depends(get_db),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    apply_item_fields(
        item, db,
        name=name, box_id=box_id, description=description, notes=notes,
        unit=unit, quantity=quantity, category_ids=category_ids,
    )
    db.commit()
    db.refresh(item)
    return {"success": True, "data": item}


@router.get("/unidentified/all")
def list_unidentified_items(db: Session = Depends(get_db)):
    items = list_unidentified(db, Item)
    return {"success": True, "data": items, "total": len(items)}

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import urllib.parse

from app.database import get_db
from app.models.item import Item
from app.models.box import Box
from app.models.item_category import ItemCategory

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
def delete_item(item_id: str, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"success": True, "data": {"message": "Item deleted"}}


@router.post("/{item_id}/identify")
async def identify_item(item_id: str, request: Request, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Read raw body and parse
    name = ""
    box_id = ""
    description = ""
    notes = ""
    unit = "pcs"
    cats_str = ""
    quantity = 1

    try:
        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8")
        parsed = urllib.parse.parse_qs(body_str)
        name = parsed.get("name", [""])[0]
        box_id = parsed.get("box_id", [""])[0]
        description = parsed.get("description", [""])[0]
        notes = parsed.get("notes", [""])[0]
        unit = parsed.get("unit", ["pcs"])[0] or "pcs"
        cats_str = parsed.get("category_ids", [""])[0]
        qty_str = parsed.get("quantity", ["1"])[0] or "1"
        quantity = int(qty_str) if qty_str.isdigit() else 1
    except Exception:
        # Fallback query params
        name = request.query_params.get("name", "") or ""
        box_id = request.query_params.get("box_id", "") or ""
        description = request.query_params.get("description", "") or ""
        notes = request.query_params.get("notes", "") or ""
        unit = request.query_params.get("unit", "pcs") or "pcs"
        cats_str = request.query_params.get("category_ids", "") or ""
        qty = request.query_params.get("quantity", "1") or "1"
        quantity = int(qty) if qty.isdigit() else 1

    item.name = name or None
    item.box_id = box_id or None
    item.description = description or None
    item.notes = notes or None
    item.quantity = max(1, quantity)
    item.unit = unit or "pcs"
    item.status = "identified"

    ids = []
    if cats_str:
        for v in str(cats_str).split(","):
            v = v.strip()
            if v.isdigit():
                ids.append(int(v))
    if ids:
        db.query(ItemCategory).filter(ItemCategory.item_id == item_id).delete()
        for cid in ids:
            db.add(ItemCategory(item_id=item_id, category_id=cid))

    db.commit()
    db.refresh(item)
    return {"success": True, "data": item}


@router.post("/{item_id}/edit")
async def edit_item(item_id: str, request: Request, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8")
    import urllib.parse
    parsed = urllib.parse.parse_qs(body_str)

    name = parsed.get("name", [""])[0]
    box_id = parsed.get("box_id", [""])[0]
    description = parsed.get("description", [""])[0]
    notes = parsed.get("notes", [""])[0]
    unit = parsed.get("unit", ["pcs"])[0] or "pcs"
    cats_str = parsed.get("category_ids", [""])[0]
    qty_str = parsed.get("quantity", ["1"])[0] or "1"
    quantity = int(qty_str) if qty_str.isdigit() else 1

    item.name = name or None
    item.box_id = box_id or None
    item.description = description or None
    item.notes = notes or None
    item.quantity = max(1, quantity)
    item.unit = unit or "pcs"
    item.status = "identified" if item.name else "unidentified"

    ids = []
    if cats_str:
        for v in str(cats_str).split(","):
            v = v.strip()
            if v.isdigit():
                ids.append(int(v))
    if ids:
        db.query(ItemCategory).filter(ItemCategory.item_id == item_id).delete()
        for cid in ids:
            db.add(ItemCategory(item_id=item_id, category_id=cid))

    db.commit()
    db.refresh(item)
    return {"success": True, "data": item}


@router.get("/unidentified/all")
def list_unidentified(db: Session = Depends(get_db)):
    items = db.query(Item).filter(Item.status == "unidentified").order_by(Item.created_at.desc()).all()
    return {"success": True, "data": items, "total": len(items)}
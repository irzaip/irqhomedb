from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.location import Location

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.get("")
def list_locations(db: Session = Depends(get_db)):
    locs = db.query(Location).order_by(Location.sort_order, Location.name).all()
    result = []
    for l in locs:
        result.append({
            "id": l.id,
            "name": l.name,
            "parent_id": l.parent_id,
            "room": l.room,
            "description": l.description,
            "sort_order": l.sort_order,
            "photos": [{"id": p.id, "filename": p.filename, "caption": p.caption} for p in (l.photos or [])],
            "created_at": str(l.created_at),
        })
    return {"success": True, "data": result}


@router.get("/{loc_id}")
def get_location(loc_id: int, db: Session = Depends(get_db)):
    l = db.query(Location).filter(Location.id == loc_id).first()
    if not l:
        raise HTTPException(status_code=404, detail="Location not found")
    return {"success": True, "data": {
        "id": l.id,
        "name": l.name,
        "parent_id": l.parent_id,
        "room": l.room,
        "description": l.description,
        "sort_order": l.sort_order,
        "photos": [{"id": p.id, "filename": p.filename, "caption": p.caption} for p in (l.photos or [])],
        "created_at": str(l.created_at),
    }}


@router.post("")
def create_location(name: str = Form(...), parent_id: int = Form(0), room: str = Form(""), db: Session = Depends(get_db)):
    loc = Location(
        name=name,
        parent_id=parent_id if parent_id else None,
        room=room or None,
    )
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return {"success": True, "data": {"id": loc.id, "name": loc.name}}


@router.put("/{loc_id}")
def update_location(loc_id: int, name: str = "", parent_id: int = 0, room: str = "", db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.id == loc_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    if name:
        loc.name = name
    if parent_id:
        loc.parent_id = parent_id if parent_id else None
    if room:
        loc.room = room
    db.commit()
    db.refresh(loc)
    return {"success": True, "data": {"id": loc.id, "name": loc.name}}


@router.delete("/{loc_id}")
def delete_location(loc_id: int, db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.id == loc_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(loc)
    db.commit()
    return {"success": True, "data": {"message": "Location deleted"}}
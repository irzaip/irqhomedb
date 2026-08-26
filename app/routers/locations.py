from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.location import Location
from app.services.auth_service import require_user
from app.services.entity_service import serialize_location

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.get("")
def list_locations(db: Session = Depends(get_db)):
    locs = db.query(Location).order_by(Location.sort_order, Location.name).all()
    return {"success": True, "data": [serialize_location(l) for l in locs]}


@router.get("/{loc_id}")
def get_location(loc_id: int, db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.id == loc_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return {"success": True, "data": serialize_location(loc)}


@router.post("")
def create_location(name: str = Form(...), parent_id: int = Form(0), room: str = Form(""), _user=Depends(require_user), db: Session = Depends(get_db)):
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
def update_location(loc_id: int, name: str = Form(""), parent_id: int = Form(0), room: str = Form(""), _user=Depends(require_user), db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.id == loc_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    if name:
        loc.name = name
    if parent_id:
        loc.parent_id = parent_id
    if room:
        loc.room = room
    db.commit()
    db.refresh(loc)
    return {"success": True, "data": {"id": loc.id, "name": loc.name}}


@router.delete("/{loc_id}")
def delete_location(loc_id: int, _user=Depends(require_user), db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.id == loc_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(loc)
    db.commit()
    return {"success": True, "data": {"message": "Location deleted"}}

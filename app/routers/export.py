import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.item import Item

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/csv")
def export_csv(db: Session = Depends(get_db)):
    items = db.query(Item).filter(Item.status == "identified").order_by(Item.name).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nama", "Jumlah", "Satuan", "Kategori", "Lokasi", "Deskripsi", "Notes"])

    for item in items:
        cat_names = ", ".join([c.name for c in item.categories]) if item.categories else ""
        loc_name = item.box.location.name if (item.box and item.box.location) else ""
        writer.writerow([item.name, item.quantity, item.unit, cat_names, loc_name, item.description or "", item.notes or ""])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=irqhomedb_items.csv"},
    )


@router.get("/json")
def export_json(db: Session = Depends(get_db)):
    items = db.query(Item).filter(Item.status == "identified").all()
    data = []
    for item in items:
        data.append({
            "id": item.id,
            "name": item.name,
            "quantity": item.quantity,
            "unit": item.unit,
            "categories": [c.name for c in item.categories] if item.categories else [],
            "location": item.box.location.name if (item.box and item.box.location) else None,
            "description": item.description,
            "notes": item.notes,
        })
    return {"success": True, "data": data}
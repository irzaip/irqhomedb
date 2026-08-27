"""Shared entity-update logic for items, boxes, locations.

identify and edit endpoints previously carried two copies of the same
field-assignment code; these helpers are the single source now.
"""
from sqlalchemy.orm import Session

from app.models.box import Box
from app.models.item import Item
from app.models.item_category import ItemCategory
from app.models.location import Location


def parse_category_ids(cats_str: str) -> list[int]:
    """Parse a comma-separated category id list from form data."""
    return [int(v.strip()) for v in str(cats_str or "").split(",") if v.strip().isdigit()]


def parse_positive_int(value: str, default: int = 1) -> int:
    return int(value) if str(value or "").isdigit() else default


def apply_item_fields(
    item: Item,
    db: Session,
    *,
    name: str,
    box_id: str,
    description: str,
    notes: str,
    unit: str,
    quantity: str,
    category_ids: str,
    make_identified: bool = False,
) -> Item:
    """Assign editable item fields from (stringly-typed) form values and sync
    the many-to-many categories. Caller commits.

    edit (make_identified=False): the form reposts the full current state, so
    an empty field is an explicit clear — categories are always replaced.
    identify (make_identified=True): the form starts blank and only carries
    what the user wants to fill in, so an empty category selection is left
    alone rather than wiping categories the item already has.
    """
    name = (name or "").strip()
    item.name = name or None
    item.box_id = box_id or None
    item.description = description or None
    item.notes = notes or None
    item.quantity = max(1, parse_positive_int(quantity, 1))
    item.unit = unit or "pcs"
    item.status = "identified" if (make_identified or name) else "unidentified"

    ids = parse_category_ids(category_ids)
    if not make_identified or ids:
        # edit: always authoritative. identify: only touch categories when the
        # user actually picked some.
        db.query(ItemCategory).filter(ItemCategory.item_id == item.id).delete()
        for cid in ids:
            db.add(ItemCategory(item_id=item.id, category_id=cid))
    return item


def apply_box_fields(
    box: Box,
    *,
    name: str,
    location_id: int,
    description: str,
    make_identified: bool | None = None,
) -> Box:
    """Assign editable box fields.

    identify (make_identified=True): the identify form starts with a blank
    location select, so an omitted location/description is left untouched —
    never overwriting an existing value with None. Status is forced to
    "identified".
    edit (make_identified=None): the form reposts the full state, so an empty
    value is an explicit clear; status derives from having a name.
    """
    name = (name or "").strip()
    if make_identified is True:
        box.name = name or None
        if location_id:
            box.location_id = location_id
        if description:
            box.description = description
        box.status = "identified"
    else:
        box.name = name or None
        box.location_id = location_id if location_id else None
        box.description = description or None
        box.status = "identified" if name else "unidentified"
    return box


def list_unidentified(db: Session, model) -> list:
    """All rows with status='unidentified', newest first."""
    return (
        db.query(model)
        .filter(model.status == "unidentified")
        .order_by(model.created_at.desc())
        .all()
    )


def serialize_location(loc: Location) -> dict:
    return {
        "id": loc.id,
        "name": loc.name,
        "parent_id": loc.parent_id,
        "room": loc.room,
        "description": loc.description,
        "sort_order": loc.sort_order,
        "photos": [
            {"id": p.id, "filename": p.filename, "caption": p.caption}
            for p in (loc.photos or [])
        ],
        "created_at": str(loc.created_at),
    }

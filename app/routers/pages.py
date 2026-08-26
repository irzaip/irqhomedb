"""HTML page routes (Jinja-rendered). API JSON endpoints live in the other
routers; this one only serves pages and is auth-gated via require_user."""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.item import Item
from app.models.box import Box
from app.models.location import Location
from app.models.category import Category
from app.services.auth_service import require_user

router = APIRouter(tags=["pages"])

TEMPLATES_DIR = str(Path(__file__).parent.parent / "templates")
jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def render_template(name: str, request: Request, **context):
    context.setdefault("request", request)
    return HTMLResponse(jinja_env.get_template(name).render(**context))


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, user=Depends(require_user), db: Session = Depends(get_db)):
    return render_template("dashboard.html", request,
        user=user,
        total_items=db.query(Item).count(),
        total_boxes=db.query(Box).count(),
        unidentified_items=db.query(Item).filter(Item.status == "unidentified").count(),
        unidentified_boxes=db.query(Box).filter(Box.status == "unidentified").count(),
        low_stock=db.query(Item).filter(Item.status == "identified", Item.quantity <= Item.min_quantity).count(),
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return render_template("auth/login.html", request)


@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request, user=Depends(require_user)):
    return render_template("upload.html", request, user=user)


@router.get("/items", response_class=HTMLResponse)
def items_page(request: Request, user=Depends(require_user)):
    return render_template("items/list.html", request, user=user)


@router.get("/items/identify", response_class=HTMLResponse)
def identify_items_page(request: Request, user=Depends(require_user)):
    return render_template("items/identify.html", request, user=user)


@router.get("/items/{item_id}", response_class=HTMLResponse)
def item_detail_page(request: Request, item_id: str, user=Depends(require_user), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return render_template("items/detail.html", request, user=user, item=item)


@router.get("/items/{item_id}/edit", response_class=HTMLResponse)
def item_edit_page(request: Request, item_id: str, user=Depends(require_user), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    boxes = db.query(Box).order_by(Box.name).all()
    locations = db.query(Location).order_by(Location.name).all()
    categories = db.query(Category).order_by(Category.name).all()
    item_cat_ids = [c.id for c in (item.categories or [])]
    return render_template("items/edit.html", request,
        user=user, item=item, boxes=boxes, locations=locations,
        categories=categories, item_cat_ids=item_cat_ids)


@router.get("/boxes", response_class=HTMLResponse)
def boxes_page(request: Request, user=Depends(require_user)):
    return render_template("boxes/list.html", request, user=user)


@router.get("/boxes/identify", response_class=HTMLResponse)
def identify_boxes_page(request: Request, user=Depends(require_user)):
    return render_template("boxes/identify.html", request, user=user)


@router.get("/boxes/{box_id}", response_class=HTMLResponse)
def box_detail_page(request: Request, box_id: str, user=Depends(require_user), db: Session = Depends(get_db)):
    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        raise HTTPException(status_code=404, detail="Box not found")
    return render_template("boxes/detail.html", request, user=user, box=box)


@router.get("/boxes/{box_id}/edit", response_class=HTMLResponse)
def box_edit_page(request: Request, box_id: str, user=Depends(require_user), db: Session = Depends(get_db)):
    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        raise HTTPException(status_code=404, detail="Box not found")
    locations = db.query(Location).order_by(Location.name).all()
    return render_template("boxes/edit.html", request, user=user, box=box, locations=locations)


@router.get("/boxes/{box_id}/add-items", response_class=HTMLResponse)
def box_add_items_page(request: Request, box_id: str, user=Depends(require_user), db: Session = Depends(get_db)):
    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        raise HTTPException(status_code=404, detail="Box not found")
    return render_template("boxes/add_items.html", request, user=user, box=box)


@router.get("/categories", response_class=HTMLResponse)
def categories_page(request: Request, user=Depends(require_user)):
    return render_template("categories/manage.html", request, user=user)


@router.get("/locations", response_class=HTMLResponse)
def locations_page(request: Request, user=Depends(require_user)):
    return render_template("locations/manage.html", request, user=user)


@router.get("/locations/{loc_id}", response_class=HTMLResponse)
def location_detail_page(request: Request, loc_id: int, user=Depends(require_user), db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.id == loc_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return render_template("locations/detail.html", request, user=user, loc=loc)

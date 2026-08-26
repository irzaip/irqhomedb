from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from app.config import STATIC_DIR, ITEM_PHOTO_DIR, BOX_PHOTO_DIR, LOCATION_PHOTO_DIR
from app.database import init_db, get_db
from app.models.item import Item
from app.models.box import Box
from app.models.location import Location
from app.models.category import Category
from app.services.auth_service import get_session_user
from app.routers import auth_router, items_router, boxes_router, categories_router, locations_router
from app.routers.photos import router as photos_router
from app.routers.export import router as export_router

app = FastAPI(title="irqhomedb", version="1.0.0")

# Add no-cache headers to all responses
from starlette.middleware.base import BaseHTTPMiddleware

class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

app.add_middleware(NoCacheMiddleware)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads/items", StaticFiles(directory=ITEM_PHOTO_DIR), name="item_photos")
app.mount("/uploads/boxes", StaticFiles(directory=BOX_PHOTO_DIR), name="box_photos")
app.mount("/uploads/locations", StaticFiles(directory=LOCATION_PHOTO_DIR), name="location_photos")

TEMPLATES_DIR = str(Path(__file__).parent / "templates")
jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def render_template(name: str, request: Request, **context):
    context.setdefault("request", request)
    return HTMLResponse(jinja_env.get_template(name).render(**context))

app.include_router(auth_router)
app.include_router(items_router)
app.include_router(boxes_router)
app.include_router(categories_router)
app.include_router(locations_router)
app.include_router(photos_router)
app.include_router(export_router)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    return render_template("dashboard.html", request,
        user=user,
        total_items=db.query(Item).count(),
        total_boxes=db.query(Box).count(),
        unidentified_items=db.query(Item).filter(Item.status == "unidentified").count(),
        unidentified_boxes=db.query(Box).filter(Box.status == "unidentified").count(),
        low_stock=db.query(Item).filter(Item.status == "identified", Item.quantity <= Item.min_quantity).count(),
    )

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return render_template("auth/login.html", request)

@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request, db: Session = Depends(get_db)):
    return render_template("upload.html", request, user=get_session_user(request, db))

@app.get("/items", response_class=HTMLResponse)
def items_page(request: Request, db: Session = Depends(get_db)):
    return render_template("items/list.html", request, user=get_session_user(request, db))

@app.get("/items/identify", response_class=HTMLResponse)
def identify_items_page(request: Request, db: Session = Depends(get_db)):
    return render_template("items/identify.html", request, user=get_session_user(request, db))

@app.get("/items/{item_id}", response_class=HTMLResponse)
def item_detail_page(request: Request, item_id: str, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    return render_template("items/detail.html", request, user=get_session_user(request, db), item=item)


@app.get("/items/{item_id}/edit", response_class=HTMLResponse)
def item_edit_page(request: Request, item_id: str, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    boxes = db.query(Box).order_by(Box.name).all()
    locations = db.query(Location).order_by(Location.name).all()
    categories = db.query(Category).order_by(Category.name).all()
    item_cat_ids = [c.id for c in (item.categories or [])]
    return render_template("items/edit.html", request,
        user=get_session_user(request, db),
        item=item, boxes=boxes, locations=locations,
        categories=categories, item_cat_ids=item_cat_ids)

@app.get("/boxes", response_class=HTMLResponse)
def boxes_page(request: Request, db: Session = Depends(get_db)):
    return render_template("boxes/list.html", request, user=get_session_user(request, db))

@app.get("/boxes/identify", response_class=HTMLResponse)
def identify_boxes_page(request: Request, db: Session = Depends(get_db)):
    return render_template("boxes/identify.html", request, user=get_session_user(request, db))

@app.get("/boxes/{box_id}", response_class=HTMLResponse)
def box_detail_page(request: Request, box_id: str, db: Session = Depends(get_db)):
    box = db.query(Box).filter(Box.id == box_id).first()
    return render_template("boxes/detail.html", request, user=get_session_user(request, db), box=box)


@app.get("/boxes/{box_id}/edit", response_class=HTMLResponse)
def box_edit_page(request: Request, box_id: str, db: Session = Depends(get_db)):
    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        raise HTTPException(status_code=404, detail="Box not found")
    locations = db.query(Location).order_by(Location.name).all()
    return render_template("boxes/edit.html", request,
        user=get_session_user(request, db), box=box, locations=locations)


@app.get("/boxes/{box_id}/add-items", response_class=HTMLResponse)
def box_add_items_page(request: Request, box_id: str, db: Session = Depends(get_db)):
    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        raise HTTPException(status_code=404, detail="Box not found")
    return render_template("boxes/add_items.html", request,
        user=get_session_user(request, db), box=box)

@app.get("/categories", response_class=HTMLResponse)
def categories_page(request: Request, db: Session = Depends(get_db)):
    return render_template("categories/manage.html", request, user=get_session_user(request, db))

@app.get("/locations", response_class=HTMLResponse)
def locations_page(request: Request, db: Session = Depends(get_db)):
    return render_template("locations/manage.html", request, user=get_session_user(request, db))

@app.get("/locations/{loc_id}", response_class=HTMLResponse)
def location_detail_page(request: Request, loc_id: int, db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.id == loc_id).first()
    return render_template("locations/detail.html", request, user=get_session_user(request, db), loc=loc)
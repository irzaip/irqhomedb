from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import STATIC_DIR, ITEM_PHOTO_DIR, BOX_PHOTO_DIR, LOCATION_PHOTO_DIR
from app.database import init_db
from app.routers import (
    auth_router, users_router, items_router, boxes_router, categories_router,
    locations_router, pages_router,
)
from app.routers.photos import router as photos_router
from app.routers.export import router as export_router
from app.routers.backup import router as backup_router
from app.services.bootstrap import seed_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_admin()
    yield


app = FastAPI(title="irqhomedb", version="1.0.0", lifespan=lifespan)


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

app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(items_router)
app.include_router(boxes_router)
app.include_router(categories_router)
app.include_router(locations_router)
app.include_router(photos_router)
app.include_router(export_router)
app.include_router(backup_router)

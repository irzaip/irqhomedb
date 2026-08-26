import os
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
ITEM_PHOTO_DIR = os.path.join(UPLOAD_DIR, "items")
BOX_PHOTO_DIR = os.path.join(UPLOAD_DIR, "boxes")
LOCATION_PHOTO_DIR = os.path.join(UPLOAD_DIR, "locations")
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/irqhomedb.db")

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))

# Auth
SECRET_KEY = os.getenv("SECRET_KEY", "irqhomedb-dev-secret-change-in-production")

# Photo
MAX_PHOTO_SIZE = 10 * 1024 * 1024  # 10MB
THUMBNAIL_SIZE = (300, 300)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Ensure dirs exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ITEM_PHOTO_DIR, exist_ok=True)
os.makedirs(BOX_PHOTO_DIR, exist_ok=True)
os.makedirs(LOCATION_PHOTO_DIR, exist_ok=True)
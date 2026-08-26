"""
Seed data: initial locations + admin user.
Run: python scripts/seed.py
"""
import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import init_db, SessionLocal
from app.models.user import User
from app.models.location import Location
from app.services.auth_service import hash_password


def seed():
    init_db()
    db = SessionLocal()

    # Create admin user if not exists
    admin = db.query(User).filter(User.username == "irza").first()
    if not admin:
        admin = User(
            username="irza",
            password_hash=hash_password("admin123"),
            display_name="Irza",
        )
        db.add(admin)

    asisten = db.query(User).filter(User.username == "asisten").first()
    if not asisten:
        asisten = User(
            username="asisten",
            password_hash=hash_password("asisten123"),
            display_name="Asisten",
        )
        db.add(asisten)

    # Seed locations
    seed_locations = [
        ("Rumah", None, "Rumah"),
        ("Lt 1", None, "Lantai 1"),
        ("Ruang Tamu", 2, "Ruang Tamu"),
        ("Dapur", 2, "Dapur"),
        ("Ruang Kerja", 2, "Ruang Kerja"),
        ("Ruang Makan", 2, "Ruang Makan"),
        ("Lt 2", None, "Lantai 2"),
        ("Kamar Utama", 7, "Kamar Utama"),
        ("Kamar Tamu", 7, "Kamar Tamu"),
        ("Garasi", 1, "Garasi"),
        ("Gudang", 1, "Gudang"),
        ("Rak Bawah", 5, "Rak Bawah Ruang Kerja"),
        ("Rak Tengah", 5, "Rak Tengah Ruang Kerja"),
        ("Rak Atas", 5, "Rak Atas Ruang Kerja"),
    ]

    existing = {l.name: l for l in db.query(Location).all()}
    for name, parent_id, room in seed_locations:
        if name not in existing:
            loc = Location(name=name, parent_id=parent_id, room=room)
            db.add(loc)

    db.commit()
    print("✅ Seed complete:")
    print(f"   Users: irza / admin123, asisten / asisten123")
    print(f"   Locations: {len(seed_locations)} created/verified")


if __name__ == "__main__":
    seed()
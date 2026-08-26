# irqhomedb

Inventory Barang Rumah Irza — **Photo-First** workflow.  
Foto dari HP → upload → identify di desktop.

---

## Cara Install & Jalankan

### 1. Setup Python

```bash
cd /home/irzaip/irqhomedb
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Seed Data

```bash
python scripts/seed.py
```

Buat akun: `irza` / `admin123` dan `asisten` / `asisten123`

### 3. Jalankan

```bash
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### 4. Akses dari HP

**Di Windows** — buka `http://localhost:8080` ✅

**Dari HP** — perlu 2 langkah:

**Langkah 1:** Jalankan `setup_akses_hp.bat` sebagai **Administrator**
- File ada di: `/home/irzaip/irqhomedb/setup_akses_hp.bat`
- Copy dulu ke Windows: `cp setup_akses_hp.bat /mnt/c/Users/`
- Klik kanan → **Run as administrator**

**Langkah 2:** Buka HP di browser:
```
http://192.168.30.50:8080
```

---

## Struktur

```
app/
├── main.py            # FastAPI entry + page routes
├── config.py          # Konfigurasi
├── database.py        # SQLAlchemy engine
├── models/            # 9 model (Box, Item, Category, dll)
├── routers/           # API endpoints
├── services/          # Auth + logic
├── templates/         # Jinja2 pages
└── static/            # CSS/JS
scripts/seed.py        # Seed data
```

## 9 Model Tabel

| Tabel | Fungsi |
|-------|--------|
| Box | Koper, laci, kardus — tempat penyimpanan |
| Item | Part/komponen — punya foto sendiri |
| Category | Multi kategori (many-to-many via ItemCategory) |
| Location | Hierarki ruangan |
| ItemPhoto | Foto item (multi-angle) |
| BoxPhoto | Foto box (multi-angle) |
| ItemCategory | Junction many-to-many |
| ItemLog | Audit trail |
| User | Auth |

## API Endpoints

- `POST /api/auth/login` — Login
- `GET/POST/PUT/DELETE /api/items` — CRUD Item
- `GET/POST/PUT/DELETE /api/boxes` — CRUD Box
- `GET/POST/PUT/DELETE /api/categories` — CRUD Kategori
- `GET/POST/PUT/DELETE /api/locations` — CRUD Lokasi
- `POST /api/upload` — Bulk upload foto
- `GET /api/export/csv` — Export CSV
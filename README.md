# irqhomedb

> **Inventory Barang Rumah** — Photo-First workflow.  
> Foto dari HP → Upload → Identify di Desktop.

Aplikasi inventaris barang rumah tangga dengan alur **photo-first**: foto dulu pake HP, urusan data entry dikerjakan belakangan di desktop. Cocok buat nyatet parts, komponen, spare part, kabel, baut — barang kecil yang sering berserakan dan gak keliatan.

---

## 📸 Alur Kerja

```
HP: 📸 Foto → Upload         → ✅ Selesai (di HP)
Desktop:                      → 🏷️ Identify → 📦 Data rapi
```

1. **Foto Box / Item** dari HP — langsung upload, gak perlu isi data dulu
2. **Buka Desktop** — lihat unidentified boxes & items
3. **Identify** — kasih nama, assign lokasi/box, kategori

### Hierarki

```
📍 Location (Ruangan / Rak)
   └── 📦 Box (Koper, Laci, Kardus, Case)
        └── 📦 Item (Part / Komponen / Barang)
```

---

## ✨ Fitur

| Fitur | Detail |
|-------|--------|
| 📸 **Photo-First Upload** | 1 foto = 1 item. Upload dari HP, isi data nanti |
| 🏷️ **Identify Workflow** | Identifikasi box & item yang belum punya nama |
| 📦 **Box Management** | Buat & edit box, assign ke lokasi, ganti foto |
| 📋 **Item CRUD** | Nama, jumlah, satuan, kategori, deskripsi, notes |
| 🏷️ **Multi Kategori (Tags)** | Many-to-many — item bisa masuk banyak kategori |
| 🔍 **Cari + Filter** | Cari nama/deskripsi/notes, filter box/kategori/lokasi/status |
| 🗑️ **Hapus dengan Konfirmasi** | Dari grid item & detail |
| 🔐 **Multi User** | Irza (admin) + Asisten |
| 📱 **Mobile-First** | UI responsif, hamburger menu, floating home button |
| 🖥️ **Desktop Layout** | Foto kiri, data/form kanan (3:4 portrait) |

---

## 🛠️ Tech Stack

| Lapisan | Teknologi |
|---------|-----------|
| Backend | Python + **FastAPI** |
| Database | **SQLite** via SQLAlchemy |
| Template | **Jinja2** |
| Frontend | HTML + CSS + Vanilla JS (no framework) |
| Auth | Session-based (itsdangerous) |
| Image | Pillow (thumbnails) |

---

## 🚀 Cara Install & Jalankan

### Persyaratan
- Python 3.10+
- WSL / Linux / macOS

### 1. Clone & Setup

```bash
git clone https://github.com/irzaip/irqhomedb.git
cd irqhomedb
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Seed Data (opsional)

```bash
python scripts/seed.py
```

Buat 2 akun demo:
- `irza` / `admin123`
- `asisten` / `asisten123`

### 3. Jalankan

```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Buka `http://localhost:8080`

### 4. Akses dari HP (jaringan WiFi rumah)

Jalankan port forwarding di Windows (Administrator):

```batch
:: setup_akses_hp.bat
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=192.168.30.50
netsh advfirewall firewall add rule name="irqhomedb" dir=in action=allow protocol=tcp localport=8080
```

Buka HP: `http://192.168.30.50:8080`

---

## 📁 Struktur Proyek

```
irqhomedb/
├── app/
│   ├── main.py              # FastAPI entry + page routes
│   ├── config.py            # Konfigurasi path, upload, db
│   ├── database.py          # SQLAlchemy engine + session
│   ├── models/              # 10 model SQLAlchemy
│   │   ├── item.py
│   │   ├── box.py
│   │   ├── location.py
│   │   ├── category.py
│   │   ├── item_category.py # Many-to-many junction
│   │   ├── item_photo.py
│   │   ├── box_photo.py
│   │   ├── location_photo.py
│   │   ├── log.py           # Audit trail (ItemLog)
│   │   └── user.py
│   ├── routers/             # API endpoints
│   │   ├── items.py         # CRUD item + identify
│   │   ├── boxes.py         # CRUD box + identify + edit
│   │   ├── categories.py    # CRUD kategori
│   │   ├── locations.py     # CRUD lokasi
│   │   ├── photos.py        # Upload & manage foto
│   │   ├── auth.py          # Login/logout
│   │   └── export.py        # Export CSV
│   ├── services/
│   │   └── auth_service.py  # Session auth
│   ├── templates/           # 17 halaman Jinja2
│   │   ├── base.html        # Layout: sidebar + main
│   │   ├── dashboard.html
│   │   ├── upload.html
│   │   ├── auth/login.html
│   │   ├── items/           # list, detail, edit, identify, add_photos
│   │   ├── boxes/           # list, detail, edit, identify, add_items
│   │   ├── categories/
│   │   ├── locations/
│   │   └── ...
│   └── static/              # CSS/JS
├── scripts/
│   └── seed.py              # Data awal
├── data/                    # SQLite DB (auto-created)
├── uploads/                 # Foto items / boxes / locations
│   ├── items/
│   ├── boxes/
│   └── locations/
└── requirements.txt
```

---

## 🧠 Data Model

| Tabel | Fungsi |
|-------|--------|
| `Location` | Ruangan / rak (punya foto sendiri) |
| `Box` | Koper, laci, kardus — tempat penyimpanan |
| `Item` | Part / komponen — entitas utama |
| `Category` | Tag / kategori (tree hierarkis) |
| `ItemCategory` | Junction many-to-many item ↔ kategori |
| `ItemPhoto` | Foto item (multi-angle) |
| `BoxPhoto` | Foto box (multi-angle) |
| `LocationPhoto` | Foto lokasi |
| `ItemLog` | Audit trail perubahan item |
| `User` | Akun (irza + asisten) |

---

## 🌐 API Endpoints

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| POST | `/api/auth/login` | Login |
| GET | `/api/items` | List item (search, filter) |
| GET | `/api/items/{id}` | Detail item |
| POST | `/api/items/{id}/edit` | Edit item |
| POST | `/api/items/{id}/identify` | Identify item |
| DELETE | `/api/items/{id}` | Hapus item |
| GET | `/api/boxes` | List box |
| GET | `/api/boxes/{id}` | Detail box |
| POST | `/api/boxes/{id}/edit` | Edit box |
| POST | `/api/boxes/{id}/identify` | Identify box |
| DELETE | `/api/boxes/{id}` | Hapus box |
| GET/POST | `/api/categories` | CRUD kategori |
| GET/POST | `/api/locations` | CRUD lokasi |
| POST | `/api/upload` | Upload foto → auto-create item |
| POST | `/api/items/{id}/photos` | Tambah foto ke item |
| POST | `/api/boxes/{id}/photos` | Tambah foto ke box |
| GET | `/api/export/csv` | Export CSV |

---

## 🖥️ Halaman Web

| Route | Halaman |
|-------|---------|
| `/` | Dashboard (stats) |
| `/upload` | Upload foto dari HP |
| `/items` | Grid item dengan search & filter |
| `/items/identify` | Identify unidentified items |
| `/items/{id}` | Detail item (foto kiri, data kanan) |
| `/items/{id}/edit` | Edit item |
| `/boxes` | List box |
| `/boxes/identify` | Identify unidentified boxes |
| `/boxes/{id}` | Detail box + isi item |
| `/boxes/{id}/edit` | Edit box + ganti foto |
| `/boxes/{id}/add-items` | Upload item langsung ke box |
| `/categories` | Manage kategori |
| `/locations` | Manage lokasi |
| `/locations/{id}` | Detail lokasi |

---

## 📱 Mobile vs Desktop

**Layout otomatis beda** via CSS media query (768px breakpoint):

| | Desktop (>768px) | Mobile (≤768px) |
|---|---|---|
| **Sidebar** | Selalu kelihatan (kiri) | Hamburger menu |
| **Detail/Edit** | Foto kiri 3:4, data/form kanan | Vertikal 1 kolom |
| **Home button** | Sembunyi | Floating di kanan bawah |

---

## 📄 Lisensi

Hak milik Irza Pulungan — Internal use.  
Tidak untuk didistribusikan ke publik.
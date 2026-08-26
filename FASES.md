# irqhomedb — Ringkasan Fase Implementasi

## Fase 0: Setup (1-2 hr)
Inisialisasi project + DB + Auth
- FastAPI + SQLAlchemy
- 9 model tabel (Box, Item, Category, Location, ItemPhoto, BoxPhoto, ItemCategory, ItemLog, User)
- Login/logout session
- Seed lokasi awal

## Fase 1: Upload (3-4 hr)
Photo-first — upload dari HP
- `POST /api/upload` — bulk multipart
- Halaman upload mobile-friendly
- Upload detect: foto → otomatis Box + Item (unidentified)
- BoxPhoto + ItemPhoto + thumbnail

## Fase 2: Identify (3-4 hr)
Data entry di desktop
- Identify Box: lihat foto, kasih nama, assign lokasi
- Identify Item: lihat foto, kasih nama, assign ke box + kategori
- CRUD Box + Category (many-to-many) + Location (tree)
- Box Detail — lihat isi item
- Search FTS5 (nama, deskripsi, notes, kategori)

## Fase 3: Browse (2 hr)
Navigasi & dashboard
- Item list/grid + thumbnail
- Box tree view (Location → Box)
- Dashboard: total items/boxes/unidentified/low stock
- Mobile responsive

## Fase 4: Export (1 hr)
Export & admin
- Export CSV/JSON items + boxes
- Backup DB
- Filter status
- User management

---

## Flow Ringkas

```
Fase 0 — Setup      ████░░░░░░░░░░
Fase 1 — Upload     ████████████░░
Fase 2 — Identify   ████████████░░
Fase 3 — Browse     ████████░░░░░░
Fase 4 — Export     ████░░░░░░░░░░
                    ───────────────
                    ~10-12 hari kerja
```

## Dependency Antar Fase

```
Fase 0 ──── harus selesai sebelum semua fase
    │
Fase 1 ──── bisa mulai setelah Fase 0
    │
Fase 2 ──── butuh Fase 1 (data dari upload)
    │
    ├── Fase 3 ──── butuh Fase 2 (data teridentifikasi)
    │
    └── Fase 4 ──── bisa jalan paralel dengan Fase 3
```
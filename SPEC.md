# irqhomedb — Spesifikasi Aplikasi

> **Dokumen:** Spesifikasi & Desain Aplikasi Inventory Rumah Irza  
> **Versi:** 1.0 (MVP)  
> **Tanggal:** 26 Agustus 2026  
> **Status:** Draft

---

## Daftar Isi

1. [Ringkasan Produk](#1-ringkasan-produk)
2. [Problem Statement](#2-problem-statement)
3. [Target User & Skenario](#3-target-user--skenario)
4. [Core Features (MVP)](#4-core-features-mvp)
5. [Future Features](#5-future-features)
6. [Tech Stack](#6-tech-stack)
7. [Data Model](#7-data-model)
8. [User Interface](#8-user-interface)
9. [API Design](#9-api-design)
10. [Struktur Direktori](#10-struktur-direktori)
11. [Fase Implementasi](#11-fase-implementasi)
12. [Constraint & Catatan](#12-constraint--catatan)

---

## 1. Ringkasan Produk

|**irqhomedb** adalah aplikasi inventarisasi barang-barang rumah tangga milik Irza — khususnya *small parts, komponen, dan benda kecil* yang selama ini berserakan tanpa sistem organisasi yang jelas.

Aplikasi ini berjalan di web lokal (local network) sehingga bisa diakses dari:
- Laptop/PC di rumah
- HP/tablet via browser (dalam jaringan WiFi rumah)
- Desktop langsung

Dua orang pengguna: **Irza** (pemilik) dan **asisten** — keduanya bisa menambah, mencari, dan mengelola data inventaris.

### Workflow Utama: Photo-First

**Prinsip:** Foto dulu, isi data belakangan.

**Hierarki Inventaris:**
```
Location (Ruangan / Rak)
    └── Box (Koper, Laci, Kardus, Case)
          └── Item (Part / Komponen)
```

1. 📸 **Foto Box** — foto koper / laci / case dari berbagai angle
2. 📸 **Foto Item** — foto part/komponen, apapun sudutnya
3. 📤 **Upload** — foto masuk ke server, otomatis jadi **2 jenis entitas terpisah**:
   - Entitas **Box** (tanpa nama) — foto box terasosiasi ke sini
   - Entitas **Item** (tanpa nama) — foto part terasosiasi ke sini
4. 💻 **Buka Desktop** — lihat unidentified boxes + unidentified items
5. ✏️ **Identify Box** — kasih nama box, assign ke lokasi (ruangan/rak)
6. ✏️ **Identify Item** — kasih nama item, assign ke box yang sudah ada, kasih kategori

Satu Box bisa menampung banyak Item.  
ItemPhoto = foto part. BoxPhoto = foto box (multi-angle).

Dengan cara ini, workflow HP super cepat (foto → upload selesai), dan data entry/rapihin dikerjakan nanti di desktop yang lebih nyaman.

---

## 2. Problem Statement

### Masalah Saat Ini

- **Parts & komponen kecil** — baut, konektor, kabel, adaptor, spare part — berserakan di berbagai tempat tanpa katalog
- **Tidak ada catatan** — "barang ini ada di mana?" hanya diandalkan ke ingatan
- **Duplikasi & kebingungan** — beli barang yang sama karena lupa sudah punya
- **Asisten tidak punya akses informasi** — kalau Irza tidak di rumah, asisten tidak tahu lokasi barang

### Solusi

Database inventory yang:
- Mencatat **nama, kategori, lokasi, jumlah, foto, dan catatan** setiap barang
- Bisa **dicari** dengan cepat (nama, kategori, lokasi, tag)
- Bisa **difoto** langsung dari HP saat memasukkan data
- Bisa **diakses bersama** oleh Irza dan asisten

---

## 3. Target User & Skenario

### Persona 1: Irza (Pemilik)

| Aspek | Detail |
|-------|--------|
| **Peran** | Pemilik rumah, organizer utama |
| **Kebutuhan** | Memasukkan barang baru, mencari barang, update stok/lokasi |
| **Akses** | Laptop utama + HP |
| **Frekuensi** | Beberapa kali seminggu — saat beli part baru, saat perlu cari sesuatu |

### Persona 2: Asisten

| Aspek | Detail |
|-------|--------|
| **Peran** | Ikut mengelola inventaris |
| **Kebutuhan** | Mencari lokasi barang, menandai barang yang dipindah/dipakai, menambah catatan |
| **Akses** | HP (mobile browser) |
| **Frekuensi** | Harian — saat merapikan, mencari barang, atau menyimpan barang baru |

### Skenario Umum

**Skenario A: Photo-First Upload (dari HP)**

1. **Beli Part Baru** — Irza baru pulang belanja part. Buka irqhomedb dari HP → klik **Upload Foto**.
2. **Foto Box** — Foto dulu koper / laci / kardus tempat nyimpen — dari beberapa sudut.
3. **Foto Item** — Foto part-partnya — bisa sekaligus banyak, dari berbagai angle.
4. **Upload** — Upload semua foto sekaligus. Server bikin **entitas Box** (tanpa nama) + **entitas Item** (tanpa nama), foto terasosiasi otomatis.
5. **Beres di HP** — Tutup HP, lanjut aktivitas lain.

**Skenario B: Data Entry — Identify Box & Item (dari Desktop/Laptop)**

6. **Buka Dashboard** — Lihat unidentified boxes (👤) dan unidentified items (📦).
7. **Identify Box Dulu** — Klik box, lihat foto-foto box dari berbagai angle. Kasih nama box (misal "Koper Alat Tukang"), assign ke lokasi (Ruang Kerja > Rak Bawah).
8. **Identify Item** — Klik item, lihat foto-foto part. Kasih nama, assign ke box yang sudah diidentifikasi, kasih kategori.
9. **Simpan** — Semua terstruktur: Lokasi → Box → Item.

**Skenario C: Mencari Barang**

10. **Cari Kabel USB-C** — Ketik "usb c", muncul foto part + nama + box + lokasi.
11. **Ambil** — Langsung tahu: "Ada di Box Kecil Laci Atas, Ruang Kerja".

**Skenario D: Update & Audit**

12. **Pindah Box** — Pindahkan satu box ke rak lain — semua item di dalamnya ikut pindah.
13. **Cari Barang Dalam Box** — Buka detail box → lihat daftar semua item di dalamnya.
14. **Audit** — Buka per lokasi → lihat semua box di situ → cek isi.

---

## 4. Core Features (MVP)

### F-01: Manajemen Item (CRUD)

| Sub-feature | Prioritas |
|-------------|-----------|
| Tambah item baru via form (nama, kategori, box, jumlah, dll) | P0 |
| Edit item (nama, kategori, box, jumlah, deskripsi) | P0 |
| Item lahir dari upload foto — **nama bisa kosong** (status: unidentified) | P0 |
| Assign item ke box — 1 box bisa punya banyak item | P0 |
| Lihat isi box — tampilkan daftar semua item dalam suatu box | P0 |
| Hapus item | P0 |
| Duplikasi item (fast-entry untuk item serupa) | P1 |

### F-02: Kategori (Multi — seperti TAG)

- Item bisa punya **banyak kategori** (many-to-many), bukan cuma satu
- Kategori berfungsi seperti **tag** — satu item bisa masuk "Elektronik" DAN "Kabel" DAN "USB" sekaligus
- Kategori tetap punya hierarki (parent/child) untuk navigasi tree
- Contoh: USB-C cable → kategori: `Elektronik > Kabel > USB`, `Aksesoris HP`, `Charger`
- Filter / browse per kategori — tampilkan item yang punya kategori tersebut
- Manage kategori: tambah, edit, hapus, atur parent

### F-03: Box — Tempat Penyimpanan

**Box** adalah entitas utama — tempat fisik dimana item disimpan. Contoh: koper, laci lemari, kardus, case, rak kecil, toolbox.

| Sub-feature | Prioritas |
|-------------|-----------|
| **CRUD Box** — tambah/edit/hapus box | P0 |
| Box bisa lahir dari upload foto — **nama bisa kosong** (status: unidentified) | P0 |
| Satu box punya **banyak foto sendiri** (BoxPhoto) — dari berbagai angle | P0 |
| Assign box ke lokasi (Location) — ruangan / rak tempat box itu berada | P0 |
| Lihat isi box — daftar semua item di dalamnya | P0 |
| Pindah box — ganti lokasi, semua item di dalamnya ikut pindah | P0 |
| Tampilkan box tree: Location > Box > Items | P1 |

### F-04: Lokasi (Ruangan / Rak)

| Sub-feature | Prioritas |
|-------------|-----------|
| Hierarki lokasi: *Rumah > Lt 1 > Ruang Kerja > Rak Kiri* | P0 |
| Satu lokasi bisa punya banyak box | P0 |
| Filter / browse per lokasi — tampilkan semua box di lokasi itu | P0 |

### F-05: Pencarian & Filter

- Pencarian teks cepat mencakup: **nama item, nama box, deskripsi, keterangan/notes, kategori, dan tags**
- Full-text search (FTS5) — search langsung tembus ke deskripsi & notes
- Filter kombinasi: kategori + box + lokasi + stok minimum + status (unidentified/identified)
- Hasil pencarian menampilkan foto thumbnail item

### F-06: Foto Item & Box — Multi-Angle

| Sub-feature | Prioritas |
|-------------|-----------|
| **Bulk upload foto via HP** — pilih multiple foto dari galeri, upload sekaligus | P0 |
| Upload otomatis bikin **2 entitas terpisah**: Box (unidentified) + Item (unidentified) | P0 |
| **Box** punya banyak foto sendiri (BoxPhoto) — dari berbagai angle | P0 |
| **Item** punya banyak foto sendiri (ItemPhoto) — dari berbagai angle part | P0 |
| Pas upload, user bisa **grouping foto** — centang mana foto box, mana foto item | P0 |
| Preview foto di detail (besar, bisa zoom, slideshow) | P0 |
| Thumbnail di daftar pencarian | P0 |
| Tidak ada konsep "foto utama" — semua foto setara, diurutkan upload | P0 |

### F-07: Stok & Jumlah

- Set quantity per item
- Tampilkan item dengan stok rendah (threshold configurable)
- Log perubahan stok (opsional di MVP)

### F-08: Multi-User Sederhana

- Login sederhana (username/password)
- Dua akun: Irza + asisten
- Semua user bisa read & write (no complex permissions di MVP)
- Riwayat siapa yang terakhir mengubah (audit trail dasar)

### F-09: Export Data

| Sub-feature | Prioritas |
|-------------|-----------|
| Export item list ke CSV | P0 |
| Export item list ke JSON | P0 |
| Backup database (download SQLite file) | P1 |

### F-10: Unidentified Boxes & Items Queue

| Sub-feature | Prioritas |
|-------------|-----------|
| **Halaman Upload Foto** dari HP — pilih foto, upload, jadi Box atau Item | P0 |
| Upload foto box → otomatis bikin **Box** (unidentified) dengan BoxPhoto | P0 |
| Upload foto part → otomatis bikin **Item** (unidentified) dengan ItemPhoto | P0 |
| **Halaman "Identify Boxes"** — daftar box yang belum punya nama | P0 |
| **Halaman "Identify Items"** — daftar item yang belum punya nama | P0 |
| Identify Box: lihat foto-foto box, kasih nama, assign ke lokasi | P0 |
| Identify Item: lihat foto-foto part, kasih nama, assign ke box, kasih kategori | P0 |
| Setelah diisi → status berubah jadi `identified` → muncul di inventaris normal | P0 |
| Filter: "Semua" / "Unidentified" / "Identified" | P0 |

---

## 5. Future Features (Post-MVP)

| Fitur | Deskripsi |
|-------|-----------|
| **QR Code** | Generate & scan QR code per item — tempel di rak, scan untuk lihat detail |
| **Barcode Scanner** | Scan barcode produk untuk auto-fill nama & kategori |
| **Receipt Upload** | Foto struk belanja — otomatis OCR nama barang |
| **Shopping List** | Tandai item yang habis → generate list belanja |
| **Move History** | Riwayat lengkap perpindahan barang (lokasi sebelum → sesudah) |
| **Photo Gallery View** | Grid view foto semua barang — visual browsing |
| **Location Map** | Denah rumah sederhana — klik ruangan → lihat barang di situ |
| **REST API** | Jika nanti perlu integrasi dengan sistem lain |
| **Notifications** | Reminder audit bulanan, stok menipis |
| **PWA** | Installable ke home screen HP |

---

## 6. Tech Stack

### Recommended

| Layer | Teknologi | Alasan |
|-------|-----------|--------|
| **Backend** | FastAPI (Python 3.11+) | Sama dengan stack Irza (VIDIVICI), ringan, cepat, auto docs |
| **Database** | SQLite + SQLAlchemy | Zero-config, file-based, cukup untuk single-server lokal |
| **Frontend** | HTML + JS (SPA) + HTMX | Minimal dependencies, ringan, cocok untuk mobile browser |
| **CSS** | TailwindCSS (CDN) atau custom | Responsive, mobile-first |
| **Image Storage** | File system (`uploads/`) + thumbnail cache | Sederhana, lokal |
| **Server** | Uvicorn (local) + optional nginx reverse proxy | |

### Alternatif (simpler)

| Layer | Opsi |
|-------|------|
| **All-in-one** | Django + SQLite (lebih berat tapi built-in admin panel) |
| **Frontend heavy** | Flask + Jinja2 (server-side rendering, tanpa JS SPA) |
| **Desktop** | Tauri + SQLite (Rust-based desktop app) — lebih complex setup |

**Rekomendasi:** FastAPI + SQLite + HTML/HTMX — paling cocok dengan skill set Irza dan kebutuhan lokal.

---

## 7. Data Model

### Item

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | UUID / auto-increment | ✓ | Primary key |
| `status` | String (enum) | ✓ (default `unidentified`) | `unidentified` → `identified` → `archived` |
| `name` | String (200) | ✗ (null allowed) | **Bisa kosong** — diisi setelah upload (desktop) |
| `description` | Text (1000) | ✗ | Deskripsi, notes |
| `box_id` | FK → Box | ✗ (null allowed saat unidentified) | Box tempat item disimpan |
| `quantity` | Integer | ✓ (default 1) | Jumlah stok |
| `min_quantity` | Integer | ✗ (default 0) | Threshold stok rendah |
| `unit` | String (20) | ✗ (default "pcs") | Satuan (pcs, meter, set, dll) |
| `tags` | String (JSON array) | ✗ | Tags bebas untuk search |
| `notes` | Text | ✗ | Catatan tambahan |
| `upload_session_id` | String (UUID) | ✗ | ID sesi upload |
| `created_by` | FK → User | ✓ | Pembuat entry |
| `updated_by` | FK → User | ✓ | Pengedit terakhir |
| `created_at` | DateTime | auto | |
| `updated_at` | DateTime | auto | |

### Category

| Field | Type | Notes |
|-------|------|-------|
| `id` | auto-increment | |
| `name` | String (100) | Nama kategori |
| `parent_id` | FK → Category (nullable) | Hierarki kategori |
| `icon` | String (20) | Emoji / icon name |
| `sort_order` | Integer | Urutan tampilan |

### Location

| Field | Type | Notes |
|-------|------|-------|
| `id` | auto-increment | |
| `name` | String (200) | Nama lokasi |
| `parent_id` | FK → Location (nullable) | Hierarki lokasi |
| `room` | String (100) | Nama ruangan (denormalized untuk fast filter) |
| `description` | Text | Deskripsi lokasi |
| `sort_order` | Integer | |

### Box

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | UUID / auto-increment | ✓ | Primary key |
| `status` | String (enum) | ✓ (default `unidentified`) | `unidentified` → `identified` → `archived` |
| `name` | String (200) | ✗ (null allowed) | Nama box — bisa kosong pas upload |
| `description` | Text (1000) | ✗ | Deskripsi box |
| `location_id` | FK → Location | ✗ (null allowed) | Lokasi tempat box diletakkan |
| `upload_session_id` | String (UUID) | ✗ | ID sesi upload |
| `created_by` | FK → User | ✓ | Pembuat entry |
| `updated_by` | FK → User | ✓ | Pengedit terakhir |
| `created_at` | DateTime | auto | |
| `updated_at` | DateTime | auto | |

### ItemPhoto

| Field | Type | Notes |
|-------|------|-------|
| `id` | auto-increment | |
| `item_id` | FK → Item | |
| `filename` | String | File path |
| `sort_order` | Integer | Urutan tampilan |
| `caption` | String (200) | Keterangan foto (misal: "tampak atas", "samping") |
| `created_at` | DateTime | |

> ✅ ItemPhoto = foto dari item (part) saja. Foto box punya tabel sendiri.

### BoxPhoto

| Field | Type | Notes |
|-------|------|-------|
| `id` | auto-increment | |
| `box_id` | FK → Box | |
| `filename` | String | File path |
| `sort_order` | Integer | Urutan tampilan |
| `caption` | String (200) | Keterangan foto (misal: "isi box penuh", "label box") |
| `created_at` | DateTime | |

> ✅ BoxPhoto = foto dari box (koper/laci/kardus) dari berbagai angle.

### ItemCategory (Many-to-Many)

| Field | Type | Notes |
|-------|------|-------|
| `item_id` | FK → Item | |
| `category_id` | FK → Category | |

> Satu item bisa punya banyak kategori (seperti tag).  
> Satu kategori bisa dipakai banyak item.

### ItemLog (Audit Trail)

| Field | Type | Notes |
|-------|------|-------|
| `id` | auto-increment | |
| `item_id` | FK → Item | |
| `user_id` | FK → User | |
| `action` | String | created, updated, moved, quantity_changed, deleted |
| `old_value` | Text (JSON) | Nilai sebelum |
| `new_value` | Text (JSON) | Nilai sesudah |
| `created_at` | DateTime | |

### User

| Field | Type | Notes |
|-------|------|-------|
| `id` | auto-increment | |
| `username` | String (50) | Login ID |
| `password_hash` | String | bcrypt hashed |
| `display_name` | String (100) | Nama tampilan |
| `is_active` | Boolean | |
| `created_at` | DateTime | |

---

## 8. User Interface

### Layout Umum

```
+------------------------------------------+
| Header: Logo + Search Bar + User     |
+----------+-------------------------------+
| Sidebar  | Main Content Area              |
| (nav)    |                                |
|          |  - 📤 Upload (HP)             |
|          |  - 📦 Boxes (⚠️ N unid)       |
| - All    |  - 📦 Items (⚠️ N unid)       |
| - By Box |  - Item List / Grid            |
| - By Cat |  - Item Detail                 |
| - By Loc |  - Form Tambah/Edit            |
| - Tags   |  - Box Detail                  |
| - Low    |  - Dashboard / Stats           |
|   Stok   |                                |
+----------+-------------------------------+
```

**Mobile:** Sidebar collapse jadi hamburger menu. Content full-width.

### Halaman

| Page | Route | Fungsi |
|------|-------|--------|
| **Dashboard** | `/` | Statistik: total items, total boxes, unidentified count, stok rendah |
| **Upload Foto** | `/upload` | **Mobile-first**: pilih dari galeri, grouping box/item, upload bulk |
| **Boxes** | `/boxes` | Daftar semua box (tree/list), filter status |
| **Identify Boxes** | `/boxes/identify` | Box unidentified — lihat foto, kasih nama, assign lokasi |
| **Box Detail** | `/boxes/{id}` | Detail box + foto-foto box + daftar isi (items) |
| **Identify Items** | `/items/identify` | Item unidentified — lihat foto, kasih nama, assign ke box, kategori |
| **Item List** | `/items` | Grid/list view, search, filter, sort |
| **Item Detail** | `/items/{id}` | Detail item + foto part + info box+location |
| **Item Edit** | `/items/{id}/edit` | Form edit barang |
| **Item Add** | `/items/new` | Form tambah barang (dari desktop) |
| **Categories** | `/categories` | Manage kategori (tree view) |
| **Locations** | `/locations` | Manage lokasi (tree view) |
| **Login** | `/login` | Login form |

### Komponen UI Utama

1. **Search Bar** — selalu visible di header, autocomplete dropdown hasil
2. **Item Card** — thumbnail foto + nama (atau "Belum Diidentifikasi" jika kosong) + kategori + lokasi + quantity
3. **Photo Uploader (Mobile)** — pilih multiple foto dari galeri HP, grouping part/box via toggle/centang, progress bar upload
4. **Identify Card** — tampilkan 2 foto bersebelahan (part kiri, box kanan), form singkat nama+kategori+lokasi di bawahnya, tombol "Simpan & Next"
5. **Category/Location Tree** — hierarchical navigation di sidebar
6. **Filter Bar** — dropdown kategori + lokasi + slider stok minimum + filter status (all/unidentified/identified)
7. **Quick Stats** — di dashboard: total items, total categories, unidentified count, low stock count

### Wireframe: Halaman Upload (Mobile — HP)

```
┌─────────────────────────────┐
│ ← Upload Foto        👤 Irza│
├─────────────────────────────┤
│                             │
│   📷  📷  📷  📷  📷  📷   │
│   📷  📷  📷  📷  📷  📷   │  ← grid galeri
│   📷  📷  📷  📷  📷  📷   │
│                             │
│ ┌─ Foto Box ─┐ ┌─ Item ──┐ │
│ │📸  dipilih 4│ │📸  dipilih 8│← grouping
│ │(koper/laci) │ │(part²)  │ │   centang
│ └─────────────┘ └─────────┘ │
│                             │
│ [ ⚡ Upload 12 Foto ]       │
│ ████████████░░░░░ 70%      │  ← progress bar
└─────────────────────────────┘
```

### Wireframe: Identify Box (Desktop)

```
┌─────────────────────────────────────────┐
│ ← Identify Boxes    ⚠️ 3 unidentified  │
├─────────────────────────────────────────┤
│                                         │
│ ┌── Box #2 of 3 ──────────────────┐    │
│ │ ┌───── FOTO BOX ────────────┐  │    │
│ │ │ [📸][📸][📸] ← thumbnail  │  │    │
│ │ │ ┌───────────────────────┐ │  │    │
│ │ │ │ 📸 (besar, aktif)     │ │  │    │
│ │ │ │ koper alat, tampak    │ │  │    │
│ │ │ │ depan                 │ │  │    │
│ │ │ └───────────────────────┘ │  │    │
│ │ └───────────────────────────┘  │    │
│ │                                │    │
│ │ Nama Box: [Koper Alat Tukang] │    │
│ │ Lokasi:   [Ruang Kerja ▼]     │    │
│ │           [Rak Bawah ▼]       │    │
│ │ Notes:    [________________]  │    │
│ │                                │    │
│ │ [← Prev] [✓ Simpan & Next]    │    │
│ └────────────────────────────────┘    │
│                                         │
│ ─── Daftar Box ───                     │
│ ┌────┐ ┌────┐ ┌────┐                  │
│ │📸  │ │📸  │ │📸  │                  │
│ │--  │ │ ✓  │ │--  │  ← sudah diisi   │
│ └────┘ └────┘ └────┘                  │
└─────────────────────────────────────────┘
```

### Wireframe: Identify Item (Desktop)

```
┌─────────────────────────────────────────┐
│ ← Identify Items   ⚠️ 12 unidentified  │
├─────────────────────────────────────────┤
│                                         │
│ ┌── Item #5 of 12 ────────────────┐    │
│ │ ┌───── FOTO ITEM ───────────┐  │    │
│ │ │ [📸][📸][📸][📸] thumb    │  │    │
│ │ │ ┌──────────────────────┐ │  │    │
│ │ │ │ 📸 (besar)           │ │  │    │
│ │ │ │ kabel USB, tampak    │ │  │    │
│ │ │ │ samping              │ │  │    │
│ │ │ └──────────────────────┘ │  │    │
│ │ └──────────────────────────┘  │    │
│ │                                │    │
│ │ Nama:   [USB-C Cable 2m]      │    │
│ │ Box:    [Koper Alat Tukang ▼] │    │
│ │ Kategori: [+ Tambah kategori] │    │
│ │   [Elektronik ×] [Kabel ×]    │    │
│ │   [USB ×]                     │    │
│ │ Jumlah: [5 ] pcs              │    │
│ │ Deskripsi: [Kabel fast charge]│    │
│ │ Notes:    [Beli di Tokped...] │    │
│ │                                │    │
│ │ [← Prev] [✓ Simpan & Next]    │    │
│ └────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### Wireframe: Box Detail

```
┌─────────────────────────────────────────┐
│ ← Boxes          Edit Box      + Add Item│
├─────────────────────────────────────────┤
│                                         │
│ ┌── FOTO BOX ──────────────┐           │
│ │ [📸][📸][📸] ← thumb    │           │
│ │ ┌──────────────────────┐ │           │
│ │ │ 📸 (besar, aktif)    │ │           │
│ │ │ koper alat terbuka   │ │           │
│ │ └──────────────────────┘ │           │
│ └──────────────────────────┘           │
│                                         │
│ 🧰 Koper Alat Tukang                    │
│ 📍 Ruang Kerja > Rak Bawah              │
│ 📝 Isi: kunci, obeng, tang, kabel      │
│                                         │
│ ─── Isi Box (12 items) ────            │
│ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐       │
│ │📸   │ │📸   │ │📸   │ │📸   │       │
│ │USB-C│ │Obeng│ │Tang │ │Kunci│       │
│ │ 5pcs│ │ 1pc │ │ 2pc │ │ 3pc │       │
│ └─────┘ └─────┘ └─────┘ └─────┘       │
│                                         │
│ ⏰ Dibuat: 25 Agt 2026 · 👤 Irza       │
└─────────────────────────────────────────┘
```

---

## 9. API Design

### Backend Endpoints (REST-like)

#### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login, return session token |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Current user info |

#### Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/items` | List items (search, filter, pagination) |
| GET | `/api/items/{id}` | Get item detail |
| POST | `/api/items` | Create item |
| PUT | `/api/items/{id}` | Update item |
| DELETE | `/api/items/{id}` | Delete item |
| GET | `/api/items/unidentified` | List unidentified items (no name yet) |
| POST | `/api/items/{id}/identify` | Identify item (isi nama, box, kategori, dll) |

#### Boxes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/boxes` | List all boxes (search, filter, pagination) |
| GET | `/api/boxes/{id}` | Get box detail + items inside |
| POST | `/api/boxes` | Create box |
| PUT | `/api/boxes/{id}` | Update box |
| DELETE | `/api/boxes/{id}` | Delete box |
| GET | `/api/boxes/unidentified` | List unidentified boxes (no name yet) |
| POST | `/api/boxes/{id}/identify` | Identify box (isi nama, lokasi, dll) |

#### Photos

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | **Bulk upload foto** (multipart) — otomatis detect: foto item → Item, foto box → Box |
| POST | `/api/items/{id}/photos` | Upload photo(s) ke item existing (ItemPhoto) |
| POST | `/api/boxes/{id}/photos` | Upload photo(s) ke box existing (BoxPhoto) |
| DELETE | `/api/items/{id}/photos/{photo_id}` | Delete item photo |
| DELETE | `/api/boxes/{id}/photos/{photo_id}` | Delete box photo |

#### Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories` | List all (tree) |
| POST | `/api/categories` | Create |
| PUT | `/api/categories/{id}` | Update |
| DELETE | `/api/categories/{id}` | Delete |

#### Locations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/locations` | List all (tree) |
| POST | `/api/locations` | Create |
| PUT | `/api/locations/{id}` | Update |
| DELETE | `/api/locations/{id}` | Delete |

#### Export

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/export/csv` | Download CSV |
| GET | `/api/export/json` | Download JSON |

Response format: JSON dengan wrapper `{"success": true, "data": ..., "error": ...}`

---

## 10. Struktur Direktori

```
irqhomedb/
├── SPEC.md                         # ← Dokumen ini
├── README.md                       # Panduan instalasi & penggunaan
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app entry point
│   ├── config.py                   # Settings & config
│   ├── database.py                 # SQLAlchemy engine & session
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── item.py                 # Item model
│   │   ├── box.py                  # Box model (koper, laci, kardus)
│   │   ├── category.py             # Category model
│   │   ├── location.py             # Location model
│   │   ├── item_photo.py           # ItemPhoto model
│   │   ├── box_photo.py            # BoxPhoto model (foto box)
│   │   ├── item_category.py        # ItemCategory junction table
│   │   ├── log.py                  # ItemLog model
│   │   └── user.py                 # User model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── item.py
│   │   ├── box.py
│   │   ├── category.py
│   │   ├── location.py
│   │   └── user.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── items.py                # /api/items routes
│   │   ├── boxes.py                # /api/boxes routes
│   │   ├── categories.py
│   │   ├── locations.py
│   │   ├── photos.py               # /api/upload + photo routes
│   │   ├── auth.py
│   │   └── export.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── item_service.py
│   │   ├── box_service.py
│   │   ├── photo_service.py        # Image processing, thumbnails (item + box)
│   │   ├── search_service.py       # FTS5 search
│   │   └── export_service.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── upload.html             # Upload page (mobile-first)
│   │   ├── boxes/
│   │   │   ├── list.html
│   │   │   ├── detail.html         # Box detail + items inside
│   │   │   └── identify.html       # Identify box
│   │   ├── items/
│   │   │   ├── list.html
│   │   │   ├── detail.html
│   │   │   ├── form.html
│   │   │   └── identify.html       # Identify item
│   │   ├── categories/
│   │   │   └── manage.html
│   │   ├── locations/
│   │   │   └── manage.html
│   │   └── auth/
│   │       └── login.html
│   │
│   └── static/
│       ├── css/
│       │   └── app.css             # Custom styles
│       ├── js/
│       │   └── app.js              # Client-side interactions
│       └── images/
│           └── (icons, logo)
│
├── uploads/                        # Uploaded photos (gitignored)
│   └── items/
│       └── (item_id-based folders)
│
├── data/
│   └── irqhomedb.db                # SQLite database file
│
├── scripts/
│   ├── seed.py                     # Seed data (sample categories/locations)
│   └── backup.py                   # Backup database script
│
└── .gitignore
```

---

## 11. Fase Implementasi

### Fase 0: Setup (1-2 hari)

- [ ] Inisialisasi project: FastAPI + SQLAlchemy + template structure
- [ ] Setup database: models definition (Item, Box, Category, Location, ItemPhoto, BoxPhoto, ItemCategory, ItemLog, User)
- [ ] Auth system: login/logout, session management
- [ ] Seed data: lokasi awal (Rumah, Lt 1, Ruang Kerja, dll)

### Fase 1: Photo-First Upload (3-4 hari)

- [ ] **Bulk upload endpoint** (`POST /api/upload`) — multipart, multiple files
- [ ] Upload page UI mobile-first — foto box vs foto item grouping
- [ ] Upload detect: foto → Box (unidentified) + foto → Item (unidentified)
- [ ] Box model + BoxPhoto model
- [ ] Item model + ItemPhoto model (item punya foto sendiri)
- [ ] Serve uploaded photos via static route + thumbnail generation

### Fase 2: Identify & Data Entry (3-4 hari)

- [ ] **Identify Box** page UI — lihat foto box, kasih nama, assign lokasi
- [ ] **Identify Item** page UI — lihat foto item, kasih nama, assign ke box + kategori
- [ ] Box CRUD (backend + frontend list/detail/edit)
- [ ] Item → Box assignment (dropdown box)
- [ ] Box Detail page — tampilkan daftar item di dalam box
- [ ] Category CRUD + many-to-many (ItemCategory)
- [ ] Location CRUD + tree UI
- [ ] Search backend (FTS5) — search item name, box name, description, notes, category

### Fase 3: Browse & Polish (2 hari)

- [ ] Item list/grid view dengan thumbnail
- [ ] Item detail page (foto item + info box/location)
- [ ] Box list + tree view (Location → Box)
- [ ] Dashboard with stats (total items, total boxes, unidentified count, low stock)
- [ ] Low stock indicator
- [ ] Mobile responsive seluruh halaman

### Fase 4: Export & Admin (1 hari)

- [ ] Export CSV/JSON (items + boxes)
- [ ] Database backup
- [ ] Filter status: all / unidentified / identified
- [ ] User management (add/change password)

### Future

- [ ] QR Code generation & scanning
- [ ] Barcode OCR
- [ ] PWA

---

## 12. Constraint & Catatan

### Performance

- Database: **SQLite** — cukup untuk ribuan item. Hindari concurrent write dari banyak user sekaligus (SQLite write lock).
- Foto: Simpan di filesystem, bukan di DB. Gunakan kompresi JPEG (max 1024px) untuk thumbnail.
- Search: **SQLite FTS5** untuk full-text search — index mencakup nama item, nama box, deskripsi, notes, kategori, dan tags. Pencarian cepat tanpa LIKE scan.

### Security (local network)

- Walaupun di local network, tetap pakai **password login** — akses dari tamu atau device tak dikenal perlu dicegah.
- Session menggunakan JWT atau session cookie.
- Upload foto: validasi tipe file (hanya image), batasi ukuran (max 10MB per file).

### Deployment

1. `pip install -r requirements.txt`
2. `cd app && uvicorn main:app --host 0.0.0.0 --port 8080`
3. Buka dari HP: `http://<ip-laptop>:8080`
4. Opsional: buat systemd service atau startup script

### Development Workflow

1. Backend-first: semua API endpoint dulu, test via Swagger UI (FastAPI built-in `/docs`)
2. Frontend: Jinja2 templates + vanilla JS (HTMX jika mau lebih interaktif)
3. Testing: pytest untuk backend API tests
4. Git: commit per feature, push ke repo lokal

---

> **irqhomedb** — *Organized home, clear mind.*

---
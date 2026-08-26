# Cara Akses irqhomedb dari HP

## Kenapa HP Tidak Bisa Akses?

**WSL itu virtual machine**, punya IP sendiri (172.18.237.85) — ini alamat internal
yang cuma dikenal sama Windows. HP di WiFi rumah (192.168.30.x) tidak bisa
menjangkau IP WSL secara langsung.

Yang bisa akses WSL:
- ✅ Dari Windows: `http://localhost:8080`
- ✅ Dari Windows: `http://172.18.237.85:8080`
- ❌ Dari HP: `http://192.168.30.50:8080` — **TIDAK BISA** (default)

Supaya bisa, kita perlu:
1. Buka firewall Windows untuk port 8080
2. Forward port 8080 dari Windows → WSL
3. HP akses lewat IP Windows

---

## Step 1: Jalankan Server

Buka terminal WSL / Ubuntu, jalankan:

```bash
cd /home/irzaip/irqhomedb
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Biarkan terminal ini terbuka — jangan ditutup.

---

## Step 2: Copy File Setup ke Windows

Di terminal WSL (buka terminal baru), ketik:

```bash
cp /home/irzaip/irqhomedb/setup_akses_hp.bat /mnt/c/Users/
```

---

## Step 3: Jalankan File Setup sebagai Administrator

**Buka File Explorer di Windows**, masuk ke folder:

```
C:\Users\
```

Cari file **`setup_akses_hp.bat`**.

**Klik kanan** file tersebut → pilih **"Run as administrator"**.
Klik **Yes** kalau muncul UAC (User Account Control).

File ini akan menjalankan 3 perintah:

```
[1/3] netsh advfirewall firewall add rule ...
    → Buka firewall port 8080

[2/3] netsh interface portproxy add ...
    → Forward port 8080 dari Windows → WSL

[3/3] netsh interface portproxy show all
    → Verifikasi apakah forwarding berhasil
```

Kalau berhasil, akan muncul tampilan:

```
Listen on ipv4:             Connect to ipv4:
Address         Port        Address         Port
--------------- ----------  --------------- ----------
0.0.0.0         8080        172.18.237.85   8080
```

---

## Step 4: Akses dari HP

**Pastikan HP terhubung ke WiFi yang sama** dengan laptop.

Buka browser di HP, ketik:

```
http://192.168.30.50:8080
```

Kalau muncul halaman login ✅ — **berhasil!**

Login:
- **Username:** irza
- **Password:** admin123

---

## Kalau Masih Gagal

### A. Firewall masih blocking

Coba matikan sementara firewall Windows:
1. Buka **Windows Security** → **Firewall & network protection**
2. Klik jaringan yang aktif (Domain/Private/Public)
3. Matikan **Microsoft Defender Firewall** (sementara)
4. Coba akses dari HP lagi

Kalau berhasil, berarti firewall yang blocking. Aktifkan lagi firewall-nya,
lalu jalankan ulang `setup_akses_hp.bat` sebagai Administrator.

### B. IP Windows berbeda

Cek IP Windows:

```bash
/mnt/c/Windows/System32/ipconfig.exe
```

Cari yang ada tulisan `Wireless LAN adapter Wi-Fi` atau `Ethernet adapter`,
lihat baris `IPv4 Address`. Gunakan IP itu untuk akses dari HP.

### C. Server mati

Pastikan terminal WSL masih jalan. Kalau server mati, ulangi **Step 1**.

---

## Step 5 (Opsional): Buat Auto-Start Server

Biar gak perlu manual start server tiap kali, buat file batch di Windows:

Buka Notepad, ketik:

```batch
@echo off
cd /d %USERPROFILE%
wsl -d Ubuntu -- cd /home/irzaip/irqhomedb && source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Simpan sebagai `start_irqhomedb.bat` di Desktop.
Tinggal double-click → server jalan otomatis.

---

## Ringkasan (1x Setup)

| Step | Perintah | Di mana? |
|------|----------|----------|
| 1 | `python -m uvicorn app.main:app --host 0.0.0.0 --port 8080` | Terminal WSL |
| 2 | `cp setup_akses_hp.bat /mnt/c/Users/` | Terminal WSL |
| 3 | Klik kanan → Run as administrator | Windows Explorer |
| 4 | Buka `http://192.168.30.50:8080` | Browser HP |

**Catatan:** Setelah Windows restart, port forward dan firewall rule bisa hilang.
Jalankan ulang **Step 3** (setup_akses_hp.bat) setelah restart Windows.
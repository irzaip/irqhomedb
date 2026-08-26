@echo off
title irqhomedb — Setup Akses dari HP
echo ============================================
echo    irqhomedb — Setup Akses dari HP
echo ============================================
echo.
echo WSL IP: 172.18.237.85
echo Windows IP: 192.168.30.50
echo.
echo FILE INI HARUS DIJALANKAN SEBAGAI ADMINISTRATOR!
echo (Klik kanan -^> Run as administrator)
echo.
pause

echo.
echo [1/3] Membuat firewall rule...
netsh advfirewall firewall add rule name="irqhomedb 8080" dir=in action=allow protocol=TCP localport=8080

echo.
echo [2/3] Setup port forwarding Windows -^> WSL...
netsh interface portproxy delete all
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=172.18.237.85

echo.
echo [3/3] Verifikasi...
netsh interface portproxy show all

echo.
echo ============================================
echo ✅ Selesai!
echo.
echo Dari HP di WiFi yang sama, buka:
echo   http://192.168.30.50:8080
echo.
echo Login: irza / admin123
echo ============================================
pause
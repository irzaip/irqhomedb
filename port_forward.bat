@echo off
echo ========== irqhomedb — Setup Port Forward ==========
echo.
echo Jalankan file ini sebagai ADMINISTRATOR!
echo (Klik kanan → Run as administrator)
echo.
pause

netsh interface portproxy delete all
netsh interface portproxy add v4tov4 listenport=8880 listenaddress=0.0.0.0 connectport=8880 connectaddress=172.18.237.85
netsh interface portproxy show all

echo.
echo ✅ Port forward selesai!
echo Dari HP buka: http://192.168.30.50:8080
pause

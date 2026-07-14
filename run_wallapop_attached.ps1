# Scrape Wallapop attaching to your running Chrome (CDP port 9222)
# Uso: .\run_wallapop_attached.ps1
#
# PASOS PREVIOS:
#   1. Cierra Chrome del todo.
#   2. Abre Chrome con el puerto de depuracion activo. En PowerShell o Ejecutar (Win+R):
#        chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome_dev"
#   3. En ese Chrome, abre una o varias de estas busquedas (ordenadas por novedades):
#        https://es.wallapop.com/search?keywords=masters+del+universo+origins&order_by=newest
#        https://es.wallapop.com/search?keywords=masters+of+the+universe+origins&order_by=newest
#        https://es.wallapop.com/search?keywords=motu+origins&order_by=newest
#   4. Ejecuta este script.

Clear-Host
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "INCURSION MANUAL ASISTIDA: WALLAPOP (CDP)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Conectando a tu ventana de Chrome en el puerto 9222..." -ForegroundColor Gray
.venv\Scripts\python scripts\scrape_wallapop_via_cdp.py

Write-Host ""
Write-Host "Proceso completado." -ForegroundColor Green

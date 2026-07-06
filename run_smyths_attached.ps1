# Scrape Smyths Toys attaching to your running Chrome
# Uso: .\run_smyths_attached.ps1

Clear-Host
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "INCURSION MANUAL ASISTIDA (CDP ATTACH)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Conectando a tu ventana de Chrome en el puerto 9222..." -ForegroundColor Gray
.venv\Scripts\python scripts\scrape_via_cdp.py

Write-Host ""
Write-Host "Proceso completado." -ForegroundColor Green

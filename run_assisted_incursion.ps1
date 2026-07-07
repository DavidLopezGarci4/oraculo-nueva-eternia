# Run Universal Assisted Scraper attaching to your running Chrome
# Uso: .\run_assisted_incursion.ps1

Clear-Host
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "INCURSION MANUAL ASISTIDA UNIVERSAL (CDP)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Conectando a tu ventana de Chrome en el puerto 9222..." -ForegroundColor Gray
.venv\Scripts\python scripts\scrape_multi_via_cdp.py

Write-Host ""
Write-Host "Proceso completado." -ForegroundColor Green

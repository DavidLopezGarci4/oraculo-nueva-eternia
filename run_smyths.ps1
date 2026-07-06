# Run Smyths Toys Scraper on Windows Host Machine
# Uso: .\run_smyths.ps1

Clear-Host
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "INCURSION MANUAL: SMYTHS TOYS (NATIVO)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Ensure we use native Windows Google Chrome
Write-Host "Iniciando scraper localmente..." -ForegroundColor Gray
.venv\Scripts\python scripts\run_single_incursion.py SmythsToys

Write-Host ""
Write-Host "Proceso completado." -ForegroundColor Green

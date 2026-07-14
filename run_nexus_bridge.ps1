# Nexus Local Bridge - Worker de Wallapop (IP Residencial)
# Uso: .\run_nexus_bridge.ps1
#
# Este worker resuelve, desde TU PC (IP residencial, no la del servidor), los
# trabajos de busqueda de Wallapop que se encolen desde el panel de Configuracion.
# Dejalo corriendo en segundo plano mientras quieras que el Oraculo pueda usar
# Wallapop sin bloqueos de CloudFront.
#
# Configuracion opcional (variables de entorno en .env):
#   ORACULO_API_BASE_URL       URL de la API del Oraculo (por defecto http://localhost:8000)
#   ORACULO_API_KEY            Clave de administracion
#   NEXUS_BRIDGE_POLL_INTERVAL Segundos entre sondeos sin trabajos pendientes (por defecto 20)

Clear-Host
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "NEXUS LOCAL BRIDGE - WALLAPOP (IP RESIDENCIAL)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Iniciando worker local..." -ForegroundColor Gray
.venv\Scripts\python scripts\nexus_local_worker.py

Write-Host ""
Write-Host "Worker detenido." -ForegroundColor Green

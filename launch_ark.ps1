
# 🚢 Launch The Ark - Docker Launcher
# Uso: .\launch_ark.ps1

Clear-Host
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚢  DESPLEGANDO EL ARCA (DOCKER)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🛑 Deteniendo contenedores antiguos..." -ForegroundColor Gray
docker-compose down

Write-Host "🚀 Iniciando motores (Build & Up)..." -ForegroundColor Yellow
Write-Host "Esto puede tardar unos minutos la primera vez mientras se descargan las imágenes." -ForegroundColor DarkGray
docker-compose up --build


# ⚔️ Launch Eternia - Nueva Eternia Unified Launcher
# Uso: .\launch_eternia.ps1

Clear-Host
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "⚔️  DESPERTANDO EL ORÁCULO DE NUEVA ETERNIA" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Limpieza de Puertos (Evita errores de 'Port in use')
Write-Host "🧹 Paso 1: Limpiando puertos 8000 y 5173/5174..." -ForegroundColor Gray
$ports = @(8000, 5173, 5174)
foreach ($port in $ports) {
    try {
        $procId = (Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue).OwningProcess
        if ($procId) {
            Stop-Process -Id $procId -Force
            Write-Host "   - Puerto $port liberado." -ForegroundColor DarkGray
        }
    }
    catch {}
}

# 2. Lanzar Backend (API Broker)
Write-Host "📡 Paso 2: Iniciando API Broker (Backend) en nueva ventana..." -ForegroundColor Yellow
$BackendCmd = "`$Host.UI.RawUI.WindowTitle = 'ORACULO - BACKEND (API)'; `$env:PYTHONPATH='.'; python src/interfaces/api/main.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $BackendCmd -WorkingDirectory $PSScriptRoot

# 3. Lanzar Frontend (Vite)
Write-Host "🎨 Paso 3: Iniciando Tablero React (Frontend) en nueva ventana..." -ForegroundColor Green
$FrontendCmd = "`$Host.UI.RawUI.WindowTitle = 'ORACULO - FRONTEND (UX)'; Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; cd frontend; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $FrontendCmd -WorkingDirectory $PSScriptRoot

Write-Host ""
Write-Host "🚀 ¡TODO EN MARCHA!" -ForegroundColor Cyan
Write-Host "El backend está en http://localhost:8000" -ForegroundColor Gray
Write-Host "El frontend estará disponible en http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "Puedes cerrar esta ventana, las otras dos seguirán corriendo." -ForegroundColor White

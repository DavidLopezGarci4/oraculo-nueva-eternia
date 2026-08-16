# ===================================================================
# EL ORACULO DE NUEVA ETERNIA - CENTRO DE CONTROL UNIFICADO
# ===================================================================
# Uso: .\oraculo.ps1

function Show-Header {
    Clear-Host
    Write-Host "===================================================================" -ForegroundColor Cyan
    Write-Host "      *  EL ORACULO DE NUEVA ETERNIA - CENTRO DE CONTROL  *        " -ForegroundColor Yellow
    Write-Host "===================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Invoke-LocalStart {
    Show-Header
    Write-Host "[1] INICIANDO ORACULO EN LOCAL (NATIVO)..." -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Paso 1: Liberando puertos (8000, 3001, 5173, 5174)..." -ForegroundColor Gray
    $ports = @(8000, 3001, 5173, 5174)
    foreach ($port in $ports) {
        try {
            $procId = (Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue).OwningProcess
            if ($procId) {
                Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
                Write-Host "   - Puerto $port liberado." -ForegroundColor DarkGray
            }
        } catch {}
    }

    Write-Host "Paso 2: Iniciando Backend FastAPI (http://localhost:8000)..." -ForegroundColor Yellow
    $BackendCmd = "`$Host.UI.RawUI.WindowTitle = 'ORACULO - BACKEND (API)'; Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .venv\Scripts\python -m src.interfaces.api.main"
    Start-Process powershell -ArgumentList "-ExecutionPolicy", "Bypass", "-NoExit", "-Command", $BackendCmd -WorkingDirectory $PSScriptRoot

    Write-Host "Paso 3: Iniciando Frontend React/Vite (http://localhost:3001)..." -ForegroundColor Green
    $FrontendCmd = "`$Host.UI.RawUI.WindowTitle = 'ORACULO - FRONTEND (UX)'; Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; cd frontend; npm run dev"
    Start-Process powershell -ArgumentList "-ExecutionPolicy", "Bypass", "-NoExit", "-Command", $FrontendCmd -WorkingDirectory $PSScriptRoot

    Write-Host ""
    Write-Host "Backend y Frontend iniciados en ventanas independientes." -ForegroundColor Cyan
    Write-Host "API Swagger: http://localhost:8000/docs" -ForegroundColor DarkGray
    Write-Host "Web App:     http://localhost:3001" -ForegroundColor DarkGray
    Write-Host ""
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

function Invoke-DockerStart {
    Show-Header
    Write-Host "[2] INICIANDO ORACULO EN DOCKER (THE ARK)..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Deteniendo contenedores previos..." -ForegroundColor Gray
    docker-compose down
    Write-Host "Construyendo y levantando contenedores..." -ForegroundColor Yellow
    docker-compose up --build -d
    Write-Host ""
    Write-Host "Contenedores iniciados en segundo plano." -ForegroundColor Green
    Write-Host "Web App Docker: http://localhost:3001 o http://localhost" -ForegroundColor DarkGray
    Write-Host ""
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

function Invoke-NexusBridge {
    Show-Header
    Write-Host "[3] INICIANDO NEXUS LOCAL BRIDGE (IP RESIDENCIAL)..." -ForegroundColor Yellow
    Write-Host "Este worker procesa busquedas de Wallapop desde tu IP de casa." -ForegroundColor Gray
    Write-Host "Puedes encolar busquedas enviando /nexus desde Telegram." -ForegroundColor Cyan
    Write-Host "Para detener el worker en cualquier momento, presiona Ctrl + C." -ForegroundColor DarkGray
    Write-Host ""
    
    $PythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    if (!(Test-Path $PythonExe)) { $PythonExe = "python" }
    
    & $PythonExe scripts\nexus_local_worker.py
    
    Write-Host ""
    Write-Host "Worker detenido." -ForegroundColor Green
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

function Invoke-BackupDb {
    Show-Header
    Write-Host "[4] REALIZANDO COPIA DE SEGURIDAD INMEDIATA..." -ForegroundColor Green
    Write-Host ""
    
    $BackupScript = Join-Path $PSScriptRoot "backup_db.ps1"
    if (Test-Path $BackupScript) {
        & $BackupScript
    } else {
        Write-Host "No se encontro backup_db.ps1." -ForegroundColor Red
    }

    Write-Host ""
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

function Invoke-ChromeDebug {
    Show-Header
    Write-Host "[5] ABRIENDO GOOGLE CHROME EN MODO DEPURACION (PUERTO 9222)..." -ForegroundColor Cyan
    Write-Host ""
    
    $CommonPaths = @(
        "C:\Program Files\Google\Chrome\Application\chrome.exe",
        "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
    )

    $ChromePath = $null
    foreach ($Path in $CommonPaths) {
        if (Test-Path $Path) {
            $ChromePath = $Path
            break
        }
    }

    if ($null -eq $ChromePath) {
        Write-Host "No se encontro google chrome.exe en las rutas habituales." -ForegroundColor Red
        Read-Host "Presiona [Enter] para volver..."
        return
    }

    $UserDataDir = Join-Path $PSScriptRoot "scratch\chrome_dev"
    if (!(Test-Path $UserDataDir)) {
        New-Item -ItemType Directory -Path $UserDataDir -Force | Out-Null
    }

    $ArgList = @(
        "--remote-debugging-port=9222",
        "--user-data-dir=$UserDataDir",
        "--disable-blink-features=AutomationControlled",
        "--no-first-run",
        "--no-default-browser-check",
        "--start-maximized"
    )

    Start-Process -FilePath $ChromePath -ArgumentList $ArgList
    Write-Host "Chrome abierto en puerto 9222 con perfil aislado." -ForegroundColor Green
    Write-Host "Ahora puedes navegar a cualquier tienda (Wallapop, Vinted, Smyths) y luego usar la opcion [6] para extraer las ofertas." -ForegroundColor Gray
    Write-Host ""
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

function Invoke-AssistedIncursion {
    Show-Header
    Write-Host "[6] EJECUTANDO INCURSION ASISTIDA UNIVERSAL (CDP)..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Conectando al Chrome abierto en el puerto 9222..." -ForegroundColor Gray
    
    $PythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    if (!(Test-Path $PythonExe)) { $PythonExe = "python" }

    & $PythonExe scripts\scrape_multi_via_cdp.py
    
    Write-Host ""
    Write-Host "Incursion finalizada." -ForegroundColor Green
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

function Invoke-RunTests {
    Show-Header
    Write-Host "[7] EJECUTANDO SUITE COMPLETA DE PRUEBAS Y DIAGNOSTICO..." -ForegroundColor Magenta
    Write-Host ""
    
    $PythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    if (!(Test-Path $PythonExe)) { $PythonExe = "python" }

    & $PythonExe -m pytest tests/ -v
    
    Write-Host ""
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

function Invoke-CreateShortcuts {
    Show-Header
    Write-Host "[8] CREANDO ACCESOS DIRECTOS EN EL ESCRITORIO..." -ForegroundColor Yellow
    Write-Host ""
    
    $WScriptShell = New-Object -ComObject WScript.Shell
    $DesktopPath = [Environment]::GetFolderPath("Desktop")

    $MasterShortcut = Join-Path $DesktopPath "Oraculo - Centro de Control.lnk"
    $TargetScript = Join-Path $PSScriptRoot "oraculo.ps1"
    $s1 = $WScriptShell.CreateShortcut($MasterShortcut)
    $s1.TargetPath = "powershell.exe"
    $s1.Arguments = "-ExecutionPolicy Bypass -NoExit -File `"$TargetScript`""
    $s1.WorkingDirectory = $PSScriptRoot
    $s1.Description = "Centro de Control Unificado del Oraculo de Nueva Eternia"
    $s1.IconLocation = "shell32.dll,220"
    $s1.Save()
    Write-Host "Acceso directo creado: 'Oraculo - Centro de Control.lnk'" -ForegroundColor Green

    $BackupShortcut = Join-Path $DesktopPath "Oraculo - Guardian de Backups.lnk"
    $BackupTarget = Join-Path $PSScriptRoot "backup_db.ps1"
    $s2 = $WScriptShell.CreateShortcut($BackupShortcut)
    $s2.TargetPath = "powershell.exe"
    $s2.Arguments = "-ExecutionPolicy Bypass -NoExit -File `"$BackupTarget`""
    $s2.WorkingDirectory = $PSScriptRoot
    $s2.Description = "Crear Copia de Seguridad Inmediata de oraculo.db"
    $s2.IconLocation = "shell32.dll,44"
    $s2.Save()
    Write-Host "Acceso directo creado: 'Oraculo - Guardian de Backups.lnk'" -ForegroundColor Green

    Write-Host ""
    Write-Host "Accesos directos listos en tu Escritorio de Windows." -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

function Invoke-DeployCloud {
    Show-Header
    Write-Host "[9] DESPLEGANDO Y ACTUALIZANDO EN ORACLE CLOUD..." -ForegroundColor Cyan
    Write-Host ""
    
    $KeyPath = "C:\Users\dace8\OneDrive\Documentos\nueva-eternia-produccion.key"
    $Server = "opc@79.72.50.244"
    
    if (!(Test-Path $KeyPath)) {
        Write-Host "No se encontro la clave en: $KeyPath" -ForegroundColor Yellow
        $KeyPath = Read-Host "Introduce la ruta completa a tu clave .key"
    }

    Write-Host "Conectando a Oracle Cloud y ejecutando actualizacion..." -ForegroundColor Yellow
    $RemoteCmd = "cd ~/oraculo-nueva-eternia && git reset --hard origin/main && git pull origin main && sudo docker compose -f docker-compose.prod.yml up -d --build"
    
    ssh -i "$KeyPath" "$Server" "$RemoteCmd"
    
    Write-Host ""
    Write-Host "Proceso de despliegue en la nube finalizado." -ForegroundColor Green
    Write-Host "Comprobar web en: https://oraculo-eternia.duckdns.org" -ForegroundColor DarkGray
    Write-Host ""
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

function Invoke-SshConnect {
    Show-Header
    Write-Host "[10] CONECTANDO POR SSH A ORACLE CLOUD..." -ForegroundColor Cyan
    Write-Host ""
    
    $KeyPath = "C:\Users\dace8\OneDrive\Documentos\nueva-eternia-produccion.key"
    $Server = "opc@79.72.50.244"

    if (!(Test-Path $KeyPath)) {
        Write-Host "No se encontro la clave en: $KeyPath" -ForegroundColor Yellow
        $KeyPath = Read-Host "Introduce la ruta completa a tu clave .key"
    }

    Write-Host "Iniciando terminal interactiva en el servidor..." -ForegroundColor Gray
    ssh -i "$KeyPath" "$Server"
    
    Write-Host ""
    Write-Host "Sesion SSH cerrada." -ForegroundColor Green
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

function Invoke-RenewSslCloud {
    Show-Header
    Write-Host "[11] RENOVANDO CERTIFICADOS SSL EN ORACLE CLOUD..." -ForegroundColor Cyan
    Write-Host ""
    
    $KeyPath = "C:\Users\dace8\OneDrive\Documentos\nueva-eternia-produccion.key"
    $Server = "opc@79.72.50.244"

    if (!(Test-Path $KeyPath)) {
        Write-Host "No se encontro la clave en: $KeyPath" -ForegroundColor Yellow
        $KeyPath = Read-Host "Introduce la ruta completa a tu clave .key"
    }

    Write-Host "Conectando al servidor y ejecutando renovacion SSL..." -ForegroundColor Yellow
    $RemoteCmd = "cd ~/oraculo-nueva-eternia && sudo docker run --rm -v \$(pwd)/certbot/conf:/etc/letsencrypt -v \$(pwd)/certbot/www:/var/www/certbot certbot/certbot renew && sudo docker compose -f docker-compose.prod.yml restart frontend"
    
    ssh -i "$KeyPath" "$Server" "$RemoteCmd"
    
    Write-Host ""
    Write-Host "Proceso de renovacion SSL completado." -ForegroundColor Green
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

do {
    Show-Header
    Write-Host "  [1]  Iniciar Oraculo en Local (Backend + Frontend Nativo)" -ForegroundColor White
    Write-Host "  [2]  Iniciar Oraculo en Docker (The Ark Stack)" -ForegroundColor White
    Write-Host "  [3]  Iniciar Nexus Local Bridge (Worker Residencial Wallapop)" -ForegroundColor White
    Write-Host "  [4]  Realizar Copia de Seguridad Inmediata (DB Backup)" -ForegroundColor White
    Write-Host "  [5]  Abrir Google Chrome en Depuracion (Puerto 9222)" -ForegroundColor White
    Write-Host "  [6]  Incursion Asistida Universal (CDP Multi-tienda)" -ForegroundColor White
    Write-Host "  [7]  Ejecutar Suite Completa de Tests y Diagnostico" -ForegroundColor White
    Write-Host "  [8]  Crear / Actualizar Accesos Directos en el Escritorio" -ForegroundColor White
    Write-Host "  [9]  Desplegar y Actualizar en Oracle Cloud (1 Clic)" -ForegroundColor Cyan
    Write-Host "  [10] Conectar por SSH al Servidor en la Nube" -ForegroundColor Cyan
    Write-Host "  [11] Renovar Certificados SSL en Oracle Cloud" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [0]  Salir" -ForegroundColor Red
    Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
    $choice = Read-Host "  Selecciona una opcion [0-11]"

    switch ($choice.Trim()) {
        "1" { Invoke-LocalStart }
        "2" { Invoke-DockerStart }
        "3" { Invoke-NexusBridge }
        "4" { Invoke-BackupDb }
        "5" { Invoke-ChromeDebug }
        "6" { Invoke-AssistedIncursion }
        "7" { Invoke-RunTests }
        "8" { Invoke-CreateShortcuts }
        "9" { Invoke-DeployCloud }
        "10" { Invoke-SshConnect }
        "11" { Invoke-RenewSslCloud }
        "0" { 
            Clear-Host
            Write-Host "Hasta la proxima, Guardian de Nueva Eternia!" -ForegroundColor Cyan
            exit 
        }
        Default {
            Write-Host "Opcion no valida. Intentalo de nuevo." -ForegroundColor Yellow
            Start-Sleep -Seconds 1
        }
    }
} while ($true)

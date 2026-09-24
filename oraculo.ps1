param (
    [switch]$Backup
)
# Forzar codificacion UTF-8 en consola y tuberias
try {
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}


# ===================================================================
# EL ORACULO DE NUEVA ETERNIA - CENTRO DE CONTROL UNIFICADO
# ===================================================================
# Uso: .\oraculo.ps1

function Get-PythonExe {
    $venvPy = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    if (Test-Path $venvPy) { return $venvPy }
    return "python"
}

function Show-Header {
    Clear-Host
    Write-Host "===================================================================" -ForegroundColor Cyan
    Write-Host "      *  EL ORACULO DE NUEVA ETERNIA - CENTRO DE CONTROL  *        " -ForegroundColor Yellow
    Write-Host "===================================================================" -ForegroundColor Cyan
    Write-Host ""
}

# -------------------------------------------------------------------
# [1] INICIAR ORACULO EN LOCAL
# -------------------------------------------------------------------
function Invoke-LocalStart {
    Show-Header
    Write-Host "[1] INICIANDO ORACULO EN LOCAL (NATIVO)..." -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Paso 1: Liberando puertos de desarrollo (8000, 3001, 5173, 5174)..." -ForegroundColor Gray
    $ports = @(8000, 3001, 5173, 5174)
    foreach ($port in $ports) {
        try {
            $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
            foreach ($conn in $connections) {
                if ($conn.OwningProcess) {
                    Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
                    Write-Host "   - Puerto $port liberado (PID $($conn.OwningProcess))." -ForegroundColor DarkGray
                }
            }
        } catch {}
    }

    $PythonExe = Get-PythonExe
    Write-Host "Paso 2: Iniciando Backend FastAPI (http://localhost:8000)..." -ForegroundColor Yellow
    $BackendCmd = "`$Host.UI.RawUI.WindowTitle = 'ORACULO - BACKEND (API)'; Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; `"$PythonExe`" -m src.interfaces.api.main"
    Start-Process powershell -ArgumentList "-ExecutionPolicy", "Bypass", "-NoExit", "-Command", $BackendCmd -WorkingDirectory $PSScriptRoot

    Write-Host "Paso 3: Iniciando Frontend React/Vite (http://localhost:3001)..." -ForegroundColor Green
    $FrontendCmd = "`$Host.UI.RawUI.WindowTitle = 'ORACULO - FRONTEND (UX)'; Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; cd frontend; npm run dev"
    Start-Process powershell -ArgumentList "-ExecutionPolicy", "Bypass", "-NoExit", "-Command", $FrontendCmd -WorkingDirectory $PSScriptRoot

    Write-Host ""
    Write-Host "Backend y Frontend iniciados en ventanas independientes." -ForegroundColor Cyan
    Write-Host "  -> API Swagger: http://localhost:8000/docs" -ForegroundColor DarkGray
    Write-Host "  -> Web App:     http://localhost:3001" -ForegroundColor DarkGray
    Write-Host ""
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

# -------------------------------------------------------------------
# [2] INICIAR EN DOCKER
# -------------------------------------------------------------------
function Invoke-DockerStart {
    Show-Header
    Write-Host "[2] INICIANDO ORACULO EN DOCKER (THE ARK STACK)..." -ForegroundColor Cyan
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

# -------------------------------------------------------------------
# [3] SUITE DE TESTS
# -------------------------------------------------------------------
function Invoke-RunTests {
    Show-Header
    Write-Host "[3] EJECUTANDO SUITE COMPLETA DE PRUEBAS Y DIAGNOSTICO..." -ForegroundColor Magenta
    Write-Host ""
    
    $PythonExe = Get-PythonExe
    & $PythonExe -m pytest tests/ -v
    
    Write-Host ""
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

# -------------------------------------------------------------------
# [4] NEXUS LOCAL BRIDGE (RESIDENCIAL)
# -------------------------------------------------------------------
function Invoke-NexusBridge {
    Show-Header
    Write-Host "[4] INICIANDO NEXUS LOCAL BRIDGE (IP RESIDENCIAL)..." -ForegroundColor Yellow
    Write-Host "Este worker procesa busquedas de Wallapop desde tu IP de casa." -ForegroundColor Gray
    Write-Host "Puedes encolar busquedas enviando /nexus desde Telegram o desde la Web." -ForegroundColor Cyan
    Write-Host "Para detener el worker en cualquier momento, presiona Ctrl + C." -ForegroundColor DarkGray
    Write-Host ""
    
    $PythonExe = Get-PythonExe
    & $PythonExe scripts\nexus_local_worker.py
    
    Write-Host ""
    Write-Host "Worker detenido." -ForegroundColor Green
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

# -------------------------------------------------------------------
# [5] CHROME DEPURACION
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# [6] INCURSION ASISTIDA UNIVERSAL (CDP)
# -------------------------------------------------------------------
function Invoke-AssistedIncursion {
    Show-Header
    Write-Host "[6] EJECUTANDO INCURSION ASISTIDA UNIVERSAL (CDP)..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Conectando al Chrome abierto en el puerto 9222..." -ForegroundColor Gray
    
    $PythonExe = Get-PythonExe
    & $PythonExe scripts\scrape_multi_via_cdp.py
    
    Write-Host ""
    Write-Host "Incursion finalizada." -ForegroundColor Green
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

# -------------------------------------------------------------------
# [7] INCURSION DIRECTA MULTI-TIENDA
# -------------------------------------------------------------------
function Invoke-MultiIncursion {
    Show-Header
    Write-Host "[7] INCURSION DIRECTA MULTI-TIENDA (IP RESIDENCIAL)..." -ForegroundColor Yellow
    Write-Host "Extrae figuras, actualiza precios y alimenta el Purgatorio sin abrir el navegador manual." -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [1] Smyths Toys (Alemania - Catalogo MOTU completo)" -ForegroundColor White
    Write-Host "  [2] Wallapop (Busqueda local residencial)" -ForegroundColor White
    Write-Host "  [3] Vinted (Ofertas de segunda mano Europa)" -ForegroundColor White
    Write-Host "  [4] eBay (Solo moderno/Origins - Vintage inhabilitado)" -ForegroundColor White
    Write-Host "  [5] Amazon (Stock y precios retail)" -ForegroundColor White
    Write-Host "  [6] BigBadToyStore (BBTS - Importacion USA)" -ForegroundColor White
    Write-Host "  [x] Cancelar y volver" -ForegroundColor DarkGray
    Write-Host ""
    $shopOpt = Read-Host "Selecciona tienda [1-6]"

    $shopMap = @{
        "1" = "SmythsToys"
        "2" = "Wallapop"
        "3" = "Vinted"
        "4" = "Ebay"
        "5" = "Amazon"
        "6" = "BBTS"
    }

    if (!$shopMap.ContainsKey($shopOpt)) {
        Write-Host "Operacion cancelada." -ForegroundColor DarkGray
        Start-Sleep -Seconds 1
        return
    }

    $shopName = $shopMap[$shopOpt]
    $query = Read-Host "Introduce termino de busqueda (deja vacio para 'auto')"
    if ([string]::IsNullOrWhiteSpace($query)) { $query = "auto" }

    Write-Host ""
    Write-Host "Ejecutando incursion en $shopName para: '$query'..." -ForegroundColor Cyan
    $PythonExe = Get-PythonExe
    & $PythonExe scripts\run_single_incursion.py $shopName $query

    Write-Host ""
    Write-Host "Incursion de $shopName completada." -ForegroundColor Green
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

# -------------------------------------------------------------------
# [8] DESPLEGAR EN ORACLE CLOUD
# -------------------------------------------------------------------
function Invoke-DeployCloud {
    Show-Header
    Write-Host "[8] DESPLEGANDO Y ACTUALIZANDO EN ORACLE CLOUD..." -ForegroundColor Cyan
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

# -------------------------------------------------------------------
# [9] CONECTAR POR SSH A ORACLE CLOUD
# -------------------------------------------------------------------
function Invoke-SshConnect {
    Show-Header
    Write-Host "[9] CONECTANDO POR SSH A ORACLE CLOUD..." -ForegroundColor Cyan
    Write-Host ""
    
    $KeyPath = "C:\Users\dace8\OneDrive\Documentos\nueva-eternia-produccion.key"
    $Server = "opc@79.72.50.244"

    if (!(Test-Path $KeyPath)) {
        Write-Host "No se encontro la clave en: $KeyPath" -ForegroundColor Yellow
        $KeyPath = Read-Host "Introduce la ruta completa a tu clave .key"
    }

    Write-Host "Iniciando terminal interactiva en el servidor (escribe 'exit' para salir)..." -ForegroundColor Gray
    ssh -i "$KeyPath" "$Server"
    
    Write-Host ""
    Write-Host "Sesion SSH cerrada." -ForegroundColor Green
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

# -------------------------------------------------------------------
# [10] RENOVAR SSL EN ORACLE CLOUD
# -------------------------------------------------------------------
function Invoke-RenewSslCloud {
    Show-Header
    Write-Host "[10] RENOVANDO CERTIFICADOS SSL EN ORACLE CLOUD..." -ForegroundColor Cyan
    Write-Host ""
    
    $KeyPath = "C:\Users\dace8\OneDrive\Documentos\nueva-eternia-produccion.key"
    $Server = "opc@79.72.50.244"

    if (!(Test-Path $KeyPath)) {
        Write-Host "No se encontro la clave en: $KeyPath" -ForegroundColor Yellow
        $KeyPath = Read-Host "Introduce la ruta completa a tu clave .key"
    }

    Write-Host "Conectando al servidor y ejecutando renovacion SSL..." -ForegroundColor Yellow
    $RemoteCmd = "cd ~/oraculo-nueva-eternia && bash scripts/renew_ssl.sh --force"
    
    ssh -i "$KeyPath" "$Server" "$RemoteCmd"
    
    Write-Host ""
    Write-Host "Proceso de renovacion SSL completado." -ForegroundColor Green
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

# -------------------------------------------------------------------
# [11] BACKUP DUAL COMPLETO (SQLITE + SUPABASE)
# -------------------------------------------------------------------
function Invoke-BackupDual {
    Show-Header
    Write-Host "[11] REALIZANDO COPIA DE SEGURIDAD DUAL (SQLITE + SUPABASE)..." -ForegroundColor Green
    Write-Host ""
    
    $BackupDir = Join-Path $PSScriptRoot "backups"
    if (!(Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir | Out-Null
    }

    $Timestamp = Get-Date -Format "yyyyMMdd_HHmm"
    $SourceDB = Join-Path $PSScriptRoot "oraculo.db"
    $DestDB = Join-Path $BackupDir "oraculo_$Timestamp.db"
    $PythonExe = Get-PythonExe

    # 1. Backup Local SQLite
    Write-Host "Paso 1: Respaldando base de datos local SQLite (oraculo.db)..." -ForegroundColor Yellow
    if (Test-Path $SourceDB) {
        $pyBackupLocal = @'
import sys, sqlite3
src_path = sys.argv[1]
dst_path = sys.argv[2]
src = sqlite3.connect(src_path)
dst = sqlite3.connect(dst_path)
src.backup(dst)
dst.close()
src.close()
'@
        & $PythonExe -c $pyBackupLocal "$SourceDB" "$DestDB"

        if ($LASTEXITCODE -eq 0 -and (Test-Path $DestDB)) {
            Write-Host "   -> Backup local creado con exito: oraculo_$Timestamp.db" -ForegroundColor Green
            
            # Limpieza: Mantener solo los ultimos 10 backups de oraculo.db
            $Backups = Get-ChildItem $BackupDir -File -Filter "oraculo_*.db" | Sort-Object LastWriteTime -Descending
            if ($Backups.Count -gt 10) {
                $Backups[10..($Backups.Count - 1)] | Remove-Item -Force
                Write-Host "   -> Backups locales antiguos eliminados (mantenemos los 10 mas recientes)." -ForegroundColor Gray
            }
        } else {
            Write-Host "   -> Error: el backup local via sqlite3.backup() fallo." -ForegroundColor Red
        }
    } else {
        Write-Host "   -> Advertencia: No se encontro oraculo.db en la raiz." -ForegroundColor Yellow
    }

    # 2. Backup Cloud Supabase
    Write-Host ""
    $doCloud = "S"
    if (!$Backup) {
        $doCloud = Read-Host "¿Deseas descargar tambien un snapshot completo de Supabase Cloud? [S/n]"
    }

    if ([string]::IsNullOrWhiteSpace($doCloud) -or $doCloud.ToUpper() -eq "S") {
        Write-Host "Paso 2: Descargando snapshot de Supabase Cloud..." -ForegroundColor Yellow
        $CloudBackupFile = Join-Path $BackupDir "supabase_$Timestamp.db"
        $pyBackupCloud = @'
import sys, os
from pathlib import Path
root_dir = Path(sys.argv[1])
sys.path.append(str(root_dir))
dest_file = sys.argv[2]
from src.core.config import settings
from scripts.backup_supabase import backup_cloud_data

if settings.SUPABASE_DATABASE_URL and "sqlite" not in settings.SUPABASE_DATABASE_URL:
    backup_cloud_data(settings.SUPABASE_DATABASE_URL, dest_file)
    print("   -> Snapshot de Supabase descargado correctamente.")
else:
    print("   -> No se detecto SUPABASE_DATABASE_URL valida o configurada.")
'@
        & $PythonExe -c $pyBackupCloud "$PSScriptRoot" "$CloudBackupFile"

        # Mantener solo los 5 backups mas recientes de Supabase
        $CloudBackups = Get-ChildItem $BackupDir -File -Filter "supabase_*.db" | Sort-Object LastWriteTime -Descending
        if ($CloudBackups.Count -gt 5) {
            $CloudBackups[5..($CloudBackups.Count - 1)] | Remove-Item -Force
            Write-Host "   -> Snapshots antiguos de Supabase eliminados (mantenemos los 5 mas recientes)." -ForegroundColor Gray
        }
    }

    Write-Host ""
    Write-Host "Proceso de copia de seguridad finalizado." -ForegroundColor Green
    if (!$Backup) {
        Read-Host "Presiona [Enter] para volver al menu principal..."
    }
}

# -------------------------------------------------------------------
# [12] DIAGNOSTICO DE PARIDAD Y SALUD
# -------------------------------------------------------------------
function Invoke-DiagnosticDb {
    Show-Header
    Write-Host "[12] DIAGNOSTICO DE PARIDAD Y SALUD DUAL (SQLITE vs SUPABASE)..." -ForegroundColor Cyan
    Write-Host ""
    
    $PythonExe = Get-PythonExe
    $pyDiag = @'
import sys, os, sqlite3
from pathlib import Path
root_dir = Path(sys.argv[1])
sys.path.append(str(root_dir))
from src.core.config import settings
from sqlalchemy import create_engine, text

print("+" + "-"*65 + "+")
print("|  METRICA DE DATOS       |  SQLITE LOCAL   |  SUPABASE CLOUD  |")
print("+" + "-"*65 + "+")

loc_prods, loc_origins, loc_offers, loc_lore = 0, 0, 0, 0
db_path = "oraculo.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM products")
        loc_prods = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM products WHERE is_vintage = 0 OR is_vintage IS NULL")
        loc_origins = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM offers")
        loc_offers = cur.fetchone()[0]
    except Exception: pass
    try:
        cur.execute("SELECT COUNT(*) FROM character_lore")
        loc_lore = cur.fetchone()[0]
    except Exception: pass
    conn.close()

cld_prods, cld_origins, cld_offers, cld_lore = 0, 0, 0, 0
cld_status = "Desconectado"
if settings.SUPABASE_DATABASE_URL and "sqlite" not in settings.SUPABASE_DATABASE_URL:
    try:
        engine = create_engine(settings.SUPABASE_DATABASE_URL)
        with engine.connect() as conn:
            res = conn.execute(text("SELECT COUNT(*) FROM products"))
            cld_prods = res.scalar() or 0
            res = conn.execute(text("SELECT COUNT(*) FROM products WHERE is_vintage = false OR is_vintage IS NULL"))
            cld_origins = res.scalar() or 0
            res = conn.execute(text("SELECT COUNT(*) FROM offers"))
            cld_offers = res.scalar() or 0
            try:
                res = conn.execute(text("SELECT COUNT(*) FROM character_lore"))
                cld_lore = res.scalar() or 0
            except Exception: pass
            cld_status = "Conectado (OK)"
    except Exception as e:
        cld_status = f"Error ({str(e)[:15]})"
else:
    cld_status = "No Configurado"

print(f"|  Productos Totales      |  {loc_prods:<14} |  {cld_prods:<15} |")
print(f"|  Figuras Origins        |  {loc_origins:<14} |  {cld_origins:<15} |")
print(f"|  Ofertas (Purgatorio)   |  {loc_offers:<14} |  {cld_offers:<15} |")
print(f"|  Perfiles Grimorio Lore |  {loc_lore:<14} |  {cld_lore:<15} |")
print("+" + "-"*65 + "+")
print(f"Estado Supabase: {cld_status}")
if loc_prods == cld_prods and loc_origins == cld_origins and loc_lore == cld_lore and loc_prods > 0:
    print("Estado de Paridad: EXCELENTE (Paridad Dual 100% Identica)")
else:
    print("Estado de Paridad: DISCREPANCIAS DETECTADAS (Usa [13] o [14] para sincronizar)")
'@
    & $PythonExe -c $pyDiag "$PSScriptRoot"

    Write-Host ""
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

# -------------------------------------------------------------------
# [13] MIGRACION UNIVERSAL DE ESQUEMAS DUALES
# -------------------------------------------------------------------
function Invoke-UniversalMigrator {
    Show-Header
    Write-Host "[13] SINCRONIZANDO ESQUEMAS DE BASE DE DATOS (UNIVERSAL MIGRATOR)..." -ForegroundColor Yellow
    Write-Host "Verifica y añade tablas y columnas faltantes tanto en SQLite como en Supabase." -ForegroundColor Gray
    Write-Host ""
    
    $PythonExe = Get-PythonExe
    & $PythonExe -m src.infrastructure.universal_migrator
    
    Write-Host ""
    Write-Host "Sincronizacion de esquemas finalizada." -ForegroundColor Green
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

# -------------------------------------------------------------------
# [14] SEMBRAR GRIMORIO LORE CANONICO (ORIGINS DUAL)
# -------------------------------------------------------------------
function Invoke-SeedCanonicalLore {
    Show-Header
    Write-Host "[14] SEMBRAR / SINCRONIZAR GRIMORIO LORE CANONICO (ORIGINS DUAL)..." -ForegroundColor Green
    Write-Host "Puebla los 54 perfiles arquetipicos y las 338+ figuras Origins en español con paridad dual." -ForegroundColor Gray
    Write-Host "Regla Estricta: Aplica unicamente a la coleccion Origins (excluye Vintage)." -ForegroundColor DarkCyan
    Write-Host ""
    
    $forceChoice = Read-Host "¿Deseas forzar la sobreescritura de textos no verificados? [s/N]"
    $isForce = if ($forceChoice.ToUpper() -eq "S") { "True" } else { "False" }

    $PythonExe = Get-PythonExe
    $pySeed = @'
import sys, os
from pathlib import Path
root_dir = Path(sys.argv[1])
sys.path.append(str(root_dir))
force = (sys.argv[2] == "True")

from src.infrastructure.database import SessionLocal
from src.infrastructure.database_cloud import SessionCloud, engine_cloud
from src.application.services.product_lore_seed import ProductLoreSeedService

print("1. Sembrando en Base de Datos Local SQLite...")
with SessionLocal() as db_loc:
    c_loc = ProductLoreSeedService.seed_canonical_characters(db_loc, force=force)
    p_loc = ProductLoreSeedService.seed_origins_products(db_loc, force=force)
    print(f"   -> SQLite: {c_loc['total_characters']} personajes y {p_loc['total_origins']} figuras Origins listas.")

if engine_cloud and "sqlite" not in str(engine_cloud.url):
    print("\n2. Sembrando en Base de Datos Supabase Cloud (PostgreSQL)...")
    try:
        with SessionCloud() as db_cld:
            c_cld = ProductLoreSeedService.seed_canonical_characters(db_cld, force=force)
            p_cld = ProductLoreSeedService.seed_origins_products(db_cld, force=force)
            print(f"   -> Supabase: {c_cld['total_characters']} personajes y {p_cld['total_origins']} figuras Origins listas.")
    except Exception as e:
        print(f"   -> Error sincronizando en Supabase: {e}")
else:
    print("\n2. Supabase Cloud no configurado o es SQLite. Omitiendo.")

print("\nSincronizacion del Grimorio Lore completada con exito.")
'@
    & $PythonExe -c $pySeed "$PSScriptRoot" "$isForce"

    Write-Host ""
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

# -------------------------------------------------------------------
# [15] REFRESCAR IMAGEN DESDE ACTIONFIGURE411 (DUAL)
# -------------------------------------------------------------------
function Invoke-RefreshFigureImage {
    Show-Header
    Write-Host "[15] ACTUALIZAR IMAGEN DESDE ACTIONFIGURE411 (DUAL)..." -ForegroundColor Magenta
    Write-Host "Descarga la imagen actualizada en alta resolucion y sincroniza en Storage, SQLite y Supabase." -ForegroundColor Gray
    Write-Host ""
    
    $FigureId = Read-Host "Introduce el ID de figura o producto (ej. 14038 para Skeletor Movie)"
    if ([string]::IsNullOrWhiteSpace($FigureId)) {
        Write-Host "ID no valido. Operacion cancelada." -ForegroundColor Yellow
        Start-Sleep -Seconds 1
        return
    }

    $PythonExe = Get-PythonExe
    $pyImage = @'
import sys, os
from pathlib import Path
root_dir = Path(sys.argv[1])
sys.path.append(str(root_dir))
fig_id = sys.argv[2]

from src.infrastructure.database import SessionLocal
from src.infrastructure.database_cloud import SessionCloud, engine_cloud
from src.application.services.catalog_refresh_service import CatalogRefreshService

print("1. Actualizando en SQLite Local...")
with SessionLocal() as db_loc:
    res_loc = CatalogRefreshService.refresh_figure_image(db_loc, fig_id)
    print("   -> Resultado SQLite:", res_loc)

if engine_cloud and "sqlite" not in str(engine_cloud.url):
    print("\n2. Actualizando en Supabase Cloud...")
    try:
        with SessionCloud() as db_cld:
            res_cld = CatalogRefreshService.refresh_figure_image(db_cld, fig_id)
            print("   -> Resultado Supabase:", res_cld)
    except Exception as e:
        print("   -> Error en Supabase:", e)
'@
    & $PythonExe -c $pyImage "$PSScriptRoot" "$FigureId"

    Write-Host ""
    Read-Host "Presiona [Enter] para volver al menu principal..."
}

# -------------------------------------------------------------------
# [16] MENU FAQ Y GUIA DE USO
# -------------------------------------------------------------------
function Show-OptionFaqDetail {
    param (
        [string]$optNum
    )
    Clear-Host
    Write-Host "===================================================================" -ForegroundColor Cyan
    Write-Host "               GUIA DETALLADA DE LA OPCION [$optNum]               " -ForegroundColor Yellow
    Write-Host "===================================================================" -ForegroundColor Cyan
    Write-Host ""

    switch ($optNum) {
        "1" {
            Write-Host "OPCION [1]: Iniciar Oraculo en Local (Backend API + Frontend Nativo)" -ForegroundColor Green
            Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "QUE HACE:" -ForegroundColor Yellow
            Write-Host "   Mata cualquier proceso zombie en puertos 8000, 3001, 5173 y 5174."
            Write-Host "   Arranca FastAPI (http://localhost:8000) y Vite (http://localhost:3001)"
            Write-Host "   en dos ventanas de PowerShell independientes."
            Write-Host ""
            Write-Host "UTILIDAD:" -ForegroundColor Yellow
            Write-Host "   Es la forma diaria y rapida de desarrollar con Hot-Reload instantaneo."
            Write-Host ""
            Write-Host "CRITICIDAD: CRITICA (Indispensable para desarrollo local)" -ForegroundColor Red
            Write-Host ""
            Write-Host "MODO DE USO:" -ForegroundColor Yellow
            Write-Host "   Pulsa 1 en el menu principal. Abre tu navegador en http://localhost:3001."
        }
        "2" {
            Write-Host "OPCION [2]: Iniciar Oraculo en Docker (Stack Completo Contenedores)" -ForegroundColor Green
            Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "QUE HACE:" -ForegroundColor Yellow
            Write-Host "   Ejecuta 'docker-compose down' y 'docker-compose up --build -d'."
            Write-Host "   Levanta Backend, Frontend, Nginx y Redis en contenedores aislados."
            Write-Host ""
            Write-Host "UTILIDAD:" -ForegroundColor Yellow
            Write-Host "   Verificar que la compilacion de produccion funcione antes de subir a la nube."
            Write-Host ""
            Write-Host "CRITICIDAD: MEDIA (Alternativa de pruebas integradas)" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "MODO DE USO:" -ForegroundColor Yellow
            Write-Host "   Asegurate de tener Docker Desktop abierto. Pulsa 2 y accede a http://localhost:3001."
        }
        "3" {
            Write-Host "OPCION [3]: Ejecutar Suite Completa de Tests y Diagnostico de Codigo" -ForegroundColor Green
            Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "QUE HACE:" -ForegroundColor Yellow
            Write-Host "   Lanza Pytest contra la carpeta tests/ evaluando 35 suites de tests."
            Write-Host ""
            Write-Host "UTILIDAD:" -ForegroundColor Yellow
            Write-Host "   Previene regresiones y confirma que no se haya roto la autenticacion,"
            Write-Host "   los scrapers, el calculo de precios o el Grimorio Lore."
            Write-Host ""
            Write-Host "CRITICIDAD: ALTA (Seguridad antes de commits o despliegues)" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "MODO DE USO:" -ForegroundColor Yellow
            Write-Host "   Pulsa 3 y verifica que todos los tests muestren PASSED en verde."
        }
        "4" {
            Write-Host "OPCION [4]: Iniciar Nexus Local Bridge (Worker Residencial Wallapop)" -ForegroundColor Green
            Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "QUE HACE:" -ForegroundColor Yellow
            Write-Host "   Escucha trabajos de busqueda pendientes de Wallapop o Smyths Toys"
            Write-Host "   y los procesa desde tu PC con tu direccion IP residencial de casa."
            Write-Host ""
            Write-Host "UTILIDAD:" -ForegroundColor Yellow
            Write-Host "   Wallapop bloquea las IPs de Datacenter (Oracle Cloud). Tu IP residencial"
            Write-Host "   permite extraer las ofertas sin ser bloqueado y enviarlas al Purgatorio."
            Write-Host ""
            Write-Host "CRITICIDAD: ALTA (Puente esencial para Wallapop a coste 0)" -ForegroundColor Red
            Write-Host ""
            Write-Host "MODO DE USO:" -ForegroundColor Yellow
            Write-Host "   Pulsa 4 y dejalo corriendo mientras quieras procesar busquedas. Ctrl + C para parar."
        }
        "5" {
            Write-Host "OPCION [5]: Abrir Google Chrome en Depuracion (Puerto 9222)" -ForegroundColor Green
            Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "QUE HACE:" -ForegroundColor Yellow
            Write-Host "   Abre Google Chrome en puerto 9222 con un perfil limpio (scratch/chrome_dev)"
            Write-Host "   y las banderas de automatizacion desactivadas."
            Write-Host ""
            Write-Host "UTILIDAD:" -ForegroundColor Yellow
            Write-Host "   Permite al usuario humano iniciar sesion y pasar captchas en tiendas protegidas"
            Write-Host "   para luego extraer los datos con la opcion 6."
            Write-Host ""
            Write-Host "CRITICIDAD: ALTA (Evasion antibot asistida)" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "MODO DE USO:" -ForegroundColor Yellow
            Write-Host "   Pulsa 5, abre la web de la tienda que quieras consultar y dejala abierta."
        }
        "6" {
            Write-Host "OPCION [6]: Incursion Asistida Universal (CDP Multi-tienda)" -ForegroundColor Green
            Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "QUE HACE:" -ForegroundColor Yellow
            Write-Host "   Conecta via Playwright CDP al Chrome de la opcion 5, lee la pestaña activa"
            Write-Host "   y extrae las figuras y precios sin disparar protecciones antibot."
            Write-Host ""
            Write-Host "UTILIDAD:" -ForegroundColor Yellow
            Write-Host "   Metodo definitivo infalible cuando los bots automaticos son bloqueados."
            Write-Host ""
            Write-Host "CRITICIDAD: ALTA (Herramienta antibloqueo definitiva)" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "MODO DE USO:" -ForegroundColor Yellow
            Write-Host "   Con Chrome abierto en 9222 mostrando figuras, pulsa 6 en este menu."
        }
        "7" {
            Write-Host "OPCION [7]: Incursion Directa Multi-Tienda (Smyths, Wallapop, Vinted, eBay...)" -ForegroundColor Green
            Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "QUE HACE:" -ForegroundColor Yellow
            Write-Host "   Permite elegir cualquier tienda soportada y lanzar una extraccion rapida"
            Write-Host "   desde la consola usando tu IP residencial."
            Write-Host ""
            Write-Host "UTILIDAD:" -ForegroundColor Yellow
            Write-Host "   Actualizar los precios o descubrir novedades en Smyths Toys, Wallapop,"
            Write-Host "   Vinted, eBay o Amazon de forma individual en segundos."
            Write-Host ""
            Write-Host "CRITICIDAD: MEDIA-ALTA | REGLA: Vintage inhabilitado en scrapers" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "MODO DE USO:" -ForegroundColor Yellow
            Write-Host "   Pulsa 7, selecciona la tienda (1-6) y confirma la consulta."
        }
        "8" {
            Write-Host "OPCION [8]: Desplegar y Actualizar en Oracle Cloud (1 Clic)" -ForegroundColor Green
            Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "QUE HACE:" -ForegroundColor Yellow
            Write-Host "   Conecta por SSH al VPS (opc@79.72.50.244), hace git reset --hard origin/main,"
            Write-Host "   git pull y compila los nuevos contenedores en docker-compose.prod.yml."
            Write-Host ""
            Write-Host "UTILIDAD:" -ForegroundColor Yellow
            Write-Host "   Pasa todos los cambios commiteados en GitHub a produccion con 1 clic."
            Write-Host ""
            Write-Host "CRITICIDAD: CRITICA (Despliegue a produccion)" -ForegroundColor Red
            Write-Host ""
            Write-Host "MODO DE USO:" -ForegroundColor Yellow
            Write-Host "   Haz 'git push origin main' primero, pulsa 8 y espera la confirmacion."
        }
        "9" {
            Write-Host "OPCION [9]: Conectar por Terminal SSH al Servidor en la Nube" -ForegroundColor Green
            Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "QUE HACE:" -ForegroundColor Yellow
            Write-Host "   Abre una consola SSH interactiva directa en el servidor de Oracle Cloud."
            Write-Host ""
            Write-Host "UTILIDAD:" -ForegroundColor Yellow
            Write-Host "   Ver logs de contenedores, revisar espacio o memoria en el servidor."
            Write-Host ""
            Write-Host "CRITICIDAD: ALTA (Administracion del servidor)" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "MODO DE USO:" -ForegroundColor Yellow
            Write-Host "   Pulsa 9. Para volver, escribe 'exit' y pulsa Enter."
        }
        "10" {
            Write-Host "OPCION [10]: Renovar Certificados SSL en Oracle Cloud (Emergencia)" -ForegroundColor Green
            Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "QUE HACE:" -ForegroundColor Yellow
            Write-Host "   Ejecuta 'bash scripts/renew_ssl.sh --force' via SSH en el servidor."
            Write-Host ""
            Write-Host "UTILIDAD:" -ForegroundColor Yellow
            Write-Host "   Restaura los certificados SSL de oraculo-eternia.duckdns.org si han expirado."
            Write-Host ""
            Write-Host "CRITICIDAD: MEDIA (Herramienta de rescate HTTPS)" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "MODO DE USO:" -ForegroundColor Yellow
            Write-Host "   Pulsa 10. Certbot regenerara las claves y recargara Nginx."
        }
        "11" {
            Write-Host "OPCION [11]: Realizar Backup Dual Completo (SQLite Local + Supabase Cloud)" -ForegroundColor Green
            Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "QUE HACE:" -ForegroundColor Yellow
            Write-Host "   Copia en caliente 'oraculo.db' hacia backups/ manteniendo los 10 ultimos"
            Write-Host "   y ofrece descargar un snapshot completo de Supabase Cloud (PostgreSQL)."
            Write-Host ""
            Write-Host "UTILIDAD:" -ForegroundColor Yellow
            Write-Host "   Blindaje total de tu base de datos local y remota contra pérdidas de datos."
            Write-Host ""
            Write-Host "CRITICIDAD: ALTA (Proteccion de datos)" -ForegroundColor Red
            Write-Host ""
            Write-Host "MODO DE USO:" -ForegroundColor Yellow
            Write-Host "   Pulsa 11 en el menu o ejecuta '.\oraculo.ps1 -Backup' de forma desatendida."
        }
        "12" {
            Write-Host "OPCION [12]: Diagnostico de Paridad y Salud (SQLite vs Supabase)" -ForegroundColor Green
            Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "QUE HACE:" -ForegroundColor Yellow
            Write-Host "   Muestra en 2 segundos una tabla comparativa de productos, figuras Origins,"
            Write-Host "   ofertas en Purgatorio y perfiles del Grimorio Lore entre SQLite y Supabase."
            Write-Host ""
            Write-Host "UTILIDAD:" -ForegroundColor Yellow
            Write-Host "   Verificar que ambas bases de datos tengan la misma informacion."
            Write-Host ""
            Write-Host "CRITICIDAD: ALTA (Control de calidad y sincronizacion)" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "MODO DE USO:" -ForegroundColor Yellow
            Write-Host "   Pulsa 12 y revisa que la fila final indique 'Paridad Dual 100% Identica'."
        }
        "13" {
            Write-Host "OPCION [13]: Sincronizar Esquemas de Base de Datos (Universal Migrator)" -ForegroundColor Green
            Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "QUE HACE:" -ForegroundColor Yellow
            Write-Host "   Ejecuta universal_migrator.py para alinear columnas y tablas nuevas"
            Write-Host "   en SQLite y en Supabase sin necesidad de migraciones complejas de Alembic."
            Write-Host ""
            Write-Host "UTILIDAD:" -ForegroundColor Yellow
            Write-Host "   Imprescindible cuando se agregan nuevos campos o tablas a models.py."
            Write-Host ""
            Write-Host "CRITICIDAD: ALTA (Mantenimiento estructural de datos)" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "MODO DE USO:" -ForegroundColor Yellow
            Write-Host "   Pulsa 13 tras modificar modelos en src/domain/models.py."
        }
        "14" {
            Write-Host "OPCION [14]: Sembrar / Sincronizar Grimorio Lore Canónico (Origins Dual)" -ForegroundColor Green
            Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "QUE HACE:" -ForegroundColor Yellow
            Write-Host "   Puebla los 54 perfiles canónicos y las 338+ figuras Origins en español"
            Write-Host "   simultaneamente en SQLite local y en Supabase Cloud con coste 0 (Sin IA)."
            Write-Host ""
            Write-Host "UTILIDAD:" -ForegroundColor Yellow
            Write-Host "   Llena el Grimorio Lore y asegura que las cartas coleccionables tengan"
            Write-Host "   textos del reverso de blister, facciones y stats perfectamente sincronizadas."
            Write-Host ""
            Write-Host "CRITICIDAD: ALTA (Resuelve el Grimorio vacio en ambas BDs)" -ForegroundColor Red
            Write-Host ""
            Write-Host "MODO DE USO:" -ForegroundColor Yellow
            Write-Host "   Pulsa 14 y elige si deseas forzar la actualizacion de textos no verificados."
        }
        "15" {
            Write-Host "OPCION [15]: Refrescar Imagen de Figura desde ActionFigure411 (Dual)" -ForegroundColor Green
            Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "QUE HACE:" -ForegroundColor Yellow
            Write-Host "   Descarga la imagen oficial de AF411 para un ID concreto, la optimiza"
            Write-Host "   y la guarda tanto en SQLite local como en Supabase Cloud y Storage."
            Write-Host ""
            Write-Host "UTILIDAD:" -ForegroundColor Yellow
            Write-Host "   Corregir de forma quirurgica figuras con fotos rotas o de baja calidad."
            Write-Host ""
            Write-Host "CRITICIDAD: MEDIA-BAJA (Herramienta puntual)" -ForegroundColor DarkGray
            Write-Host ""
            Write-Host "MODO DE USO:" -ForegroundColor Yellow
            Write-Host "   Pulsa 15 e introduce el ID de la figura (ej. 14038)."
        }
        "17" {
            Write-Host "OPCION [17]: Crear / Actualizar Accesos Directos en el Escritorio" -ForegroundColor Green
            Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host "QUE HACE:" -ForegroundColor Yellow
            Write-Host "   Crea los archivos .lnk en tu Escritorio de Windows para abrir este Centro"
            Write-Host "   de Control o para hacer copias de seguridad con 1 doble clic."
            Write-Host ""
            Write-Host "UTILIDAD:" -ForegroundColor Yellow
            Write-Host "   Comodidad para no tener que abrir la terminal de comandos manualmente."
            Write-Host ""
            Write-Host "CRITICIDAD: BAJA (Utilidad inicial)" -ForegroundColor DarkGray
            Write-Host ""
            Write-Host "MODO DE USO:" -ForegroundColor Yellow
            Write-Host "   Pulsa 17 y comprueba tu Escritorio de Windows."
        }
        Default {
            Write-Host "Opcion no valida." -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Read-Host "Presiona [Enter] para volver al menu FAQ..."
}

function Invoke-ShowFAQ {
    do {
        Clear-Host
        Write-Host "===================================================================" -ForegroundColor Cyan
        Write-Host "      *  GUIA Y PREGUNTAS FRECUENTES (FAQ) DEL CENTRO DE MANDO *   " -ForegroundColor Yellow
        Write-Host "===================================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  Elige una opcion para ver su explicacion tecnica detallada:" -ForegroundColor White
        Write-Host ""
        Write-Host "  [ ENTORNO Y EJECUCION ]" -ForegroundColor DarkCyan
        Write-Host "    [1]  Iniciar Oraculo en Local       [2]  Iniciar en Docker"
        Write-Host "    [3]  Suite Completa de Tests"
        Write-Host ""
        Write-Host "  [ BÚSQUEDAS Y SCRAPING ]" -ForegroundColor DarkCyan
        Write-Host "    [4]  Nexus Local Bridge             [5]  Chrome Depuracion (9222)"
        Write-Host "    [6]  Incursion Asistida (CDP)       [7]  Incursion Directa Multi-Tienda"
        Write-Host ""
        Write-Host "  [ NUBE Y PRODUCCION ]" -ForegroundColor DarkCyan
        Write-Host "    [8]  Desplegar en Oracle Cloud      [9]  Terminal SSH Servidor"
        Write-Host "    [10] Renovar SSL en Oracle Cloud"
        Write-Host ""
        Write-Host "  [ BASE DE DATOS Y LORE ]" -ForegroundColor DarkCyan
        Write-Host "    [11] Backup Dual Completo           [12] Diagnostico Paridad SQLite/Supabase"
        Write-Host "    [13] Universal Migrator             [14] Sembrar Grimorio Lore Origins Dual"
        Write-Host "    [15] Refrescar Imagen AF411"
        Write-Host ""
        Write-Host "  [ GENERAL ]" -ForegroundColor DarkCyan
        Write-Host "    [17] Crear Accesos Directos         [D]  Abrir Documento FAQ Completo (Markdown)"
        Write-Host ""
        Write-Host "    [0]  Volver al Menu Principal" -ForegroundColor Red
        Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
        $faqChoice = Read-Host "  Selecciona una opcion [1-17, D, 0]"

        if ($faqChoice.Trim() -eq "0") {
            break
        } elseif ($faqChoice.Trim().ToUpper() -eq "D") {
            $faqPath = Join-Path $PSScriptRoot "docs\FAQ_CENTRO_DE_CONTROL.md"
            if (Test-Path $faqPath) {
                Start-Process $faqPath
                Write-Host "Abriendo $faqPath..." -ForegroundColor Green
                Start-Sleep -Seconds 1
            } else {
                Write-Host "No se encontro el archivo $faqPath" -ForegroundColor Red
                Start-Sleep -Seconds 2
            }
        } elseif ($faqChoice.Trim() -match '^\d+$') {
            Show-OptionFaqDetail -optNum ($faqChoice.Trim())
        }
    } while ($true)
}

# -------------------------------------------------------------------
# [17] CREAR ACCESOS DIRECTOS
# -------------------------------------------------------------------
function Invoke-CreateShortcuts {
    Show-Header
    Write-Host "[17] CREANDO ACCESOS DIRECTOS EN EL ESCRITORIO..." -ForegroundColor Yellow
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
    $s2 = $WScriptShell.CreateShortcut($BackupShortcut)
    $s2.TargetPath = "powershell.exe"
    $s2.Arguments = "-ExecutionPolicy Bypass -NoExit -File `"$TargetScript`" -Backup"
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

# -------------------------------------------------------------------
# MODO AUTOMATICO VIA PARAMETRO (-Backup)
# -------------------------------------------------------------------
if ($Backup) {
    Invoke-BackupDual
    exit
}

# -------------------------------------------------------------------
# BUCLE PRINCIPAL DEL MENU
# -------------------------------------------------------------------
do {
    Show-Header
    Write-Host "  [ ENTORNO Y EJECUCION LOCAL ]" -ForegroundColor DarkCyan
    Write-Host "  [1]  Iniciar Oraculo en Local (Backend API + Frontend Nativo)" -ForegroundColor White
    Write-Host "  [2]  Iniciar Oraculo en Docker (The Ark Stack)" -ForegroundColor White
    Write-Host "  [3]  Ejecutar Suite Completa de Tests y Diagnostico" -ForegroundColor White
    Write-Host ""
    Write-Host "  [ BÚSQUEDAS Y SCRAPING RESIDENCIAL ]" -ForegroundColor DarkCyan
    Write-Host "  [4]  Iniciar Nexus Local Bridge (Worker Residencial Wallapop)" -ForegroundColor White
    Write-Host "  [5]  Abrir Google Chrome en Depuracion (Puerto 9222)" -ForegroundColor White
    Write-Host "  [6]  Incursion Asistida Universal (CDP Multi-tienda)" -ForegroundColor White
    Write-Host "  [7]  Incursion Directa Multi-Tienda (Smyths, Wallapop, Vinted, eBay...)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  [ NUBE Y PRODUCCION (ORACLE CLOUD & SUPABASE) ]" -ForegroundColor DarkCyan
    Write-Host "  [8]  Desplegar y Actualizar en Oracle Cloud (1 Clic)" -ForegroundColor Cyan
    Write-Host "  [9]  Conectar por Terminal SSH al Servidor en la Nube" -ForegroundColor Cyan
    Write-Host "  [10] Renovar Certificados SSL en Oracle Cloud (Emergencia)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [ BASE DE DATOS Y LORE ]" -ForegroundColor DarkCyan
    Write-Host "  [11] Realizar Backup Dual Completo (SQLite Local + Supabase Cloud)" -ForegroundColor Green
    Write-Host "  [12] Diagnostico de Paridad y Salud (SQLite vs Supabase)" -ForegroundColor Green
    Write-Host "  [13] Sincronizar Esquemas de Base de Datos (Universal Migrator)" -ForegroundColor Green
    Write-Host "  [14] Sembrar / Sincronizar Grimorio Lore Canonico (Origins Dual)" -ForegroundColor Green
    Write-Host "  [15] Refrescar Imagen de Figura desde ActionFigure411 (Dual)" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "  [ GUIA Y UTILIDADES ]" -ForegroundColor DarkCyan
    Write-Host "  [16] Menu FAQ y Guia de Uso del Centro de Control" -ForegroundColor Yellow
    Write-Host "  [17] Crear / Actualizar Accesos Directos en el Escritorio" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  [0]  Salir" -ForegroundColor Red
    Write-Host "-------------------------------------------------------------------" -ForegroundColor DarkGray
    $choice = Read-Host "  Selecciona una opcion [0-17]"

    switch ($choice.Trim()) {
        "1"  { Invoke-LocalStart }
        "2"  { Invoke-DockerStart }
        "3"  { Invoke-RunTests }
        "4"  { Invoke-NexusBridge }
        "5"  { Invoke-ChromeDebug }
        "6"  { Invoke-AssistedIncursion }
        "7"  { Invoke-MultiIncursion }
        "8"  { Invoke-DeployCloud }
        "9"  { Invoke-SshConnect }
        "10" { Invoke-RenewSslCloud }
        "11" { Invoke-BackupDual }
        "12" { Invoke-DiagnosticDb }
        "13" { Invoke-UniversalMigrator }
        "14" { Invoke-SeedCanonicalLore }
        "15" { Invoke-RefreshFigureImage }
        "16" { Invoke-ShowFAQ }
        "17" { Invoke-CreateShortcuts }
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

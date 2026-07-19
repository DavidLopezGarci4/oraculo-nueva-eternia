# Launch Google Chrome with remote debugging port 9222 enabled
# Uso: .\launch_chrome_debug.ps1

Clear-Host
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "BUSCANDO Y LANZANDO CHROME EN MODO DEPURACION" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Lista de rutas comunes de instalacion de Chrome en Windows
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
    Write-Host "❌ No se pudo encontrar google chrome.exe en las rutas habituales." -ForegroundColor Red
    Write-Host "Por favor, abre una ventana de Ejecutar (Win+R) y lanza el comando especificando la ruta completa a tu chrome.exe." -ForegroundColor Yellow
    Exit
}

Write-Host "✨ Google Chrome encontrado en: $ChromePath" -ForegroundColor Green
# Definir directorio temporal dentro de scratch en el espacio de trabajo para evitar fallos de permisos en C:\
$UserDataDir = Join-Path $PSScriptRoot "scratch\chrome_dev"
if (!(Test-Path $UserDataDir)) {
    New-Item -ItemType Directory -Path $UserDataDir -Force | Out-Null
}

Write-Host "🚀 Iniciando Chrome en el puerto 9222 (perfil depurador en $UserDataDir)..." -ForegroundColor Yellow

# Lanzar Chrome con flags de evasión de WAF (CloudFront/Cloudflare) y automatización controlada
$ArgList = @(
    "--remote-debugging-port=9222",
    "--user-data-dir=$UserDataDir",
    "--disable-blink-features=AutomationControlled",
    "--no-first-run",
    "--no-default-browser-check",
    "--start-maximized"
)

Start-Process -FilePath $ChromePath -ArgumentList $ArgList

Write-Host ""
Write-Host "¡Chrome abierto con éxito!" -ForegroundColor Green
Write-Host "Ahora sigue estos pasos en la ventana de Chrome que se acaba de abrir:" -ForegroundColor White
Write-Host "1. Entra a Smyths Toys y navega hasta ver las figuras de Masters of the Universe." -ForegroundColor Gray
Write-Host "2. Vuelve a este terminal de PowerShell y ejecuta: .\run_smyths_attached.ps1" -ForegroundColor Gray
Write-Host ""


# 🛠️ Oráculo Tool: Node Path Resolver
# Este script localiza las rutas absolutas para ejecutar herramientas de Node sin depender del PATH global.

function Get-OraculoNodePaths {
    $paths = @{
        node = $null
        npx  = $null
        npm  = $null
    }

    # 1. Intentar rutas estándar de instalación
    $standardDirs = @(
        "C:\Program Files\nodejs",
        "C:\Program Files (x86)\nodejs",
        "$env:AppData\npm"
    )

    foreach ($dir in $standardDirs) {
        if (Test-Path "$dir\node.exe") { $paths.node = "$dir\node.exe" }
        if (Test-Path "$dir\npx.cmd") { $paths.npx = "$dir\npx.cmd" }
        if (Test-Path "$dir\npm.cmd") { $paths.npm = "$dir\npm.cmd" }
    }

    # 2. Localizar npx-cli.js para ejecución vía Node directo (omite ExecutionPolicy)
    if ($paths.node) {
        $nodeBase = Split-Path $paths.node
        $cliJs = "$nodeBase\node_modules\npm\bin\npx-cli.js"
        if (Test-Path $cliJs) { $paths.npx_js = $cliJs }
    }

    return $paths
}

# --- FUNCIÓN DE SALVAGUARDA (BUILD HELPER) ---
function Invoke-OraculoVite {
    param([string]$cmdArgs = "create-vite@latest frontend --template react-ts --yes")
    
    $cfg = Get-OraculoNodePaths
    
    if ($cfg.node -and $cfg.npx_js) {
        Write-Host ">>> Ejecutando via NPX-CLI directo (Recomendado)..." -ForegroundColor Green
        & $cfg.node $cfg.npx_js $cmdArgs.Split(" ")
    }
    elseif ($cfg.npx) {
        Write-Host ">>> Ejecutando via NPX.CMD..." -ForegroundColor Yellow
        & $cfg.npx $cmdArgs.Split(" ")
    }
    else {
        Write-Error "CRITICAL: No se ha detectado Node.js ni NPX en el sistema. Asegúrate de instalar Node.js desde https://nodejs.org/"
    }
}

# Exportar las rutas para persistencia si se necesita
$global:ORACULO_PATHS = Get-OraculoNodePaths
Write-Host "✅ Oráculo Node Resolver cargado correctamente."
Write-Host "Usa 'Invoke-OraculoVite' para ejecutar comandos de frontend."

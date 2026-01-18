
# Script para crear acceso directo en el Escritorio
# Ejecuta esto una vez: .\create_desktop_shortcut.ps1

$WScriptShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutFile = Join-Path $DesktopPath "Oraculo Docker.lnk"
$TargetScript = Join-Path $PSScriptRoot "launch_ark.ps1"
$IconPath = Join-Path $PSScriptRoot "frontend\public\favicon.ico" # Try to use favicon if exists, else powershell

$Shortcut = $WScriptShell.CreateShortcut($ShortcutFile)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -NoExit -File `"$TargetScript`""
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "Lanzar El Oráculo de Nueva Eternia (Docker)"

# Set Icon if it exists (Optional polish)
$Shortcut.IconLocation = "powershell.exe"

$Shortcut.Save()

Write-Host "✅ Acceso directo creado en: $ShortcutFile" -ForegroundColor Green
Write-Host "Ahora puedes hacer doble clic en 'Oraculo Docker' en tu escritorio." -ForegroundColor Cyan

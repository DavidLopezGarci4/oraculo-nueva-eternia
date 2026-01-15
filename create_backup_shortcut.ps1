
# Script para crear acceso directo de Backups en el Escritorio
# Ejecuta esto una vez: .\create_backup_shortcut.ps1

$WScriptShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutFile = Join-Path $DesktopPath "Oraculo - Guardián de Datos.lnk"
$TargetScript = Join-Path $PSScriptRoot "backup_db.ps1"

$Shortcut = $WScriptShell.CreateShortcut($ShortcutFile)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -NoExit -File `"$TargetScript`""
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "Crear Copia de Seguridad del Oráculo"

# Icono de escudo/seguridad (Powershell tiene uno por defecto que sirve)
$Shortcut.IconLocation = "shell32.dll,44" # Icono de disco/seguridad clásico de Windows

$Shortcut.Save()

Write-Host "✅ Acceso directo 'Guardián de Datos' creado en el Escritorio." -ForegroundColor Green
Write-Host "Ahora puedes hacer una copia de seguridad con un doble clic antes de cualquier cambio importante." -ForegroundColor Cyan


# 🛡️ Oráculo DB Backup Script
# Guarda una copia fechada de la base de datos para evitar desastres.

$BackupDir = Join-Path $PSScriptRoot "backups"
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmm"
$SourceDB = Join-Path $PSScriptRoot "oraculo.db"
$DestDB = Join-Path $BackupDir "oraculo_$Timestamp.db"

if (Test-Path $SourceDB) {
    Copy-Item $SourceDB $DestDB
    Write-Host "✅ Backup creado con éxito: oraculo_$Timestamp.db" -ForegroundColor Green
    
    # Limpieza: Mantener solo los últimos 10 backups
    $Backups = Get-ChildItem $BackupDir | Sort-Object LastWriteTime -Descending
    if ($Backups.Count -gt 10) {
        $Backups[10..($Backups.Count - 1)] | Remove-Item
        Write-Host "🧹 Backups antiguos eliminados (mantenemos los 10 más recientes)." -ForegroundColor Gray
    }
}
else {
    Write-Host "❌ Error: No se encontró oraculo.db para copiar." -ForegroundColor Red
}

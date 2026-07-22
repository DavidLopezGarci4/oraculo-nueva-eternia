
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
    # Fase AAA-Ola2 (2c): un Copy-Item normal solo copia el archivo .db tal
    # cual esta en ese instante. Si la BD esta en modo WAL (habitual en
    # SQLite), los cambios recientes viven en un .db-wal aparte y un copiado
    # simple los PIERDE (verificado: perdio datos reales durante las pruebas
    # de la migracion Alembic de esta misma app). sqlite3.backup() de Python
    # usa la API de backup online de SQLite: produce una instantanea
    # consistente sin importar el modo WAL, incluso con la app corriendo.
    $PythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    if (!(Test-Path $PythonExe)) { $PythonExe = "python" }

    $BackupScript = @"
import sqlite3
src = sqlite3.connect(r'$SourceDB')
dst = sqlite3.connect(r'$DestDB')
src.backup(dst)
dst.close()
src.close()
"@

    & $PythonExe -c $BackupScript

    if ($LASTEXITCODE -ne 0 -or !(Test-Path $DestDB)) {
        Write-Host "❌ Error: el backup via sqlite3.backup() fallo." -ForegroundColor Red
        exit 1
    }

    Write-Host "✅ Backup creado con éxito: oraculo_$Timestamp.db" -ForegroundColor Green
    
    # Limpieza: Mantener solo los últimos 10 backups
    $Backups = Get-ChildItem $BackupDir -File | Sort-Object LastWriteTime -Descending
    if ($Backups.Count -gt 10) {
        $Backups[10..($Backups.Count - 1)] | Remove-Item -Force
        Write-Host "🧹 Backups antiguos eliminados (mantenemos los 10 más recientes)." -ForegroundColor Gray
    }
}
else {
    Write-Host "❌ Error: No se encontró oraculo.db para copiar." -ForegroundColor Red
}

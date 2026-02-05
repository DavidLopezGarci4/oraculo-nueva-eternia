---
name: 3ox-windows-search
description: Provee herramientas de búsqueda (grep-like) nativas para Windows/PowerShell de forma no invasiva.
---

# 🔍 SKILL: Windows Search Compatibility (3OX)

**Propósito**: Evitar errores de "comando no encontrado" al intentar usar `grep` o `rg` en sistemas Windows, proporcionando un buscador nativo basado en PowerShell.

## 1. Herramienta Principal: `win-grep.ps1`
Usa este script cuando necesites buscar texto en archivos y obtener el número de línea.

**Uso**:
```powershell
powershell -ExecutionPolicy Bypass -File .agent/skills/3ox-windows-search/scripts/win-grep.ps1 -Pattern "tu_patron" -Path "ruta/al/archivo"
```

## 2. Fallback Directo (One-liner)
Si no quieres usar el script, usa el comando nativo de PowerShell:
```powershell
Select-String -Pattern "patron" -Path "archivo" | Select-Object LineNumber, Line
```

## 3. Reglas de Oro
- **NUNCA** asumas que `grep` está disponible en Windows.
- **SIEMPRE** verifica el sistema operativo (actualmente: Windows) antes de ejecutar comandos de búsqueda.
- **NO** instales binarios adicionales si no es estrictamente necesario; usa las herramientas del sistema.

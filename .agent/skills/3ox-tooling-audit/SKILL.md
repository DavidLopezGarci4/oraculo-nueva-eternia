---
name: 3ox-tooling-audit
description: Diagnóstico de Entorno y Trazabilidad (3OX). Asegura que las herramientas de auditoría estén disponibles o usa fallbacks de PowerShell.
---

# 🧩 SKILL: Tooling Audit & Command Resolution

## Problem
`CommandNotFoundException` para utilidades core como `grep` o `rg` en entornos Windows/PowerShell.

## Context
Necesario para auditorías iniciales y mantenimiento del `architecture_map.md`.

## 1. Mapeo de Equivalencias (Fallback)
Si la herramienta no está instalada, usar el motor nativo de PowerShell:

*   **Para grep**: `Select-String -Pattern "text" -Path "file"`
*   **Para rg**: `Select-String -Pattern "text" -Path "file" | Select-Object LineNumber, Line`

## 2. Verificación de Dependencias (Assess Phase)
Antes de ejecutar scripts de auditoría en `dev/`, verificar existencia:

```powershell
if (!(Get-Command rg -ErrorAction SilentlyContinue)) { 
    Write-Warning "ripgrep (rg) no detectado. Usando Select-String como fallback." 
}
```

## 3. Trazabilidad en 3OX
*   **Log**: Registrar en `3ox.log` si se usó una herramienta nativa o externa para la auditoría.
*   **Verify**: Asegurar que la salida de `Select-String` sea parseada correctamente para mantener la consistencia del `architecture_map.md`.

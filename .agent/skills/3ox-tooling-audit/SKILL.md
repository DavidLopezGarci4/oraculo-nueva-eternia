---
name: 3ox-tooling-audit
description: Diagnóstico de Entorno y Trazabilidad (3OX). Asegura que las herramientas de auditoría estén disponibles o usa fallbacks de PowerShell.
---

# 🧩 SKILL: Environment Integrity & Unicode Resilience (3OX)

**Propósito**: Garantizar que el agente tenga las herramientas necesarias (`rg`, `grep`) y la configuración de codificación correcta para procesar datos sin corrupción.

## 1. Verificación de Comandos (Audit Phase)
Antes de iniciar cualquier tarea de auditoría o búsqueda en el código:

*   **Acción**: Validar disponibilidad de herramientas externas (`rg`, `grep`).
*   **Fallback**: Si `rg` o `grep` fallan, conmutar automáticamente a `Select-String` en PowerShell para no detener el flujo:
    *   **Grep**: `Select-String -Pattern "text" -Path "file"`
    *   **Ripgrep**: `Select-String -Pattern "text" -Path "file" | Select-Object LineNumber, Line`

## 2. Blindaje UTF-8 (Execute Phase)
Para evitar el error de caracteres corruptos (``) y fallos en selectores CSS:

*   **Entorno**: Forzar `set PYTHONUTF8=1` (o `$env:PYTHONUTF8=1` en PowerShell) antes de cualquier ejecución.
*   **Script**: Incluir obligatoriamente el wrapper de salida en el punto de entrada:
    ```python
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    ```
*   **Web Scraping**: En `dev/adapters` (o scrapers), usar siempre `response.encoding = response.apparent_encoding` antes de procesar el HTML si se usa `requests`. En Playwright, asegurar la captura en `utf-8`.

## 3. Trazabilidad y Registro (Log Phase)
Actualizar el `3ox.log` con el estado del entorno:

*   **[ASSESS]** Tooling check: `rg` found / `grep` missing (using fallback).
*   **[VERIFY]** Encoding check: UTF-8 shield active. No mojibake detected.

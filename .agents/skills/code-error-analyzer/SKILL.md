---
name: code-error-analyzer
description: Analiza la base de código del Oráculo de Nueva Eternia en busca de inconsistencias, errores de tipos, discrepancias de base de datos o fallas de lógica.
---

# Skill: Analizador de Inconsistencias de Código

Esta skill proporciona las directivas para llevar a cabo una auditoría de la base de código del Oráculo (FastAPI + React).

## Metodología de Inspección

1. **Integridad de Base de Datos**:
   - Comparar los modelos de SQLAlchemy (`src/domain/models.py`) con el esquema de tablas en Supabase PostgreSQL y SQLite.
   - Detectar discrepancias de constraints (`NOT NULL`, llaves foráneas, nombres de campos).

2. **Acoplamiento de Scrapers**:
   - Validar que todos los scripts importados en `run_scraper_task` existan y tengan la firma correcta.
   - Verificar si existen scrapers huérfanos o inactivos no mapeados en `spiders_map`.

3. **Consistencia de Tipos en Frontend**:
   - Verificar que los componentes de React utilicen correctamente las propiedades de objetos API devueltos.
   - Detectar incoherencias en el tipado de TypeScript.

4. **Fugas de Privacidad / Evasión de Incógnito**:
   - Asegurar que todas las vistas del frontend que manejan valor monetario, ROI o conteos de posesión real apliquen el filtro `blur-incognito` condicionado a `isIncognito` o la clase global `.mode-incognito`.

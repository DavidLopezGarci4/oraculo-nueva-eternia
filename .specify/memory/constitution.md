# Constitución del Proyecto: Oráculo de Nueva Eternia
Arquitectura Híbrida SDD (Spec Kit + Gentle-AI + Engram + uv)

## 1. Misión y Dominio
Oráculo de Nueva Eternia es un sistema inteligente de agregación, scraping, matching y auditoría de ofertas comerciales desarrollado en Python (FastAPI, SQLAlchemy, Playwright/BeautifulSoup).

## 2. Gobernanza y Memoria
- **Memoria Persistente**: Búsqueda obligatoria de contexto previo con `engram search --query "Oraculo <modulo>"` antes de planificar. Persistencia de lecciones y patrones con `engram save`.
- **Fuente de Verdad**: Todo desarrollo se documenta en `.specify/memory/` (`spec.md`, `plan.md`, `tasks.md`).

## 3. Disciplina Técnica Gentle-AI & uv
- **Gestor Python**: Uso exclusivo de `uv` (`uv run pytest`, `uv add`, `uv pip install`).
- **TDD Estricto**:
  1. RED: Escribir tests en `tests/` que capturen la funcionalidad o bug.
  2. GREEN: Desarrollar la solución mínima que supere la prueba.
  3. REFACTOR: Refactorizar manteniendo la suite de pruebas completa en verde (`uv run pytest -q`).
- **Lentes 4R**:
  - **Risk**: Asegurar la integridad de la base de datos de productos y el histórico de auditoría (`data/logs/audit_receipts`).
  - **Resilience**: Manejo robusto de bloqueos anti-bot, rotación de scrapers y timeouts.
  - **Readability**: Arquitectura limpia por capas (domain, application, infrastructure, interfaces).
  - **Reliability**: Cero regresiones en la suite de pruebas unitarias e integración.

## 4. Ejecución Reactiva
- Prohibición de polling manual. Operaciones asíncronas reactivas.

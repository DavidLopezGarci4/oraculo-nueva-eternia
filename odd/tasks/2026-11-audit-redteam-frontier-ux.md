# ODD Task: Migración a ODD v4 + Auditoría Bugs/Rendimiento + UX/UI Frontier + Red Team

- **Estado:** `DONE`
- **Glosario e Invariantes:** Ver `docs/CONTEXT.md` y `.agents/AGENTS.md` (Secciones 2 y 3).
- **Restricción de Tree Activo:** Preservar íntegramente los cambios previos del Grimorio MOTU (338 figuras por `figure_id`).

## Criterios de Aceptación Globales
1. Opción A activa: `.agents/AGENTS.md` usa ODD (`gentle-ai` + `work-unit-commits`), `.agents/skills/specification-driven-development/` eliminado y `test_api_db_rls_governance.py` en verde sin excepciones legacy.
2. Cero vulnerabilidades `CRITICAL`/`HIGH` abiertas tras remediación Red Team (`test_redteam_security_hardening.py` en verde).
3. Cero regresiones de integridad/rendimiento backend (`test_backend_bugs_and_perf.py` en verde: `sync_availability` seguro, cascadas FK limpias, Vault duplicados OK, asyncio no bloqueado en rutas sync).
4. Cero fugas de precios manuales / modo incógnito (`AGENTS.md` Regla 2) y arquitectura Frontend optimizada (`LoginPage` bajo `<Suspense>`, code-splitting de `TradingCardModal` + `html-to-image`, `useDeferredValue`, sin fugas de intervalos/blobs).
5. UX/UI Frontier (`<= 400` líneas aisladas en WU5): `impeccable.exe detect --no-config --json frontend/src` == `[]`, pila modal LIFO sin colisiones de `Escape`, accesibilidad completa y 4 estados de vista con reintento.
6. Verificación adversarial ciega dual (`judgment-day`), `npm --prefix frontend run build` limpio, `pytest` completo en verde y cierre obligatorio en Engram.

## Plan de Unidades de Trabajo (Work Units)

| Unidad | Estado | Alcance | Evidencia / Resultado | Límites de Rollback |
| :--- | :--- | :--- | :--- | :--- |
| **WU1** | `DONE` | Migración Opción A SDD -> ODD v4 | `test_api_db_rls_governance.py`: `6 passed in 2.02s` | `.agents/AGENTS.md`, `docs/CONTEXT.md`, `odd/` |
| **WU2** | `DONE` | Red Team Security & Governance (`RED -> GREEN`) | `test_redteam_security_hardening.py` + suite auth/perms/showcase/image/perf: `48 passed in 23.05s` (`task-1229`) | `src/core/{safe_http,config,logger,rate_limit}.py`, `deps.py`, routers, `database_cloud.py`, workflows |
| **WU3** | `DONE` | Bugs Backend, Integridad FK y Rendimiento Async (`RED -> GREEN`) | `test_backend_bugs_and_perf.py` + `test_api_db_rls_governance.py` + `test_api_response_schemas.py`: `29 passed in 20.70s` (`task-1524`) | `pipeline.py`, repositorios, servicios, routers, `models.py` + migración índices |
| **WU4** | `DONE` | Privacidad Precios Manuales, Bugs & Perf Frontend | `npm --prefix frontend run build` (`tsc -b && vite build`): `3755 modules, 15.56s, exit 0` (`task-1692`) | `frontend/src/{App.tsx,pages/*,components/*,api/*}` |
| **WU5** | `DONE` | UX/UI Frontier & Accesibilidad (`<= 400` líneas) | `impeccable detect` = `[]`; diff UI `221+/80-`; `vite build`: `3755 modules, 14.49s, exit 0` (`task-1724`) | `useModalA11y.ts`, `index.css`, `index.html`, modales/cards UI |
| **WU6** | `DONE` | Red Team Dual Ciego (`judgment-day`), Suite Completa & Engram | Ronda 1+2 (`judgment-day`) cerradas; `pytest tests/` (`153 passed in 66.83s`), `impeccable detect` (`[]`), `vite build` (`3755 modules, 17.14s`), `alembic heads` (`b8d4f02a19c3`), cierre Engram (`b77509e4-b7d5-4a1f-84e0-3c3b4cbdc4bf-odd-wu6`) | `main.py`, `users.py`, `safe_http.py`, `pipeline.py`, `telegram_listener.py`, `pyproject.toml`, tests |

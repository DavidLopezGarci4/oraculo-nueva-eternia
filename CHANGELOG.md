# Changelog

Todos los cambios relevantes de producto de **El Oráculo de Nueva Eternia** se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto se rige por [Semantic Versioning 2.0.0](https://semver.org/lang/es/) e **ISO/IEC 19770-2** (`mobile-app-versioning v2.0`).

> **Nota de reconciliación de versionado (Octubre 2026):** Las fases internas de ingeniería registradas en `docs/MASTER_ROADMAP.md` y `docs/technical/LOG_MAESTRO_NUEVA_ETERNIA.md` (`Fases 1–101`) se preservan como hitos internos de desarrollo (*ISO/IEC 12207*), consolidándose aquí en líneas base reales de producto desde `v1.0.0` hasta `v1.2.2`.

---

## [1.2.2] - 2026-10-31

### Added
- **Modal "Acerca del Oráculo & Novedades" (`AboutModal.tsx`):** Vista perezosa en Configuración con ficha de identidad SemVer, tarjeta heroica de novedades para usuarios (`changelog.user.json`), acordeón histórico de versiones y puente directo al inspector de arquitectura para administradores.
- **Píldora de versión interactiva en cabecera (`Config.tsx`):** Acceso rápido `v1.2.2 · Novedades` con indicador visual de nueva versión y coste `0 KB` en reposo mediante constante de compilación `__APP_VERSION__` en Vite.
- **Casos de uso reales en Grafo TecnoRed (`AppArchitectureGraph.tsx`):** Renderizado interactivo de `selectedNode.useCases` en el inspector lateral con acento cromático ontológico y cierre accesible por teclado (`Escape`).
- **Doble capa de Changelog:** Creación de este `CHANGELOG.md` técnico y del manifiesto `frontend/src/config/changelog.user.json` orientado al coleccionista.

### Changed
- **Code-splitting ligero en Configuración (`Config.tsx`):** Conversión a `React.lazy()` + `<Suspense>` de las pestañas y modales secundarios de administración (`ScrapersTab`, `InventoryTab`, `UsersTab`, `LoreTab`, `TcgConfigTab`, `WallapopImporter`, `WallapopNexusBridge` y modales de gestión/calibración), reduciendo el bundle descargado al entrar en Ajustes.
- **Aislamiento de la vista `Ajustes` para el rol `Guardián` (`SystemTab.tsx`):** Ocultación de controles administrativos globales que devolvían `403` o exponían infraestructura interna (*Filtro Global Telegram*, *Descarga ZIP WebP*, *Parámetros `.env`* y *Grafo TecnoRed*), y supresión de llamadas de red administrativas innecesarias en `fetchData()`.
- **Alineación integral de versión `1.2.2`:** Unificación en `frontend/package.json`, `pyproject.toml`, `/api/health`, `stack.config.json` y documentación maestra.

---

## [1.2.1] - 2026-10-31

### Added
- **Grafo Topológico TecnoRed v2.0 (`AppArchitectureGraph.tsx` & `stack.config.json`):** Motor Canvas 2D a 60 FPS con modo dual (*Mapa Topológico* y *Rutas de Flujo*), sondas pasivas de salud (`/api/health` y Cache Storage) y navegación entre nodos conectados *(Fase 101)*.

### Changed
- **Optimización global de rendimiento full-stack:** Activación de modo `WAL` e índices compuestos en SQLite/Alembic, delegación a threadpool en rutas síncronas de FastAPI, precarga masiva sin consultas `N+1` en colecciones, concurrencia de doble semáforo en `ScrapingPipeline` y renderizado a 60 FPS en `FoilTiltCard` y caché LRU de `MOTUImage` *(Fase 100)*.

### Fixed
- **Compatibilidad CI con Ubuntu 26.04 LTS (`scrapers.yml`):** Actualización de `playwright` a `1.64.1` (`>=1.61.0`), instalación con `--with-deps chromium` y blindaje del paso `xvfb` + Cloudflare WARP con fallback APT a `noble`.
- **Privacidad en Modo Incógnito y Precios Manuales:** Eliminación de fugas de valor real en hover sobre casillas `.blur-manual-price`, ROI y métricas financieras.

---

## [1.2.0] - 2026-09-15

### Added
- **Motor Cuantitativo EMI e Inteligencia P2P:** Índice bursátil de Eternia con media móvil exponencial (Half-Life 30d), filtro IQR anti-outliers, *Pulso de Liquidez P2P* (detección de stock estancado `>45d`), *Último Bastión Retail* y optimizador multi-tienda *Matrix Cart* con amortización de envío *(Fases 96–98)*.
- **Grimorio Living Lore & Estudio de Cromos TCG (Gen 3):** Cosecha idempotente de biografías y estadísticas de combate sin consumo de tokens, editor por facciones y visor perezoso de cartas holográficas *Secret Lair* con marcos configurables *(Fases 88–99)*.

---

## [1.1.0] - 2026-08-18

### Added
- **Centinela Autónomo 24/7 de Vinted y Cazador Cloud:** Vigilancia continua con cadencia anti-ban, deduplicación diaria de chollos y control interactivo desde Telegram (`/centinela`, `/caza`) junto con panel FinOps de cuota mensual de GitHub Actions *(Fases 76–86)*.
- **Nexus Local Bridge & Extensión Multitienda:** Cola híbrida `wallapop_jobs` en Supabase con auto-relevo hacia IP residencial (`nexus_local_worker.py`) e importador directo desde extensión Chrome para Wallapop y Vinted.
- **Escudo Soberano de Dispositivos y Guardián SSL:** Autorización de nuevos dispositivos en 1 clic por Telegram (`X-Device-ID`), renovación automatizada y diagnóstico en vivo de certificados Let's Encrypt, y compactación histórica mensual FinOps (`product_monthly_stats`).

---

## [1.0.0] - 2026-06-30

### Added
- **Plataforma Nuclear Full-Stack:** Interfaz SPA en React 19 + Vite + Tailwind CSS 4 + TanStack Query conectada a FastAPI, SQLAlchemy 2.0, SQLite local y Supabase PostgreSQL con políticas Row-Level Security (RLS) *(Fases 1–75)*.
- **La Fortaleza, Catálogo Dual y Santuario Público:** Gestión patrimonial de colecciones *Nueva Eternia* y *Eternia Vintage*, soporte MOC/Loose, exportación a Excel Maestro (`lista_MOTU.xlsx`) y Bóveda SQLite, y escaparate público compartible sin datos financieros.
- **El Purgatorio, SmartMatcher y Malla de Scrapers:** Flujo *Purgatory-First* con emparejamiento difuso y veto semántico, cálculo de *Landed Price* territorial (envío + aduanas/IVA) y extracción automatizada multi-tienda europea y estadounidense.

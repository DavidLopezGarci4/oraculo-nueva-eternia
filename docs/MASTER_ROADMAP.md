# 🔮 MASTER ROADMAP: El Oráculo de Nueva Eternia

Este documento unifica la visión estratégica y el plan técnico de ejecución en una sola fuente de verdad. El objetivo es transformar el actual "motu-tracker" en una aplicación premium, escalable y resiliente.

---

## 🏗️ Visión Arquitectónica y Datos

### Estado no Agéntico (Puerta Abierta)

La aplicación operará de forma determinista y bajo control directo. Sin embargo, se diseña bajo un paradigma modular **"Plug & Play"** para permitir la integración futura de agentes inteligentes.

### Arquitectura "Plug & Play" Agéntica

Aunque la aplicación es **no agéntica** hoy, se diseña como un sistema modular que permita conectar un "Cerebro Agéntico" en el futuro.

- **Puntos de Integración**:
  - *Matching Inteligente*: Resolución de ambigüedades en `PendingMatch` mediante LLMs.
  - *Estrategia de Scraping*: Ajuste dinámico de selectores y tiempos de espera ante bloqueos.
  - *Vigilancia Predictiva*: Predicción de bajadas de precio basadas en históricos.
- **Regla de Oro**: Cada hito validado será documentado aquí. No se pasará a la siguiente fase sin una validación satisfactoria (funcional y de rendimiento) respaldada por logs de auditoría.
- **Test-Driven Development (TDD)**: No se escribirá lógica sin su correspondiente script de test. Cada componente (scrapers, sync, API) debe contar con pruebas unitarias e integración que verifiquen su comportamiento antes de la fusión.
- **Visión Modular Expandible**: El sistema se diseña para alojar módulos satélite (Sentinel, Finance, Vision) sin alterar el núcleo.

### Estrategia Híbrida de Datos

1. **SQLite (Local)**: Buffer de alta velocidad para scrapers y trabajo offline.
2. **Supabase/PostgreSQL (Cloud)**: Estado global, multi-usuario y fuente de verdad definitiva.
3. **Sincronización (Broker API + Queue)**: FastAPI actúa como mediador con una **Cola de Tareas en Segundo Plano**. El usuario nunca espera a la nube; el cambio se confirma localmente al instante y se sincroniza "fuera de banda".

### Imágenes (Cero Coste & Nube)

- **Hotlinking**: Para imágenes de tiendas (0 bytes storage).
- **Cloudinary**: Para la colección personal (capa gratuita).

---

## 🗺️ Fases de Ejecución

### Fase 0: Consolidación del Catálogo y Migración Segura

* **Origen**: `actionfigure411.com` vía `src/collectors/personal_collection.py`.
- **Identidad Multivariante & Capa de Mapeo**:
  - Para manejar cambios de nombre o versiones (ej. Michelangelo V2), se usará una **Capa de Alias**.
  - Cada URL de scraping se vincula a un `Product ID` interno. Si el nombre del item cambia en el catálogo, el mapeo persiste porque apunta al ID, no al nombre.
  - La imagen (`Image Hash`) servirá como validador visual independiente frente a colisiones de nombres **y como base para el futuro Buscador Óptico**.
- **Preservación- [x] **Phase 44: Wallapop Playwright Nexus & Hybrid Expansion (06/02/2026)**:
  - Extracción masiva (150+ items) mediante bypass 403 y expansión de DOM (Click & Scroll).

- [x] **Phase 25: API Security & Ghost Sync (20/01/2026)**:
  - Refactorización del motor de persistencia y seguridad API.
- [x] **Phase 26: Nexo Maestro Robustness & Cloud Sync** ✅
- [x] **Phase 27: Supabase Security Hardening (RLS)** ✅
  - [x] Activación de Row Level Security en 15 tablas públicas.
  - [x] Aislamiento de la vía pública de acceso a datos.
- [x] **Phase 28: Cloud Sync & Catalog Resurrect** ✅
  - [x] Unificación de API Keys en Purgatorio para desbloqueo de búfer.
  - [x] Refactorización de GitHub Actions para soporte de Storage Secrets.
  - [x] Actualización automática de URLs públicas en la base de datos.
  - **Robustez**: Corrección de puntería en el scraper de catálogo maestro.
  - **Fase 28: Sync Engine Resurrect** ✅ - Reparación del búfer de sincronización estancado y automatización total de imágenes en CI/CD. (Completado).
- **Phase 29: Log Diagnostics & International Visibility** (75 logs limit + Scraper robust loop) ✅
- **Phase 30: Scraper & Nexus Robustness** (BBTS Block Evasion + Nexus Stability + Unified Migrations) ✅
- **Phase 31: Intelligent Hierarchy & Tactical Management (27/01/2026)** ✅
  - [x] Exclusión Total: Los ítems poseídos desaparecen de Nueva Eternia para focus absoluto.
  - [x] Optimal Purchase Window: Clasificación dinámica por edad (ID) y comportamiento de mercado (Suelo/Riesgo).
  - [x] UI Tactical: Badges de edad cromáticos y corrección de capas (z-index).
  - Recuperación de visibilidad de scrapers internacionales y blindaje del motor de escaneo diario. (Completado).
  - **Cloud Architecture**: Sincronización automática de imágenes locales a Supabase Storage.
  - **Acceso Universal**: Transición a URLs públicas para visualización cross-device sin PC encendido.
  - **Importación & De-duplicación**: Se descargarán las tablas de Supabase (`users`, `roles`, `collection_items`). Se aplicará una lógica de colisión para evitar duplicados y la creación de items "fantasma".
  - **Logs de Auditoría**: Cada decisión de fusión o descarte de datos de Supabase quedará registrada en un log de migración para trazabilidad total.
  - El nuevo catálogo se integrará con estos datos existentes para que ningún usuario pierda su configuración o inventario validado.

* **Acción**: Unificar `lista_MOTU.xlsx`, auditorías locales y tablas de Supabase en el nuevo esquema relacional, validado mediante tests de integridad de datos.

### Fase 1: Reestructuración Modular (Clean Architecture)

* **Tecnologías & Herramientas**:
  - **Lenguajes**: Python 3.10+ (Tipado estricto con `mypy`/`pyright`).
  - **Validación**: **Pydantic V2** para DTOs y modelos de dominio.
  - **Persistencia**: **SQLAlchemy 2.0** (estilo moderno) + **Alembic** para migraciones (control de versiones de la DB).
  - **Calidad**: **Ruff** (linting ultra-rápido) y **Pytest** (suite de tests unitarios).
- **Estrategias de Diseño**:
  - **Patrón Repositorio**: Desacoplar la lógica de negocio de la base de datos (SQLite/Supabase).
  - **Arquitectura de Cebolla (Onion)**: Las dependencias solo apuntan hacia adentro (Dominio -> Aplicación -> Infraestructura).
  - **Inyección de Dependencias**: Facilitar el testing mediante el paso de servicios e interfaces.

- [x] **Phase 27: Supabase RLS Hardening (21/01/2026)**:
  - Blindaje de 15 tablas críticas mediante políticas RLS para cerrar la puerta pública de Supabase.
- [x] **Phase 28: Sync Buffer & Cloud Visibility Fix (21/01/2026)**:
  - **Sync Hub**: Reparación de la API Key en el Purgatorio (desbloqueo del búfer de 153 acciones).
  - **Visibility**: Automatización de URLs públicas en el Nexo Maestro para visualización cross-device.
  - **CI/CD Robustness**: Inyección de Supabase Storage Secrets en GitHub Actions.

* **Estructura `src/`**: Separación en `core` (config), `domain` (entidades), `application` (casos de uso), `infrastructure` (DB/Scrapers) y `interfaces` (Web/API).
- **Hito de Consistencia**: Refactorización total de imports y eliminación de acoplamientos circulares.

### Fase 2: El Bastión de Datos y Guardianía (Sentinel) ✅

* **Auditoría**: Implementar `OfferHistory` para registrar cada movimiento de precio.
- **Módulo Centinela (NUEVO)**: Lógica de activación de alertas proactivas. Si un precio baja del umbral definido, se genera un evento de notificación listo para consumo.
- **Purgatorio (`PendingMatch`)**: Los scrapers externos depositan hallazgos aquí; solo pasan al catálogo principal tras validación manual o matching de alta confianza.
- **Refinado de Precisión Estratégica**:
  - **Pesos Dinámicos (IDF) ✅**: Identidad y Serie se calculan automáticamente basándose en la rareza en el catálogo matriz.
  - **Normalización de Sinónimos ✅**: Soporte para `TMNT`, `MOTU`, `Origins`, etc.
  - **Leyes de Hierro & Veto ABSOLUTO ✅**: El sistema inteligente (Python) bloquea falsos positivos de motores rápidos (Rust) si hay conflicto de identidad.
  - **Gestión de Identidades (Refinado de Precisión) ✅**: Integración de Subcategoría en el cálculo de pesos para diferenciar líneas de juguetes.
  - **Buscador de Identidades Manifiesto (NUEVO)**: UI para ver qué palabras el sistema considera críticas y permitir ajustes manuales.
  - **Refuerzo por Descarte**: Si un admin descarta una sugerencia, el sistema "aprende" a bajar el peso de esa relación específica.

### Fase 3: Transactional API Broker (FastAPI) & Out-of-Band Sync ✅

* **Estrategia "Out-of-Band" (No Bloqueante) ✅**:
  - **App Update Flow ✅**: Cuando el usuario modifica un item, la app escribe en una tabla de `SyncQueue` (SQLite) y devuelve éxito al instante.
  - **Worker Silencioso ✅**: Un proceso independiente (Worker) lee la `SyncQueue` y negocia con el **FastAPI Broker** la subida a Supabase sin afectar la navegación del usuario.
  - **Reintentos Inteligentes ✅**: Si no hay conexión, el Worker reintenta automáticamente en segundo plano.
- **FastAPI como Broker & Validador ✅**:
  - Centraliza la lógica de negocio y validación Pydantic para asegurar que lo que llega a la nube sea perfecto.
  - **Seguridad de Frontera ✅**: Implementado sistema de `X-API-KEY` obligatorio para sincronización.
  - **Stack Moderno ✅**: Migrado sistema de comunicación a **HTTTPX** para mayor performance y compatibilidad asíncrona.
  - **Operación Rescate ✅**: Backup masivo de datos antiguos (Supabase -> JSON) para preservar la colección de David y la blacklist antes del cambio de esquema.
  - Proporciona endpoints de salud para monitorear el estado de la sincronización.
- **Infraestructura Cloud (PENDIENTE)**:
  - Configurar **GitHub Actions** para invocar los endpoints de la API de sincronización.
  - Secretos gestionados exclusivamente en el entorno de la API.
- **Canales de Notificación**: Integración de tokens para Telegram/Discord en la configuración cloud.

### Fase 4: Revolución UX (Frontend Evolution) 🚀

* **Desacoplamiento Total**: Con el backend ya robustecido en la Fase 3, la Fase 4 se centra 100% en la experiencia de cliente.
- **Frontend Stack ✅**:
  - **Vite 6 + React 19 + TypeScript**: Base de alto rendimiento.
  - **Tailwind CSS 4.0 ✅**: Motor de estilos de última generación (sin archivos de config pesados).
  - **TanStack Query (React Query)**: Gestión de estado asíncrono y caché para la API.
  - **Framer Motion**: Micro-animaciones para una sensación premium.
- **Hitos de Interfaz**:
  - **Diseño Glassmorphism**: Estética moderna con transparencias y desenfoques (MOTU-Dark).
  - **Componentes Atómicos**: Botones, Modales y Cards unificados para toda la app.
  - **SPA Navigation**: Cambio entre Catálogo, Purgatorio y Centinela instantáneo.
- **Consumo de API**: El frontend consume exclusivamente la API de FastAPI desarrollada en la fase anterior, garantizando fluidez y velocidad de respuesta instantánea.

### Fase 5: Refinamiento Táctico (La Gran Purificación) ✅

* **Reingeniería de Calidad de Datos**:
  - **SmartMatch Revertido ✅**: Capacidad de deshacer masivamente vínculos automáticos erróneos.
  - **SmartMatch 2.0 ✅**: Umbral elevado al 75%. Lo dudoso se deriva a revisión manual.
  - **Evolución de Purgatorio ✅**: Los items pendientes actualizan sus precios automáticamente tras cada escaneo si hay cambios.
- **Verdad del Tablero (Real-Time)**:
  - Desacoplamiento de métricas históricas. Ahora el Dashboard refleja el estado vivo de la base de datos `OfferModel`.
  - Sincronización instantánea de contadores tras purificación o vinculación.
- **Experiencia de Catálogo**:
  - **Market Intelligence UI**: Indicadores visuales ("Live" badge) para productos con ofertas activas.

### Fase 11: Expansión Continental y Dinamización ✅

* **Incursión Europea**: Integración de 14 scrapers activos cubriendo España, Alemania e Italia.
- **Bypass de IVA (OSS)**: Lógica específica para detectar y normalizar precios internacionales.
- **Interfaz del Arquitecto**: UI del Purgatorio 100% dinámica, eliminando el hardcode y permitiendo escalabilidad infinita de fuentes.
- **Atomicidad Transaccional**: Blindaje de base de datos contra duplicación de URLs y colisiones de red.
- **Heartbeat Sentinel**: Implementación de `simulated_connection.py` para monitoreo de salud de la red.

### Fase 12: Inteligencia del Dato y Refinamiento UX ✅

* **Patrones de Conexión SKU/EAN**: Investigación y mapeo de identificadores Mattel (SKU, ASIN, UPC) para automatizar el matching entre webs.
- **Métricas "ActionFigure411 Style"**: Implementación de MSRP, Revalorización (%), Precio Medio Móvil y Volumen de ventas.
- **Scraper Modernización**: Refactorización de `daily_scan.py` y scrapers clave (BBTS, Vendilo, DeToyboys) para máxima resiliencia.
- **Optimización de Legibilidad**: Rediseño de la rejilla de scrapers para evitar el colapso visual, priorizando la lectura horizontal y etiquetas claras.
- **Auditoría de Purgatorio**: Resolución de inactividad de botones mediante lógica `onSettled` y blindaje de lista negra en backend.

### Fase 12.5: Consolidación de Identidad y Auditoría de Reliquias ✅

* **Rebranding "Nueva Eternia"**: Unificación de la nomenclatura en Catálogo, Sidebar y estados de carga.
- **Auditoría Total de Catálogo**: Confirmación de 297 Figure IDs únicos, logrando paridad del 100% con la fuente ActionFigure411.
- **Bitácora de Alta Precisión**: Mejora de la UI de logs para mostrar Fecha, Hora y Tiempo Relativo de cada incursión.
- **Validación de Automatización**: Confirmación de 2 ciclos diarios de scraping vía GitHub Actions para las 11 fuentes activas.

### Fase 6: Estrategia de Valor y Futuro (Innovación)

* **Estimador de Valor (Financial)**: Cálculo automático del valor de la colección basado en precios históricos y estado del item.
- **Buscador Óptico (Future Vision)**: Identificación de figuras mediante carga de fotos (comparativa de hashes).
- **Exportación de Seguridad**: Generación de reportes PDF detallados para seguros y auditorías personales.
- **PROJECT_CODEX.md**: Guía incremental de sinergia técnica y arquitectura. ✅

---

### Fase 16: Segregación P2P y "Teoría de la Cuarentena" ✅

* **Segregación lógica**: `Retail` vs `Peer-to-Peer` en `OfferModel`.
- **Blindaje patrimonial**: P2P excluido de métricas de colección.
- **Radar de Oportunidades**: Detección de gangas por debajo del Percentil 25.

### Fase 13: El Pabellón de Subastas (Wallapop & eBay) [/]

* **Segregación de ADN**: Categorización de ofertas en `Retail` vs `Auction` para preservar la pureza de precios de tienda. ✅
- **Identidad Espejo**: Visualización dedicada para subastas utilizando las IDs y nomenclaturas maestras de Nueva Eternia. [/]
- **Filtros de Oportunidad**: Sección para ítems que solo aparecen con ofertas asociadas desde el Purgatorio (Wallapop/eBay). [/]
- **Match de Mercado**: Integración total con el motor SmartMatch para unificar el catálogo global. [/]

### Fase 15: El Oráculo Logístico (Precisión de Compra) ✅

* **Identidad Geográfica**: Implementación de ubicación por usuario (`country_code`) para cálculos dinámicos.
- **Precio de Aterrizaje (Landed Price)**: Cálculo automático de: `(Precio + Envío) * IVA + Tasas Aduaneras`.
- **ROI de Realidad**: Ajuste de las métricas de inversión y revalorización basándose en el coste real de llegada a estantería.
- **Estrategias de Tienda**: Sistema flexible para manejar excepciones (ej: Tarifa plana de BBTS, envíos fijos de Fantasia Personajes).
- **Selector de Inteligencia**: UI en Configuración para cambiar la ubicación y recalcular todo el ecosistema al instante.

---

### Fase 17: El Centinela de Cross-Validation ✅

* **Detección de Anomalías**: Bloqueo automático de ofertas con desviación >40% del precio medio.
- **Integridad Visual**: Almacenamiento de `master_image_hash` para validación contra falsificaciones/bootlegs.
- **Gobernanza de Datos**: Sistema de bloqueo preventivo en Purgatorio y validación manual por el Arquitecto.

### Fase 18: El Motor de Inversión (DealScorer) ✅

* **Algoritmo Ponderado**: Cruce de MSRP, P25 y Wishlist para obtener el Opportunity Score (1-100). ✅
- **Alertas de Alta Prioridad**: Notificación "Compra Obligatoria" en Telegram para el "Alpha" del mercado. ✅
- **Integridad de Datos**: Persistencia del score en el flujo de SmartMatch y Purgatorio. ✅
- **Restauración Cloud**: Sincronización masiva de inteligencia hacia Supabase. ✅

### Fase 19: Optimización de Rendimiento & UX Core ✅

* **Eliminación de Cuellos de Botella N+1**: Refactorización del motor financiero para cargas masivas de datos y pre-caché logístico. ✅
- **Robustez del Daily Scan**: Desacoplamiento de CLIs y manejo de flags dinámicos para evitar fallos en CI/CD. ✅
- **Refactorización del Héroe**: Evolución del selector de usuarios hacia un sistema de recarga atómica y fiable. ✅
- **Búsqueda Dual en Purgatorio**: Independencia total entre filtros de lista e integración con el Gran Catálogo. ✅
- **Ruteo Nativo P2P**: Integración de Wallapop directamente hacia El Pabellón mediante tipado de ADN dinámico. ✅

### Fase 21: Blindaje Operativo & Diagnóstico ✅

* **Estabilidad de Logging**: Registro global del nivel `SUCCESS` para evitar errores de atributo. ✅
- **Serialización Robusta**: Implementación de `DateTimeEncoder` para backups JSON resilientes. ✅
- **Diagnóstico CI/CD**: Sistema de logs de arranque para verificación de secretos de Telegram. ✅

### Fase 21.5: Purgatory-First Policy (Calidad Total) ✅

* **Filtrado Humano Proactivo**: Toda nueva extracción fluye directamente al Purgatorio, eliminando falsos positivos automáticos. ✅
- **Sanación Automática**: Capacidad de revertir retroactivamente emparejamientos defectuosos. ✅

### Fase 22: Unlink Control (Bastión de Justicia v2) ✅

* **Reversión Instantánea**: Botón de desvinculación en Catálogo para erradicar capturas erróneas. ✅
- **Protección de Futuro**: Limpieza de alias para evitar que el SmartMatch repita errores de vinculación conocidos. ✅

### Fase 23: Blindaje de Poderes Administrativos ✅

* **Confidencialidad de Acciones**: Desplazamiento de herramientas críticas a la zona de Configuración. ✅
- **Doble Autorización**: Sistema de confirmación en dos etapas para evitar el reset accidental del ecosistema. ✅

### Fase 24: Dashboard Mastery (Control Ubicuo) ✅

* **Gestión en Tiempo Real**: Capacidad de corregir vinculaciones directamente desde las oportunidades del Tablero. ✅
- **Buscador Integrado**: Drawer de re-vinculación con búsqueda atómica para una corrección fluida. ✅

### Fase 25: API Security & Sync Engine ✅

* **Refuerzo de Seguridad**: Estandarización de `ORACULO_API_KEY` en todos los clientes frontend. ✅
- **Motor Ghost Sync**: Implementación de persistencia local para acciones offline o en espera de red. ✅

### Fase 26: Nexo Maestro Cloud ✅

* **Cloud Hosting**: Sincronización automática de imágenes de catálogo a Supabase Storage. ✅
- **Robustez de Catálogo**: Fix de desplazamiento de columnas en ActionFigure411. ✅

### Fase 27: Supabase Hardening ✅

* **RLS Activation**: Protección a nivel de fila en las 15 tablas públicas de la base de datos. ✅

### Fase 28: Sync Engine Resurrect ✅

* **Reparación de Búfer**: Unificación de llaves API y automatización de despliegue de imágenes en CI/CD. ✅

### Fase 29: Log Diagnostics & International Visibility ✅

* **Expansión de Logs**: Aumento del límite de auditoría a 75 registros para visibilidad semanal. ✅
- **Resiliencia del Ciclo**: Blindaje de `daily_scan.py` contra fallos de scrapers individuales. ✅

### Fase 30: Scraper & Nexus Robustness ✅

* **Evasión de Bloqueos**: Fix de paginación en BBTS y timeouts en ActionFigure411. ✅
- **Migración Unificada**: Sincronización de esquemas locales y cloud en un solo paso. ✅

- [x] **Phase 43: Dashboard Role-Based Access** ✅
  - [x] Restricción de secciones administrativas (Actividad y Conquistas) a usuarios Admin.
  - [x] Blindaje de botones de gestión en Top Deals.
- [x] **Phase 44: Dashboard Restructuring & Docker Fixes** ✅
  - [x] Reordenación de secciones para Guardianes: Oportunidades -> Griales -> Potencial.
  - [x] Implementación de herramientas operativas exclusivas para Admin.
  - [x] Resolución de errores de resolución de host en Nginx y lints de TS.
  - [x] Resolución de fallo de build Docker (TypeScript unused vars en Config.tsx).
- [x] **Phase 45: Protocolo de Ascenso Dinámico & Hero Management** ✅
  - [x] Lifting state del usuario a `App.tsx` para reactividad global.
  - [x] Implementación de endpoints `/api/admin/users` para gestión de personal.
- [x] **Phase 51: Hardening de Seguridad & Redirección Reactiva (01/02/2026)** ✅
  - [x] Remediación de filtración de secretos (Zero-Leak Policy).
  - [x] Limpieza profunda de artefactos de diagnóstico (.html, .png).
  - [x] Implementación de Redirección Automática por Rol en el cambio de identidad.
  - [x] Fortificación de `.gitignore` y `.dockerignore`.
- [x] **Phase 54: Scraper Repair & P2P Parity (07/02/2026)**:
  - [x] **Pixelatoy Resurrect**: Reparación del scraper (0 a 120 items) mediante categoría directa y selectores robustos.
  - [x] **P2P Nexus**: Preservación de metadatos de subastas en el adapter y reparación de 539 registros en DB.
  - [x] **Logística Tradeinn**: Fijado coste de envío a 2.99€ y limpieza de lógica `tradeinn_volume`.
- [x] **Phase 55: Legado Restoration & Advanced Valuation (08/02/2026)**:
  - [x] **Restauración del Botón (i)**: Reconexión del flujo de detalles privados del item.
  - [x] **Motor de Multiplicadores**: Implementación de lógica de valoración basada en estado (MOC 1.0x, NEW 0.75x, LOOSE 0.5x).
  - [x] **Graduación "Shelf Wear"**: Introducción del Grado 1-10 para ajustes de precisión financiera (4% de impacto por punto de grado).
  - [x] **Aislamiento de Legado**: Blindaje de datos privados en `CollectionItemModel` contra purgas de catálogo.

### Fase 31: Debugging Sync Buffer Stagnation ✅

* **Motor Non-Blocking**: Sincronización resiliente que no se detiene ante fallos puntuales. ✅
- **Sala de Autopsia Forense**: Interfaz de inspección de fallos y manual intervention. ✅
- **Rescate de Datos**: Implementación de metadatos (URL/Name) en acciones de búfer y botón de "Reintentar Todo". ✅
- **Idempotencia Backend**: Refuerzo de esquemas de base de datos (columna `reason`) y manejo de conflictos 409. ✅

### Fase 32: Expanding Manual Match Results ✅

* **Visibilidad Extendida**: Ampliación del límite de búsqueda manual de 10 a 20 resultados simultáneos. ✅
- **Optimización UI**: Reajuste de la altura del contenedor de búsqueda para mejorar el scroll en figuras con múltiples variantes. ✅

### Fase 33: Decommissioning Scrapers ✅

* **Limpieza de Motores**: Eliminación de scrapers obsoletos (MotuClassicsDE, VendiloshopIT) para optimizar recursos. ✅
- **Unificación Fantasía**: Eliminación del scraper duplicado "Fantasia" y consolidación en "Fantasia Personajes" para evitar ruido visual. ✅
- **Santuario de Datos**: Preservación de ofertas históricas vinculadas mientras se limpian las bitácoras dinámicas. ✅
- **Optimización UI**: El panel de incursión individual ahora está unificado y libre de duplicidades. ✅

### Fase 36: Tradeinn Hyper-Resilience & Multi-Shop Incursion ✅

* **Target**: <www.tradeinn.com> / kidinn.com.
- **Estrategia Sirius T3**:
  - **Phase A**: Acceso directo legitimado mediante sesión previa y aceptación de cookies.
  - **Phase B**: Fallback a subdominio Kidinn para eludir redirecciones agresivas.
  - **Phase C**: Simulación humana profunda (escritura letra a letra, limpieza de buffer y click en lupa interactivo).
- **Algolia Synchro**: Sincronización con el contenedor `#js-content-buscador_ol` para carga dinámica.
- **DNA Identification**: Extracción dinámica de la sub-tienda (Tradeinn, Kidinn, Diveinn, etc.) basada en la URL. ✅

---

### Phase 37: Orquestación Táctica y Búsqueda Precisa (31/01/2026)

* **Hitos**:
  - **Custom Query Support**: Evolución de la API para permitir términos de búsqueda personalizados desde el disparador manual. ✅
  - **MOTU Search Accuracy**: Implementación de búsquedas profundas ("masters of the universe origins") para Tradeinn, eliminando el ruido de resultados genéricos. ✅
  - **Bridge Logístico**: Sincronización en tiempo real entre el motor de scraping y la Tactical Console. ✅

- [x] **Phase 60: Segregación Vintage y Flujo de Naming en Purgatorio (26/05/2026)**
  - [x] **Segregación del Legado**: Catálogos y colecciones divididas mediante parámetro `is_vintage` en la API, asegurando aislamiento absoluto con Origins (Nueva Eternia).
  - [x] **Nueva Pestaña Eternia**: Vista del catálogo vintage independiente con evolución de precios y mejores ofertas.
  - [x] **Mi Fortaleza Vintage**: Colección y lista de deseos exclusivas para piezas vintage poseídas o deseadas.
  - [x] **Asignación con Nombre Limpio**: Diálogo interactivo en Purgatorio que permite seleccionar o escribir el nombre del muñeco vintage, autocompletando con los existentes y añadiendo la partícula ` Vintage` automáticamente.

---

### 🔮 Mejoras Futuras Sugeridas (Ojo de Grayskull)

* **Auto-Keyword Optimizer**: Motor que use la IA para expandir términos de búsqueda cortos a términos de alta fidelidad de coleccionista.
- **Anti-Bot Rotation v4**: Integración de rotación de proxies residenciales para incursiones de alto volumen.
- **Image Cross-Check**: Validación visual automática comparando miniaturas con la imagen maestra para evitar falsos positivos.

---

- [x] **Phase 38: Amazon.es Sirius A1 Armor & Expansion (01/02/2026)**
  - [x] Infiltración Sirius A1: Superación de bloqueos 503/CAPTCHA.
  - [x] Expansion Engine: Paginación táctica y scroll profundo (135+ ofertas).
  - [x] 3OX Unicode Shield: Resiliencia de caracteres.

- [x] **Phase 39: Incursion Log & Scraper Synchronization (01/02/2026)**
  - [x] Registro automático de motores en la API (13 scrapers operativos).
  - [x] Integración de `Tradeinn` en `daily_scan.py`.
  - [x] Unificación de nombres y visibilidad total en el Purgatorio.

- [x] **Phase 42: Price Intelligence (Shipping & Scores - 05/02/2026)**
  - [x] Implementación de recalculación de `opportunity_score` en flujos manuales.
  - [x] Mejora de precisión financiera en eBay.es (landed_price audit).
  - [x] Saneamiento masivo de scores en DB Cloud (122 deals recuperados).
  - [x] Confirmación de extracción de benchmarks Avg/MSRP desde ActionFigure411.

- [x] **Phase 56: Blindaje Operativo & Cancelación Cooperativa (15/02/2026)**
  - [x] Pool de conexiones BD (`pool_pre_ping`, `pool_recycle=1800`) contra desconexiones en incursiones largas.
  - [x] Cancelación cooperativa de scrapers con `threading.Event` y ejecución secuencial.
  - [x] Eliminación de usuarios (`DELETE /api/admin/users/{id}`) con protección admin.
  - [x] Diagnóstico SMTP en audit endpoint y mapeo Docker de variables de email.
  - [x] Optimización masiva de intervalos de refresco frontend (60s→5min).

- [x] **Phase 57: Refactorización Visual UX & Sistema de Búsqueda Flexible (28/02/2026)**
  - [x] Optimización de transiciones y rendimiento visual mediante reserva táctica del `PowerSwordLoader`.
  - [x] Migración masiva hacia spinners nativos ligeros (`RefreshCw` lucide-react).
  - [x] Escalabilidad del buscador global en Navbar (migración a `<textarea rows={2}>` para lectura Mobile-First).

---

- [x] **Phase 61: Segregación Estricta y Ordenación Inteligente del Purgatorio (27/05/2026)**
  - [x] **Clasificación Segregada Limpia**: Reclasificadas las figuras modernas duplicadas como `Skeletor (Vintage Sculpt)` y `Skeletor (200x)` a `is_vintage = False`, reubicando de forma atómica e instantánea las existencias de los usuarios a **Mi Fortaleza** (Moderno).
  - [x] **Blindaje del Motor de Purgatorio (Backend)**: Eliminado el bug de auto-promoción recursiva en la vinculación estándar moderna (`match_purgatory`). El backend ahora preserva de forma inmutable el estado `is_vintage` definido originalmente para el producto.
  - [x] **Aislamiento de Vincular en Nueva Eternia y Eternia Vintage**:
    * *Drawer Moderno:* Filtrado de búsquedas manuales y sugerencias del Oráculo para mostrar estrictamente productos con `!is_vintage`.
    * *Modal Vintage:* Implementación del algoritmo inteligente `vintageOracleSuggestions` que filtra por `is_vintage === true`, y fallback a listado puro de `/api/products?is_vintage=true`.
  - [x] **Ordenación Dinámica e Inteligente**: Modificado el catálogo de **Eternia Vintage** para ordenar los muñecos de forma descendente según el volumen de ofertas acumuladas en el Purgatorio esperando vinculación, con fallback ascendente por ID interno de base de datos para los empates.

- [x] **Phase 63: Miscelánea Vintage, Rediseño de Métricas y Manual de Usuario (03/06/2026)**
  - [x] **Sección de Miscelánea Vintage (Lotes/Varios)**: Añadido modelo `VintageMiscellaneousModel`, APIs de clasificación, listado y reversión en el backend, y pestaña dedicada en Eternia Vintage.
  - [x] **Rediseño de Métricas y Modal**: Symmetrizados los botones de acción del modal, removido el icono de báscula/diana del Grado de Conservación e integrada la guía interactiva desplegable de la escala C de conservación.
  - [x] **Cálculo de ROI Real y Valor Ajustado**: Tarjetas de la colección actualizadas para mostrar el valor ajustado y el ROI real con plusvalías/depreciaciones.
  - [x] **Manual de Usuario Interactivo**: Creada la carpeta `docs/manual_usuario/` con 8 guías de usuario estructuradas detallando cada apartado de la aplicación.

- [x] **Phase 64: Normalización de URLs, Filtro MOTU, Calibrador de Haces de Luz y Rebranding Temático Core (06/06/2026)**
  - [x] **Sección de Bazar del Oráculo (Lotes/Varios)**: Añadido modelo `VintageMiscellaneousModel`, APIs de clasificación, listado y reversión en el backend, y pestaña dedicada en Eternia Vintage.
  - [x] **Normalización Universal de URLs**: Unificada la lógica de normalización de URLs (`normalize_url`) en pipelines de importación manual y scrapers de fondo para evitar duplicados en el Purgatorio.
  - [x] **Filtro de Relevancia MOTU**: Implementado motor de exclusión de marcas no deseadas (Funko, Masterverse, Big Jim) con excepciones y reglas permisivas para crossovers oficiales de Origins (Transformers, Thundercats, Stranger Things, TMNT) que incluyan palabras clave de He-Man/MOTU, con soporte multilingüe.
  - [x] **Limpieza Proactiva del Purgatorio**: Auto-limpieza en segundo plano de ítems del Purgatorio que ya figuren en colecciones, ofertas o blacklist.
  - [x] **Calibrador Interactivo de Haces de Luz Vintage**: Rediseño del `PowerSwordLoader` para proyectar haces de luz mediante cálculos vectoriales basados en coordenadas personalizables en Configuración y almacenadas en `localStorage`, usando `bddg-heman.png` por defecto.
  - [x] **Rebranding Temático de Secciones e Iconos**: Renombradas las secciones principales a **Orbe de Grayskull** (antes Tablero, icono `Globe`), **Mercader de Eternos** (antes El Pabellón, icono `Store`) y **Bazar del Oráculo** (antes Miscelánea, icono `Sparkles`). Unificados los loaders y mensajes de carga con descripciones genéricas e inmersivas.
  - [x] **Compactación Visual de Tarjetas y Dock**: Reducción de gaps, padding y tamaños tipográficos en las tarjetas de Catálogo, Mi Fortaleza y Mercader de Eternos para maximizar la densidad de información y reducir el scroll vertical.
  - [x] **Contraste del Botón Añadir (+)**: Incremento del contraste visual (60% de opacidad de color temático en reposo, 100% en hover) para mejorar notablemente la descubribilidad del botón de añadir.
  - [x] **Cabeceras de Ordenación y Contadores Unificados**: Portada la interfaz premium de ordenación y contadores interactivos a Catálogo, Mi Fortaleza y Mercader de Eternos, con selector de orden y botón de dirección.
  - [x] **Saneamiento de Navbar**: Eliminado el botón inoperante de campana de notificaciones de la barra superior.

- [x] **Phase 65: Características Pareto 80/20 y Blindaje Wallapop (07/06/2026)**
  - [x] **Santuario Compartido (Showcase)**: Campo `is_public_showcase` en base de datos y UI con endpoint público seguro exento de campos financieros, con bypass de login en `/santuario/:username`.
  - [x] **Filtro Cruzado de Deseos**: Toggle "Solo Deseos" en Mercader de Eternos para cruzar ofertas de subastas con tu Lista de Deseos en tiempo real.
  - [x] **Regimientos de Completitud (Waves)**: Panel en Orbe de Grayskull que agrupa el catálogo por sub-categorías y muestra el progreso de adquisición de figuras.
  - [x] **Arsenal Analytics**: Gráfico circular Donut Chart con Recharts en Orbe de Grayskull detallando el estado de conservación (MOC, New, Loose) y estimación del valor de mercado ajustado.
  - [x] **Renovación Local de SSL**: Script `renew_ssl.sh` local para renovación segura con Docker Certbot y recarga de Nginx.
  - [x] **Scraper Wallapop Hardened**: Impersonación de TLS Chrome 120 mediante `curl_cffi` para peticiones API y fallback a Playwright persistente contra bloqueos WAF.
  - [x] **Calibración de Carga Skeletor**: Reemplazado el báculo de Havoc por la silueta de Skeletor Vintage y la espada real (`GlassmorphSword.png`), configurando coordenadas por defecto alineadas verticalmente (`125.0, 175.0` a `125.0, 10.0`), actualizando los textos de la interfaz a Empuñadura/Punta, y migrando el almacenamiento a `skeletor_sword_coords`.
  - [x] **Calibración de Carga He-Man Moderno**: Añadida calibración interactiva para la pantalla de carga predeterminada del app (`HemanGlassmorphSword.png`), guardando sus coordenadas personalizadas en `modern_sword_coords` para que los ajustes del calibrador se reflejen en producción de forma reactiva.

- [x] **Phase 66: Auditoría de Seguridad, DevSecOps y Gestión de Habilidades (08/06/2026)**
  - [x] **Instalación de Skills de Ciberseguridad**: Añadidas e integradas habilidades de automatización para SAST (`security-scanning-security-sast`), Secrets Hygiene (`secrets-and-logging-hygiene`), CI/CD secrets scanning (`implementing-secrets-scanning-in-ci-cd`), dependencias/SCA (`sca-trivy`) y OWASP (`owasp-security`).
  - [x] **Personalización de Skills para el Stack**:
    * *SAST*: Adaptado el módulo de ESLint al estilo Flat Config (`eslint.config.js`) del proyecto y añadidas reglas específicas de FastAPI/SQLAlchemy.
    * *Higiene de Logs*: Añadido el patrón de patcher de Loguru para redacción dinámica de secretos en consola y archivos de salida.
    * *OWASP*: Reemplazados los snippets de Express/Node por implementaciones idiomáticas de FastAPI (Python) para control de accesos e IDOR.
    * *SCA (Trivy)*: Añadidas instrucciones y llamadas adaptadas a Windows (winget/scoop/Docker) apuntando a `package-lock.json` y `requirements.txt`.
  - [x] **Ejecución y Remediación SAST (Bandit)**: Ejecutado el análisis de seguridad estático del backend y resueltas las vulnerabilidades identificadas de nivel Medio y Alto:
    * Hardened hashes (`usedforsecurity=False` en MD5/SHA1) en `smoke_test.py`, `notifier.py`, `scrape_run_report.py`, `personal_collection.py` y `personal_vintage_collection.py`.
    * Silenciadas de forma segura falsas alarmas de seguridad en `restore_vault.py` (SQL injection), `dvdstorespain_scraper.py` (XML entity attack) y `main.py` (binding de interfaces de red).
  - [x] **Bot Bidireccional de Telegram y Alertas Multi-usuario**:
    * *Comandos*: Implementado un bot asíncrono que procesa `/register` (Guardianes), `/purgatorio` (conteo de pendientes), `/buscar` (consulta rápida local) y comandos administrativos (`/status`, `/run`, `/stop`).
    * *Alertas Multi-usuario*: Añadida columna `telegram_chat_id` en la tabla `users`. El pipeline ahora cruza de forma reactiva las nuevas ofertas con las listas de deseos y alertas de precio (`PriceAlertModel`) de cada Guardián registrado.
    * *Auditoría de Telemetría*: Creado `data/telegram_telemetry.json` para almacenamiento atómico de eventos y redactada la guía de datos y utilidad en `docs/AUDITORIA_TELEGRAM.md`.


- [x] **Phase 67: Optimización Extrema, Bypass de proxies en Amazon y Trazabilidad Operativa (09/06/2026)**
  - [x] **Lazy Keep-Alive en Frontend**: Alternancia de pestañas persistente mediante la clase CSS `hidden` en `App.tsx` para evitar desmontar páginas, mejorando el TTI y preservando el scroll a 0ms.
  - [x] **Saneamiento del Campo de Inversión y Badges**: Inputs de precio vacíos por defecto con coerción segura a 0.0 y badge de carrito de compra para precios personalizados.
  - [x] **Amazon Bypass con Proxies Premium**: Configuración de `premium=true` y `country_code=es` en ScraperAPI para eludir el WAF de Amazon.es.
  - [x] **Saneamiento de SUPABASE_DATABASE_URL**: Strip automático de espacios y comillas en `database_cloud.py`.
  - [x] **Prevención de conflictos de Telegram**: Reducción a 1 worker de Uvicorn en docker-compose para evitar errores de colisión 409 webhook/listener.
  - [x] **CI Actions (Node 20)**: Actualización de workflows de GitHub Actions para silenciar advertencias de obsolescencia.

- [x] **Phase 68: Caché Local de Imágenes y Fallback Híbrido (09/06/2026)**
  - [x] **FastAPI Static Mount**: Montaje de StaticFiles en `/api/static/images` apuntando a `data/image_cache/` para servir imágenes locales de figuras.
  - [x] **APIs de Descarga**: Implementados endpoints de descarga en lote, status de progreso en tiempo real y cancelación en `vault.py`.
  - [x] **Componente React MOTUImage**: Creado componente con lógica de fallback automático. Intenta cargar del cache local de imágenes si está habilitado en localStorage (`use_local_images`), y recurre al hotlink remoto original en caso de fallo o error 404.
  - [x] **Integración en Configuración**: Tarjeta de ajustes en Configuración con toggle de habilitación de imágenes locales y barra interactiva de progreso de descarga con opción de cancelación.
  - [x] **Etiquetas de Imagen Actualizadas**: Swappeados los elementos `<img>` tradicionales por `<MOTUImage>` en Showcase, Collection, Catalog, Vintage y Dashboard.

- [x] **Phase 69: Apertura Controlada de Ajustes y Excel Bridge Selectivo (09/06/2026)**
  - [x] **Acceso Democrático a Ajustes**: Modificado `Sidebar.tsx` para permitir el acceso a Configuración a los Guardianes.
  - [x] **Excel Bridge Seguro**: Restringido el panel de Excel Bridge en `Config.tsx` a administradores (`isAdmin`), ocultándolo para los Guardianes.
  - [x] **Preservación de Autonomía de Guardianes**: Los Guardianes mantienen el control activo de Ubicación Geográfica, Santuario Público y Caché de Imágenes Local.

- [x] **Phase 70: Caché en el Navegador (Cache API) y Rutas de Registro en Base de Datos (09/06/2026)**
  - [x] **Persistencia de Rutas**: Conexión del formulario de "Caché de Imágenes Local" para registrar las rutas del PC (`pc_image_path`) y del móvil (`mobile_image_path`) de forma personal en base de datos.
  - [x] **Cache API en Navegador**: Migración a caché nativa en navegador (`motu-image-cache`) para almacenamiento de imágenes local 100% independiente en cliente.
  - [x] **Descargador Reactivo**: Descargador de imágenes en lote del lado del cliente con barra de progreso, conteo exacto y soporte de cancelación.
  - [x] **Auto-caching en Caliente**: Carga en caché automática en tiempo real de cualquier nueva imagen renderizada en las vistas principales.

- [x] **Phase 71: Fusión Divina de Reliquias en el Catálogo (09/06/2026)**
  - [x] **Interfaz de Fusión**: Añadido botón de fusión en los controles administrativos de la ficha de detalle de producto en `Catalog.tsx`.
  - [x] **Buscador y Selección**: Buscador interactivo integrado con autocompletado en el cliente para seleccionar el producto destino para la absorción de datos.
  - [x] **Sincronización de Base de Datos**: Integración con el endpoint de fusión divina del backend para traspasar ofertas y capturas de Fortaleza de forma atómica antes de eliminar el registro duplicado.

- [x] **Phase 72: Bypass de Amazon, Purgatorio Asíncrono y Resalto de Ofertas (20/06/2026)**
  - [x] **Bypass de Amazon.es**: Implementado renderizado de Javascript (`render=true`) en ScraperAPI para peticiones en la nube y corregido el falso positivo de CAPTCHA que bloqueaba búsquedas de figuras de tipo "Robot" (Roboto, Multi-Bot).
  - [x] **Asignación Asíncrona (`BackgroundTasks`)**: Migrados los endpoints de emparejamiento manual y descarte en el Purgatorio a procesamiento en segundo plano nativo en FastAPI, devolviendo éxito inmediato (0ms).
  - [x] **Escudo de Consistencia (`PROCESSING_IDS`)**: Incorporada exclusión temporal en memoria para evitar el retorno de ítems en proceso de escritura, eliminando parpadeos y race conditions en el refresco del cliente.
  - [x] **Resalto de Ofertas en Catálogo**: Incrementado el brillo de borde y sombra de acento en tarjetas de figura del catálogo que posean ofertas activas (celeste para Moderno, ámbar para Vintage), manteniendo la vista limpia sin añadir badges adicionales.
  - [x] **Filtro de Tránsito Experimental**: Incorporado interruptor selector "On/Off" en el Purgatorio para alternar el filtrado de ofertas según tipo de origen (Retail vs P2P).

- [x] **Phase 73: Pestaña de Deseos y Sincronización de Lista de Deseos en Catálogos (21/06/2026)**
  - [x] **Pestaña en Catálogos**: Añadida una pestaña dedicada "Lista de Deseos" en la sub-navegación del Catálogo Maestro (`Catalog.tsx`), tanto para la versión moderna (Nueva Eternia) como para la retro (Eternia Vintage).
  - [x] **Badge de Conteo Reactivo**: Implementado un badge dinámico con el total de deseos (`totalWish`) junto al título de la pestaña, adaptado al color temático de la versión (azul vs ámbar).
  - [x] **Filtrado Integrado (`sortedProducts`)**: Configurado el hook de filtrado para mostrar únicamente productos deseados (`isWished(product.id) === true`) al estar en el modo de deseos.
  - [x] **Experiencia de Usuario Inmersiva**: Diseñado un contenedor de estado vacío premium con icono de estrella y guías explicativas para listas de deseos vacías, y adaptados los iconos y contadores del encabezado principal.
  - [x] **Sincronización Bidireccional de Caché**: Conectado el flujo de mutación `toggleMutation` para invalidar reactivamente las claves `collection` y `dashboard-stats`, asegurando que cualquier cambio de deseos o capturas desde el Catálogo o la Fortaleza se propague en tiempo real a todas las vistas.

- [x] **Phase 74: Integración de Servidores MCP y Skill Global de SDD (22/06/2026)**
  - [x] **Servidores MCP Configurados**: Creado el archivo `mcp_config.json` en el directorio de usuario de Antigravity, registrando Playwright MCP y CodeGraph para dotar al agente de herramientas interactivas de navegador y mapas sintácticos de código.
  - [x] **Skills Locales y Globales**: Creado el skill de Desarrollo Guiado por Especificaciones (`specification-driven-development`) de forma local en `.agents/skills/` y global en `.gemini/config/skills/` para homogeneizar la planificación y mitigar el vibe coding.
  - [x] **Reglas del Espacio de Trabajo (`AGENTS.md`)**: Creado el archivo de reglas técnicas y de negocio en `.agents/AGENTS.md` (FastAPI, React, SQLite/Supabase y recordatorio del bloqueo temporal de scrapers vintage).
  - [x] **Remoción de Componente Inactivo**: Verificada y eliminada la página obsoleta `Vintage.tsx` por carecer de referencias en la aplicación, optimizando el análisis del codebase.
  - [x] **Corrección de Telemetría de Amazon**: Añadida la carga de variables `.env` mediante `dotenv` al inicio de `base.py` para asegurar que `SCRAPERAPI_KEY` se cargue en ejecuciones en segundo plano/segundo plano, y robustecido el selector de títulos en el fallback de Playwright de `amazon_scraper.py`.
  - [x] **Corrección de Violación SQL NOT NULL**: Modificados los retornos tempranos de `update_database` en `pipeline.py` para devolver `0` en vez de `None` en lotes vacíos (como bloqueos de CloudFront WAF en Wallapop), evitando errores de base de datos en `scraper_execution_logs.new_items`.
  - [x] **Auto-scroll y Seguimiento de Telemetría**: Implementada la creación síncrona de `log_id` en el backend para poder auto-seleccionar y seguir instantáneamente en el frontend (`targetLogId`) la telemetría del scraper lanzado. Añadido auto-scroll automático vertical en la consola de logs de `Config.tsx`.

- [x] **Phase 75: Calibración Violeta, Atmósfera Inmersiva, Estandarización de Iconos y Enlace Global Supabase (28/06/2026)**
  - [x] **Estandarización de Iconos y Estilo Outline**: Reemplazo de emojis coloridos en la Gestión de Héroes y el modal de reclutamiento por iconos vectoriales outline monocromáticos (Swords, Shield y ChevronDown).
  - [x] **Dynamic Logs Parser en Telemetría**: Conversión de caracteres emoji a componentes Lucide outline vectoriales (Play, Swords, Search, etc.) al vuelo dentro de la consola del frontend.
  - [x] **Limpieza y Saneamiento de Filtros**: Eliminación de chips de filtros rápidos redundantes (`MOC`, `Loose`, `Graded`, `Vintage` en Mi Fortaleza) y renombrado de filtros manuales/automáticos a `Man` y `Auto` en contorno sin emojis.
  - [x] **Reproductor de Audio Ambiental**: Creación de reproductor de banda sonora con controles de encendido/apagado en el Navbar (`Volume2` y `VolumeX`) y persistencia en localStorage de la preferencia.
  - [x] **Cuota de Mercado y Doughnut Chart**: Incorporado gráfico interactivo Doughnut en el panel de Conquistas de Mercado con ordenación descendente dinámica, tooltips optimizados en contraste y redirección directa al Catálogo con filtros pre-cargados al pulsar sobre cualquier marketplace.
  - [x] **Conexión Supabase Activa**: Uncommenting de `SUPABASE_DATABASE_URL` en el fichero `.env` para garantizar la persistencia e inyección de datos de configuración global directamente al servidor Supabase.
  - [x] **Resolución de Inconsistencias de Código (Auditoría code-error-analyzer)**:
    *   Eliminados warnings de compilación en Vite/Rollup al unificar y estrucutrar las importaciones estáticas de `admin.ts` en `Catalog.tsx` y `Collection.tsx` (descartados los dynamic imports redundantes).
    *   Sustituido el uso obsoleto de `datetime.utcnow()` en `product.py` por `datetime.now(UTC).replace(tzinfo=None)` para erradicar las alertas de deprecación en la suite de pruebas unitarias (`pytest`).
    *   Alineados los scrapers registrados en `ensure_scrapers_registered()` (`deps.py`) añadiendo `Triguetech` y `LaMansionDelTerror` y removiendo el obsoleto `Tradeinn`.
    *   Removido el parche estático de strings en `Dashboard.tsx` dado que el nombre de la wave de WWE ya se almacena correctamente en la base de datos.
    *   Consistencia total en el escudo de Grayskull (incógnito) para ocultar y difuminar todos los contadores de la colección, leyendas del Doughnut Chart, tooltips y Regimientos de Completitud en el Dashboard.
  - [x] **Bypass de CloudFront WAF y Robustez de Entorno en Wallapop**:
    *   Forzada la carga absoluta de `.env` con `override=True` en `config.py` y `base.py` para asegurar que `SCRAPERAPI_KEY` se inyecte de forma íntegra sin fallas de entorno en subprocesos.
    *   Implementado el **Bypass Interactivo local**: el scraper abre el navegador en modo visible (`headless=False`) temporalmente al topar con Cloudflare y espera hasta 20 segundos para que el usuario resuelva el Captcha en pantalla. Al completarse, prosigue la extracción gratis.
    *   Homogeneizada al 100% la consola de telemetría del frontend (`Config.tsx`), mapeando los emojis restantes de logs (`📡`, `🌩️`, `🕵️`, `🍪`, `💾`, `✅`, `⌛`, `🎉`) a iconos outline de Lucide (`Wifi`, `CloudLightning`, `Search`, `Cookie`, `Database`, `CheckCircle2`, `Clock`, `Sparkles`).

- [x] **Phase 76: Compactación Estadística FinOps e Incursión Universal CDP (07/07/2026)**
  - [x] **Compactación de Precios**: Implementado el modelo `ProductMonthlyStatsModel` y el servicio `MaintenanceService.compact_database` para consolidar el historial detallado de precios en resúmenes mensuales que incluyen promedio, mediana, percentil 25, percentil 75, desviación estándar y volumen.
  - [x] **Purgas Inteligentes**: Configurado el purgado de ofertas detalladas inactivas para productos muertos e historial antiguo para productos vivos.
  - [x] **Mantenimiento en Daily Scan**: Enganchado el mantenimiento al inicio del job automático diario `daily_scan.py` para prevenir cuotas llenas en Supabase de forma recurrente.
  - [x] **Mantenimiento a Demanda**: Integrado el endpoint API `POST /api/system/maintenance` y una tarjeta de control premium "Purificación FinOps" en la pestaña de configuración del frontend (`Config.tsx`) con un alert de reporte del espacio liberado.
  - [x] **Scraping Universal CDP**: Creado el script `scripts/scrape_multi_via_cdp.py` y `run_assisted_incursion.ps1` en la raíz para permitir el scraping asistido de cualquier tienda abierta en la pestaña de Chrome (Amazon, eBay, Smyths Toys, BBTS) conectada al puerto 9222.

---

## ✅ Plan de Verificación

1. **Integridad de Datos**: Scripts de validación de catálogo post-migración.
2. **Rendimiento API**: Pruebas de carga básicas en la nueva capa FastAPI.
3. **Cross-Platform UI**: Pruebas visuales en navegador móvil y escritorio.

---

## 📖 Control de Cambios y Validación Documental

Cada hito alcanzado debe ser registrado aquí para mantener la integridad de la visión del proyecto. Ninguna decisión técnica relevante debe quedar fuera de este documento.

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

## ✅ Plan de Verificación

1. **Integridad de Datos**: Scripts de validación de catálogo post-migración.
2. **Rendimiento API**: Pruebas de carga básicas en la nueva capa FastAPI.
3. **Cross-Platform UI**: Pruebas visuales en navegador móvil y escritorio.

---

## 📖 Control de Cambios y Validación Documental

Cada hito alcanzado debe ser registrado aquí para mantener la integridad de la visión del proyecto. Ninguna decisión técnica relevante debe quedar fuera de este documento.

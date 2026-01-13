# 🔮 MASTER ROADMAP: El Oráculo de Eternia

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
1.  **SQLite (Local)**: Buffer de alta velocidad para scrapers y trabajo offline.
2.  **Supabase/PostgreSQL (Cloud)**: Estado global, multi-usuario y fuente de verdad definitiva.
3.  **Sincronización (Broker API + Queue)**: FastAPI actúa como mediador con una **Cola de Tareas en Segundo Plano**. El usuario nunca espera a la nube; el cambio se confirma localmente al instante y se sincroniza "fuera de banda".

### Imágenes (Cero Coste & Nube)
- **Hotlinking**: Para imágenes de tiendas (0 bytes storage).
- **Cloudinary**: Para la colección personal (capa gratuita).

---

## 🗺️ Fases de Ejecución

### Fase 0: Consolidación del Catálogo y Migración Segura
*   **Origen**: `actionfigure411.com` vía `src/collectors/personal_collection.py`.
*   **Identidad Multivariante & Capa de Mapeo**:
    - Para manejar cambios de nombre o versiones (ej. Michelangelo V2), se usará una **Capa de Alias**.
    - Cada URL de scraping se vincula a un `Product ID` interno. Si el nombre del item cambia en el catálogo, el mapeo persiste porque apunta al ID, no al nombre.
    - La imagen (`Image Hash`) servirá como validador visual independiente frente a colisiones de nombres **y como base para el futuro Buscador Óptico**.
*   **Preservación de Datos en la Nube (Validación Estricta)**:
    - **Importación & De-duplicación**: Se descargarán las tablas de Supabase (`users`, `roles`, `collection_items`). Se aplicará una lógica de colisión para evitar duplicados y la creación de items "fantasma".
    - **Logs de Auditoría**: Cada decisión de fusión o descarte de datos de Supabase quedará registrada en un log de migración para trazabilidad total.
    - El nuevo catálogo se integrará con estos datos existentes para que ningún usuario pierda su configuración o inventario validado.
*   **Acción**: Unificar `lista_MOTU.xlsx`, auditorías locales y tablas de Supabase en el nuevo esquema relacional, validado mediante tests de integridad de datos.

### Fase 1: Reestructuración Modular (Clean Architecture)
*   **Tecnologías & Herramientas**:
    - **Lenguajes**: Python 3.10+ (Tipado estricto con `mypy`/`pyright`).
    - **Validación**: **Pydantic V2** para DTOs y modelos de dominio.
    - **Persistencia**: **SQLAlchemy 2.0** (estilo moderno) + **Alembic** para migraciones (control de versiones de la DB).
    - **Calidad**: **Ruff** (linting ultra-rápido) y **Pytest** (suite de tests unitarios).
*   **Estrategias de Diseño**:
    - **Patrón Repositorio**: Desacoplar la lógica de negocio de la base de datos (SQLite/Supabase).
    - **Arquitectura de Cebolla (Onion)**: Las dependencias solo apuntan hacia adentro (Dominio -> Aplicación -> Infraestructura).
    - **Inyección de Dependencias**: Facilitar el testing mediante el paso de servicios e interfaces.
*   **Estructura `src/`**: Separación en `core` (config), `domain` (entidades), `application` (casos de uso), `infrastructure` (DB/Scrapers) y `interfaces` (Web/API).
*   **Hito de Consistencia**: Refactorización total de imports y eliminación de acoplamientos circulares.

### Fase 2: El Bastión de Datos y Guardianía (Sentinel) ✅
*   **Auditoría**: Implementar `OfferHistory` para registrar cada movimiento de precio.
*   **Módulo Centinela (NUEVO)**: Lógica de activación de alertas proactivas. Si un precio baja del umbral definido, se genera un evento de notificación listo para consumo.
*   **Purgatorio (`PendingMatch`)**: Los scrapers externos depositan hallazgos aquí; solo pasan al catálogo principal tras validación manual o matching de alta confianza.
*   **Refinado de Precisión Estratégica**:
    - **Pesos Dinámicos (IDF) ✅**: Identidad y Serie se calculan automáticamente basándose en la rareza en el catálogo matriz.
    - **Normalización de Sinónimos ✅**: Soporte para `TMNT`, `MOTU`, `Origins`, etc.
    - **Leyes de Hierro & Veto ABSOLUTO ✅**: El sistema inteligente (Python) bloquea falsos positivos de motores rápidos (Rust) si hay conflicto de identidad.
    - **Gestión de Identidades (Refinado de Precisión) ✅**: Integración de Subcategoría en el cálculo de pesos para diferenciar líneas de juguetes.
    - **Buscador de Identidades Manifiesto (NUEVO)**: UI para ver qué palabras el sistema considera críticas y permitir ajustes manuales.
    - **Refuerzo por Descarte**: Si un admin descarta una sugerencia, el sistema "aprende" a bajar el peso de esa relación específica.

### Fase 3: Transactional API Broker (FastAPI) & Out-of-Band Sync ✅
*   **Estrategia "Out-of-Band" (No Bloqueante) ✅**:
    - **App Update Flow ✅**: Cuando el usuario modifica un item, la app escribe en una tabla de `SyncQueue` (SQLite) y devuelve éxito al instante.
    - **Worker Silencioso ✅**: Un proceso independiente (Worker) lee la `SyncQueue` y negocia con el **FastAPI Broker** la subida a Supabase sin afectar la navegación del usuario.
    - **Reintentos Inteligentes ✅**: Si no hay conexión, el Worker reintenta automáticamente en segundo plano.
*   **FastAPI como Broker & Validador ✅**:
    - Centraliza la lógica de negocio y validación Pydantic para asegurar que lo que llega a la nube sea perfecto.
    - **Seguridad de Frontera ✅**: Implementado sistema de `X-API-KEY` obligatorio para sincronización.
    - **Stack Moderno ✅**: Migrado sistema de comunicación a **HTTTPX** para mayor performance y compatibilidad asíncrona.
    - **Operación Rescate ✅**: Backup masivo de datos antiguos (Supabase -> JSON) para preservar la colección de David y la blacklist antes del cambio de esquema.
    - Proporciona endpoints de salud para monitorear el estado de la sincronización.
*   **Infraestructura Cloud (PENDIENTE)**:
    - Configurar **GitHub Actions** para invocar los endpoints de la API de sincronización.
    - Secretos gestionados exclusivamente en el entorno de la API.
*   **Canales de Notificación**: Integración de tokens para Telegram/Discord en la configuración cloud.
### Fase 4: Revolución UX (Frontend Evolution) 🚀
*   **Desacoplamiento Total**: Con el backend ya robustecido en la Fase 3, la Fase 4 se centra 100% en la experiencia de cliente.
*   **Frontend Stack ✅**:
    - **Vite 6 + React 19 + TypeScript**: Base de alto rendimiento.
    - **Tailwind CSS 4.0 ✅**: Motor de estilos de última generación (sin archivos de config pesados).
    - **TanStack Query (React Query)**: Gestión de estado asíncrono y caché para la API.
    - **Framer Motion**: Micro-animaciones para una sensación premium.
*   **Hitos de Interfaz**:
    - **Diseño Glassmorphism**: Estética moderna con transparencias y desenfoques (MOTU-Dark).
    - **Componentes Atómicos**: Botones, Modales y Cards unificados para toda la app.
    - **SPA Navigation**: Cambio entre Catálogo, Purgatorio y Centinela instantáneo.
*   **Consumo de API**: El frontend consume exclusivamente la API de FastAPI desarrollada en la fase anterior, garantizando fluidez y velocidad de respuesta instantánea.

### Fase 5: Refinamiento Táctico (La Gran Purificación) ✅
*   **Reingeniería de Calidad de Datos**:
    *   **SmartMatch Revertido ✅**: Capacidad de deshacer masivamente vínculos automáticos erróneos.
    *   **Purgatorio v2 (Inteligencia) ✅**: Motor de sugerencias que muestra coincidencias ordenadas por probabilidad (30%+).
    *   **SmartMatch 2.0 ✅**: Umbral elevado al 75%. Lo dudoso se deriva a revisión manual.
*   **Verdad del Tablero (Real-Time)**:
    *   Desacoplamiento de métricas históricas. Ahora el Dashboard refleja el estado vivo de la base de datos `OfferModel`.
    *   Sincronización instantánea de contadores tras purificación o vinculación.
*   **Experiencia de Catálogo**:
    *   **Market Intelligence UI**: Indicadores visuales ("Live" badge) para productos con ofertas activas.

### Fase 6: Estrategia de Valor y Futuro (Innovación)
*   **Estimador de Valor (Financial)**: Cálculo automático del valor de la colección basado en precios históricos y estado del item.
*   **Buscador Óptico (Future Vision)**: Identificación de figuras mediante carga de fotos (comparativa de hashes).
*   **Exportación de Seguridad**: Generación de reportes PDF detallados para seguros y auditorías personales.

---

## ✅ Plan de Verificación

1.  **Integridad de Datos**: Scripts de validación de catálogo post-migración.
2.  **Rendimiento API**: Pruebas de carga básicas en la nueva capa FastAPI.
3.  **Cross-Platform UI**: Pruebas visuales en navegador móvil y escritorio.

---

## 📖 Control de Cambios y Validación Documental
Cada hito alcanzado debe ser registrado aquí para mantener la integridad de la visión del proyecto. Ninguna decisión técnica relevante debe quedar fuera de este documento.

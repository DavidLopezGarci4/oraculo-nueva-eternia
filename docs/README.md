# 🔮 El Oráculo de Nueva Eternia

**Centro de Inteligencia de Mercado y Gestión de Colecciones MOTU Origins**

![Oráculo Dashboard](https://img.shields.io/badge/Version-2.1.0-gold?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Operating-green?style=for-the-badge)
![Tech](https://img.shields.io/badge/Stack-React_19_|_FastAPI_|_Docker-blue?style=for-the-badge)

---

## 📖 Tabla de Contenidos

- [1. Visión General](#1-visión-general)
- [2. Áreas de la Aplicación](#2-áreas-de-la-aplicación)
  - [Dashboard de Inteligencia](#dashboard-de-inteligencia)
  - [Catálogo Maestro](#catálogo-maestro)
  - [La Fortaleza (Mi Colección)](#la-fortaleza-mi-colección)
  - [El Purgatorio (Validación)](#el-purgatorio-validación)
  - [Panel de Configuración](#panel-de-configuración)
- [3. Arquitectura y Tecnologías](#3-arquitectura-y-tecnologías)
- [4. Funcionamiento Interno](#4-funcionamiento-interno)
  - [El Motor SmartMatch](#el-motor-smartmatch)
  - [Sistema de Sincronización](#sistema-de-sincronización)
- [5. Guía Técnica y Despliegue](#5-guía-técnica-y-despliegue)
- [6. Arquitectura 3OX (Kernel T3)](#6-arquitectura-3ox-kernel-t3)
- [7. El Motor de Inversión (DealScorer)](#7-el-motor-de-inversión-dealscorer)
- [8. Roadmap y Evolución](#8-roadmap-y-evolución)

---

## 1. Visión General

**El Oráculo de Nueva Eternia** es una plataforma integral diseñada para coleccionistas de alto nivel (específicamente de la línea *Masters of the Universe: Origins*). Su propósito es doble:

1. **Vigilancia de Mercado**: Escanea automáticamente 16 tiendas en España y Europa para encontrar las mejores ofertas, detectar stock y alertar sobre bajadas de precio.
2. **Gestión Patrimonial**: Permite llevar un control exhaustivo de la colección personal, calculando el valor real de mercado frente a la inversión realizada (ROI).

---

## 2. Áreas de la Aplicación

- **Radar de Eternia (Admin Only)**: Un widget de actividad que muestra en tiempo real los últimos hallazgos de los scrapers.
- **Top Deals**: Algoritmo que filtra las mejores ofertas del mercado para productos que **aún no tienes** en tu colección. Los controles de gestión están reservados para administradores.

### Catálogo Maestro (Nueva Eternia)

La base de datos definitiva de todos los productos MOTU Origins, refinada mediante la **Evolución 4.7**.
- **Gestión Táctica (Intelligent Hierarchy)**: El catálogo excluye automáticamente los ítems que ya posees, permitiéndote concentrarte en el "Abastecimiento".
- **Optimal Purchase Window**: Los ítems se ordenan dinámicamente por "Edad" (Figure ID) y Comportamiento de Mercado:
  - **Zonas de Riesgo**: Ítems antiguos que empiezan a revalorizarse.
  - **Punto Dulce**: Ítems en su precio mínimo histórico (Price Floor).
  - **Exploración**: Novedades en fase de enfriamiento para detectar el mejor momento de entrada.
- **Historial de Precios (Cronos)**: Gráficos y tablas que muestran la evolución del precio de un item en diferentes tiendas.
- **Indicadores "Live"**: Los items con ofertas activas brillan con un badge cyan, indicando oportunidad de compra.

### La Fortaleza (Mi Colección)

El espacio personal del coleccionista.
- **Pestañas Poseído/Deseado**: Diferencia lo que ya tienes de tu **Wishlist** (objetivos de caza).
- **Gestión de Estado (El Legado)**: Registro quirúrgico de precio de compra, estado (MOC/New/Loose) y **Grado de Conservación (1-10)** para detección de "Shelf Wear".
- **Claim System**: Al comprar un item de la wishlist, se "reclama" y pasa a la fortaleza pidiendo los datos de inversión real.

### El Purgatorio (Validación)

Donde llegan los hallazgos de los scrapers antes de ser "Verdad Absoluta".
- **Sistema de SmartMatch**: El motor sugiere a qué figura del catálogo pertenece cada oferta encontrada.
- **Evolución de Precios**: Si un item en el Purgatorio cambia de precio antes de ser vinculado, el sistema actualiza su valor automáticamente, permitiendo rastrear ofertas y rebajas en tiempo real.
- **Validación Manual**: El usuario aprueba o descarta los vínculos.
- **Importación de Wallapop**: Sistema semi-automatizado mediante **Playwright Nexus**. Permite extracciones masivas (150+ items) saltando bloqueos 403 mediante una estrategia híbrida de "Click & Scroll" (Click en *Cargar más* y descenso infinito).
- **Radar de Oportunidades P2P**: Detección inteligente de gangas individuales bajo la "Teoría de la Cuarentena".
- **Centinela de Cross-Validation**: Protección automática contra anomalías de precio y validación visual de reliquias.

### Panel de Configuración e Inteligencia Geográfica

* **Oráculo Logístico**: Configuración de ubicación por usuario (España, USA, Europa) para recalcular precios con precisión legal.
- **Control de Scrapers**: Activa o desactiva incursiones manuales y visualiza logs de ejecución en vivo.
- **Gestión de Datos**: Acceso a herramientas de limpieza y duplicados.

---

## 3. Arquitectura y Tecnologías

La aplicación sigue una **Arquitectura de Cebolla (Clean Architecture)** ultra-desacoplada:

| Capa | Tecnología | Propósito |
| :--- | :--- | :--- |
| **Kernel 3OX** | Sirius Protocol (Tier 3) | Control de misión, auditoría inmutable y gestión de límites. |
| **Adapter (vec3)** | Python 3.11 (Adapters) | I/O robusto, UTF-8 forzado y mediación entre scripts. |
| **Frontend** | React 19 + Vite + TypeScript | Interfaz premium, rápida y tipada. |
| **Estilos** | Tailwind CSS 4.0 + Framer Motion | Estética "Glassmorphism" y animaciones. |
| **API Broker** | FastAPI (Python 3.11) | Mediador de lógica de negocio y seguridad. |
| **Base de Datos** | PostgreSQL (Supabase) | Fuente de verdad global y persistente. |
| **Scrapers** | Playwright + BeautifulSoup4 | Infiltración en tiendas y bypass de bloqueos. |
| **Contenedores** | Docker + Docker Compose | Despliegue portable y aislado. |

---

## 4. Funcionamiento Interno

### El Motor SmartMatch

Es el cerebro que decide si una oferta de "Hordak" en una tienda alemana coincide con el "Hordak" de tu catálogo. Utiliza una estrategia de tres capas:

1. **EAN Match**: Si hay código de barras, el match es instantáneo (100% confianza).
2. **Rust Kernel**: Un motor en Rust para comparaciones ultrarrápidas de texto.
3. **Python Brain (Veto)**: Un analizador semántico que usa pesos IDF (identifica palabras clave como "Origins" vs "Masterverse") y tiene poder de **Veto** si detecta una disonancia de identidad.

### Sistema de Sincronización

Para evitar esperas, el Oráculo usa un flujo **Out-of-Band**:

- **Dashboard Hyper-speed**: Optimización de consultas N+1 y pre-caché de reglas logísticas para cargas instantáneas.
- **Doble Capa de Búsqueda (Purgatorio)**: Separación de estados para filtrar la lista de espera y el catálogo maestro de forma independiente.
- **Wallapop P2P Native**: Las capturas de Wallapop se marcan como Peer-to-Peer para alimentar automáticamente "El Pabellón".
- **Kaizen Learning Log**: Memoria persistente del oráculo que registra hallazgos cualitativos y patrones de mercado.

### Jerarquía Táctica (Motivation Engine)

Implementada en la Fase 4.7, esta lógica sustituye el orden estático por un algoritmo de priorización táctica:

1. **Exclusión de Propiedad**: Si el ítem ya está en la Fortaleza, se oculta de Nueva Eternia.
2. **Clasificación Cromática**: Los IDs de las figuras se categorizan por color (Ámbar para Vintage, Plata para Medios, Azul para Nuevos).
3. **Boost de Cierre de Set**: Los ítems pertenecientes a sub-categorías casi completadas reciben un empuje dinámico para motivar el cierre de la colección.

- **Hero Dynamic Selector**: Cambio de identidad atómico entre "Guardian" y "Master" con persistencia local.
- **Búsqueda Contextual**: Filtrado en tiempo real en Catálogo y Colección con gestión de estado global.
- **Landed Price Engine**: Cálculo preciso de costes de importación (Estrategia BBTS, IVA, Aduanas).
- **Universal Migrator**: Sincronización automática de esquemas entre SQLite (Local) y Supabase (Cloud).

* Un **Worker en segundo plano** se encarga de negociar con la nube (Supabase) a través de la API, gestionando reintentos si falla la conexión.

---

## 5. Guía Técnica y Despliegue

### Requisitos Previos

* Docker y Docker Compose instalados.
- Python 3.11+ (para desarrollo local).
- Node.js 20+ (para desarrollo frontend).

### Instalación Rápida (Modo Arca)

Para levantar todo el sistema (Backend + Frontend + DB) en contenedores:

```powershell
.\launch_ark.ps1
```

### Comandos de Desarrollo

Si prefieres ejecutar los servicios por separado:

**Backend (API + Scrapers):**

```powershell
pip install -r requirements.txt
$env:PYTHONPATH="."
python src/interfaces/api/main.py
```

**Frontend:**

```powershell
cd frontend
npm install
npm run dev
```

### Variables de Entorno (.env)

Configura estos valores para la conexión total:

```env
DATABASE_URL=sqlite:///./oraculo.db
SUPABASE_DATABASE_URL=postgresql://user:pass@db.supabase.co:5432/postgres
ORACULO_API_KEY=tu_clave_secreta
TELEGRAM_BOT_TOKEN=tu_token
```

---

## 6. Roadmap y Evolución

- **Fase 9 (Guardiana)**: ✅ Perfiles de usuario y Wishlist (Completado).
- **Fase 10 (Mercados)**: ✅ Integración de Amazon España (Completado).
- **Fase 11 (Continental)**: ✅ Expansión a 14 fuentes europeas y auditoría de precios OSS (Completado).
- **Fase 12 (Logística & Identidad)**: ✅ Rebranding a "Nueva Eternia", auditoría total del catálogo (297 reliquias) e implementación del **Nexo Maestro** para sincronización automática.
- **Fase 13 (Subastas & Amazon)**: ✅ Creación del **Pabellón de Subastas** (Wallapop/eBay) e infiltración en Amazon.es (Completado).
- **Fase 15 (Oráculo Logístico)**: ✅ Implementación del **Landed Price** (IVA, Envío, Aduanas) y ROI de precisión (Completado).
- **Fase 17 (El Centinela)**: ✅ Detección de anomalías de precio y blindaje preventivo del catálogo (Completado).
- **Fase 18 (DealScorer)**: ✅ Algoritmo de puntuación de oportunidad y alertas críticas de "Compra Obligatoria" (Completado).
- **Fase 21 (Blindaje Operativo)**: ✅ Correcciones críticas de logging, serialización y diagnósticos CI/CD (Completado).
- **Fase 21.5 (Purgatory-First Policy)**: ✅ Nueva estrategia de flujo de datos: 100% de nuevas extracciones a revisión manual para precisión total (Completado).
- **Fase 22 (Unlink Control)**: ✅ Botón de desvinculación administrativa y limpieza de alias para una "sanación" total del catálogo (Completado).
- **Fase 23 (Security Hardening)**: ✅ Doble confirmación y relocalización de acciones críticas de reset para protección del Reino (Completado).
- **Fase 24 (Dashboard Mastery)**: ✅ Control absoluto desde el Tablero: desvincular y re-vincular ofertas sin salir de la vista principal (Completado).
- **Fase 25 (Security & Sync)**: ✅ Refuerzo de seguridad API y motor de sincronización persistente con "Ghost Mode" (Completado).
- **Fase 26 (Nexo Maestro Cloud)**: ✅ Robustez del scraper de catálogo y sincronización de imágenes en Supabase Storage para acceso universal (Completado).
- **Fase 27 (Supabase Hardening)**: ✅ Activación de Row Level Security (RLS) y blindaje de la API pública de Supabase (Completado).
- **Fase 28 (Sync Engine Resurrect)**: ✅ Reparación del búfer de sincronización estancado y automatización total de imágenes en CI/CD (Completado).
- **Fase 29 (Log & Visibility Fix)**: ✅ Recuperación masiva de logs internacionales y blindaje del ciclo de escaneo diario (Completado).
- **Fase 30 (Scraper Robustness)**: ✅ Superación de bloqueos en BBTS y estabilización del Nexo Maestro contra timeouts (Completado).
- **Fase 31 (Ghost Sync Fix)**: ✅ Reparación del búfer estancado y creación de la **Sala de Autopsia Forense** con rescate masivo y blindaje de esquema de base de datos (Completado).
- **Fase 32 (Search Expansion)**: ✅ Ampliación del buscador manual de 10 a 20 resultados para visibilidad total de variantes (Completado).
- **Fase 33 (Scraper Decommission)**: ✅ Eliminación de scrapers obsoletos (MotuClassicsDE/VendiloshopIT) y unificación de "Fantasía Personajes" para una UI sin duplicados (Completado).
- **Fase 34 (Purificación & Eficiencia)**: ✅ Eliminación de código legado (Streamlit), indexación crítica de base de datos y eliminación de consultas N+1 en API y Pipeline (Completado).
- **Fase 35 (Amazon Infiltration)**: ✅ Implementación de `AmazonScraper` con evasión de bloqueos y procesamiento de 54 nuevas ofertas (Completado).
- **Fase 40 (Scraper Estandarización)**: ✅ Unificación de toda la infraestructura bajo `BaseScraper` y `scraper_name`, eliminando el legado de "Spiders" (Completado).
- **Fase 41 (Nexus & Amazon Fixes)**: ✅ Resolución de `AssertionError` en Nexo Maestro y refuerzo de sigilo (Stealth Mode) en Amazon.es (Completado).
- **Fase 42 (3OX vec3 Architecture Integration)**: ✅ Refactorización de scripts de entrada y creación de adaptadores en `vec3/dev/`. Implementación de forzado UTF-8 y desequilibrio de bloques monolíticos (Completado).
- **Fase 43 (Dashboard Role-Based Access)**: ✅ Restricción de secciones administrativas (Actividad y Conquistas) y botones de gestión a usuarios Admin para una experiencia limpia y segura (Completado).
- **Fase 44 (Dashboard Restructuring & Docker Fixes)**: ✅ Reordenación de secciones para Guardianes, herramientas operativas para Admin y resolución de fallos de arranque en contenedores (Completado).
- **Fase 45 (Tradeinn Hyper-Resiliente)**: ✅ Implementación de `TradeinnScraper` con bypass de redirecciones, modo sigilo avanzado y extracción de multi-tiendas (Diveinn, Kidinn, etc.) (Completado).
- **Fase 46 (Tactical Search Engine)**: ✅ Evolución del orquestador para soportar queries personalizadas y búsquedas de alta fidelidad para MOTU Origins en Tradeinn (Completado).
- **Fase 47 (Amazon Sirius A1 Armor)**: ✅ Superación de bloqueos 503 y CAPTCHAs en Amazon.es mediante legitimación de sesión y simulación humana (Completado).
- **Fase 50 (Sincronización Total)**: ✅ Integración de todos los scrapers (13 fuentes) en la bitácora del Purgatorio y GitHub Actions. Implementación del **Eternia Shield** (Sitemap Fallback) para DVDStoreSpain, logrando precisión total en la línea Origins (Completado).
- **Fase 54 (Reparación & Paridad P2P)**: ✅ Reparación del scraper de Pixelatoy (120 items), preservación de metadatos de subasta (Wallapop/Vinted) y fijación de envíos Tradeinn a 2.99€ (Completado).
- **Fase 55 (Restauración del Legado & Grading)**: ✅ Reconexión del botón (i) con motor de multiplicadores automáticos por estado y ajuste fino de ROI mediante grados de conservación (Completado).
- **Fase 56 (Blindaje Operativo)**: ✅ Estabilización de bd cloud larga, diagnóstico SMTP, limpieza de usuarios y ajuste global de retrys Frontend (Completado).
- **Fase 57 (Refactorización UX)**: ✅ Reserva táctica del loader intensivo para transiciones maestras, spinners ligeros para data-fetching y sistema de búsqueda multilínea optimizado para móvil (Completado).
- **Fase 58 (Expansión Frikimaz)**: ✅ Integración de `FrikimazScraper` (frikimaz.es, PrestaShop SSR). Eliminación de ActionToys. Paginación automática, extracción de EAN desde ficha de producto y fallback Playwright. Fuentes activas: 16 (Completado).

---

## 8. Arquitectura y Conocimiento (El Códice)

Para entender la sinergia entre todas las tecnologías y procesos, consulta el documento incremental:

- [📜 El Códice de Eternia (PROJECT_CODEX.md)](file:///c:/Users/dace8/OneDrive/Documentos/Antigravity/oraculo-nueva-eternia/docs/PROJECT_CODEX.md)

### El Nexo Maestro (Inteligencia AF411)

El sistema utiliza ActionFigure411 como Fuente de Verdad para benchmarks de mercado:
- **MSRP & Avg Price**: Extracción automática del precio original y el precio medio de subasta.
- **Market Momentum**: Un indicador dinámico (Avg/MSRP) que detecta si una figura se está apreciando.
- **Popularidad**: Conteo de coleccionistas para priorizar objetivos de caza.
- **Detección de Identificadores**: Captura automática de UPC y ASIN para vinculaciones precisas con Amazon y eBay.

---

## 7. El Motor de Inversión (DealScorer)

El Oráculo ahora actúa como un analista de inversiones personal. Cada oferta es procesada por el `DealScorer`, que asigna una puntuación de 1 a 100 basada en tres vectores:

1. **Vector MSRP (40%)**: Descuento respecto al precio oficial.
2. **Vector P25 (40%)**: Ventaja respecto al suelo de mercado de segunda mano.
3. **Vector Wishlist (20%)**: Prioridad subjetiva por objetivos de caza.

Las ofertas de **90+ puntos** activan una alerta inmediata de **"Compra Obligatoria"** vía Telegram, asegurando que nunca pierdas una oportunidad de alto Alpha.

- **Sincronización Cloud Inteligente**: Sistema de paridad que restaura y recalcula scores en Supabase para mantener la inteligencia de mercado siempre disponible en la nube.

---

> **Nota del Oráculo**: "Lo que no es seguro, al Purgatorio. Lo que es verdad, a la Fortaleza."

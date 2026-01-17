# 🔮 El Oráculo de Eternia

**Centro de Inteligencia de Mercado y Gestión de Colecciones MOTU Origins**

![Oráculo Dashboard](https://img.shields.io/badge/Version-2.0.0-gold?style=for-the-badge)
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
- [6. Roadmap y Evolución](#6-roadmap-y-evolución)

---

## 1. Visión General
**El Oráculo de Eternia** es una plataforma integral diseñada para coleccionistas de alto nivel (específicamente de la línea *Masters of the Universe: Origins*). Su propósito es doble:
1.  **Vigilancia de Mercado**: Escanea automáticamente múltiples tiendas en España y Europa para encontrar las mejores ofertas, detectar stock y alertar sobre bajadas de precio.
2.  **Gestión Patrimonial**: Permite llevar un control exhaustivo de la colección personal, calculando el valor real de mercado frente a la inversión realizada (ROI).

---

## 2. Áreas de la Aplicación

### Dashboard de Inteligencia (El Centro de Mando)
Es la pantalla de inicio y ofrece una vista de pájaro de todo el ecosistema.
*   **Métricas Financieras**: Valor Total de la Colección, Inversión Total y ROI (Retorno de Inversión).
*   **Griales del Reino**: Muestra las piezas con mayor valor de mercado o mayor revalorización.
*   **Radar de Eternia**: Un widget de actividad que muestra en tiempo real los últimos hallazgos de los scrapers.
*   **Top Deals**: Algoritmo que filtra las mejores ofertas del mercado para productos que **aún no tienes** en tu colección.

### Catálogo Maestro
La base de datos definitiva de todos los productos MOTU Origins.
*   **Navegación Líquida**: Listado optimizado con filtros por subcategoría (Origins, Turtles of Grayskull, etc.).
*   **Historial de Precios (Cronos)**: Gráficos y tablas que muestran la evolución del precio de un item en diferentes tiendas.
*   **Indicadores "Live"**: Los items con ofertas activas brillan con un badge cyan, indicando oportunidad de compra.

### La Fortaleza (Mi Colección)
El espacio personal del coleccionista.
*   **Pestañas Poseído/Deseado**: Diferencia lo que ya tienes de tu **Wishlist** (objetivos de caza).
*   **Gestión de Estado**: Registro de precio de compra, estado (NIB/Loose) y notas personales.
*   **Claim System**: Al comprar un item de la wishlist, se "reclama" y pasa a la fortaleza pidiendo los datos de inversión real.

### El Purgatorio (Validación)
Donde llegan los hallazgos de los scrapers antes de ser "Verdad Absoluta".
*   **Sistema de SmartMatch**: El motor sugiere a qué figura del catálogo pertenece cada oferta encontrada.
*   **Validación Manual**: El usuario aprueba o descarta los vínculos.
*   **Importación de Wallapop**: Debido a bloqueos anti-bot, Wallapop tiene un importador manual donde pegas texto/URL y el sistema lo procesa.

### Panel de Configuración
*   **Control de Scrapers**: Activa o desactiva incursiones manuales y visualiza logs de ejecución en vivo.
*   **Gestión de Datos**: Acceso a herramientas de limpieza y duplicados.

---

## 3. Arquitectura y Tecnologías

La aplicación sigue una **Arquitectura de Cebolla (Clean Architecture)** ultra-desacoplada:

| Capa | Tecnología | Propósito |
| :--- | :--- | :--- |
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
1.  **EAN Match**: Si hay código de barras, el match es instantáneo (100% confianza).
2.  **Rust Kernel**: Un motor en Rust para comparaciones ultrarrápidas de texto.
3.  **Python Brain (Veto)**: Un analizador semántico que usa pesos IDF (identifica palabras clave como "Origins" vs "Masterverse") y tiene poder de **Veto** si detecta una disonancia de identidad.

### Sistema de Sincronización
Para evitar esperas, el Oráculo usa un flujo **Out-of-Band**:
*   Tus cambios se guardan localmente al instante.
*   Un **Worker en segundo plano** se encarga de negociar con la nube (Supabase) a través de la API, gestionando reintentos si falla la conexión.

---

## 5. Guía Técnica y Despliegue

### Requisitos Previos
*   Docker y Docker Compose instalados.
*   Python 3.11+ (para desarrollo local).
*   Node.js 20+ (para desarrollo frontend).

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

*   **Fase 9 (Guardiana)**: ✅ Perfiles de usuario y Wishlist (Completado).
*   **Fase 10 (Mercados)**: 🏗️ Integración de APIs de Amazon y eBay (En progreso).
*   **Fase 11 (Continental)**: ✅ Expansión a 11 tiendas europeas y auditoría de precios OSS (Completado).
*   **Fase 12 (IA)**: ⏳ Implementación de LLMs para matching semántico avanzado.

---

> **Nota del Oráculo**: "Lo que no es seguro, al Purgatorio. Lo que es verdad, a la Fortaleza."

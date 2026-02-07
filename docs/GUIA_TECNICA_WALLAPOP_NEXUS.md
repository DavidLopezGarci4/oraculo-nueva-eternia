# 🕵️ Guía Técnica: Wallapop Playwright Nexus (Phase 44)

Este documento detalla la arquitectura de infiltración y el motor de extracción profunda desarrollado para Wallapop, diseñado para superar bloqueos CDN (403) y limitaciones de carga dinámica.

## 🏗️ 1. Arquitectura del Motor

El scraper utiliza **Playwright** como motor de renderizado, actuando como un navegador real para evadir las protecciones de CloudFront que bloquean peticiones HTTP directas.

| Componente | Función |
| :--- | :--- |
| **Playwright Context** | Genera una sesión con User-Agent de Chrome 120 y `locale: es-ES`. |
| **Sirius Stealth UI** | Simula desplazamientos de ratón y tiempos de espera humanos. |
| **Hybrid Expansion** | Combina disparadores de click con eventos de scroll infinito. |
| **P2P Router** | Etiqueta automáticamente los hallazgos para su visibilidad en "El Pabellón". |

---

## 🚀 2. Protocolo de Infiltración (Flujo de Ejecución)

### Fase A: Salto de Perímetro (Cookie Bypass)
Wallapop despliega un banner de OneTrust que bloquea todas las interacciones del DOM. El script utiliza un sistema de detección multivariante:
- **Prioridad 1**: ID del botón OneTrust (`#onetrust-accept-btn-handler`).
- **Prioridad 2**: Búsqueda por rol ARIA (`name="Aceptar todo"`).
- **Prioridad 3**: Selector semántico de texto (`button:has-text('Aceptar')`).

### Fase B: El Click Maestro
A diferencia de otros sitios, Wallapop requiere un **trigger manual** para activar el scroll infinito.
1. El script navega hasta el final de la primera carga.
2. Localiza el botón turquesa **"Cargar más"**.
3. Ejecuta el click. Sin este paso, el scroll infinito permanece inactivo a nivel de JavaScript en la página.

### Fase C: Descenso Profundo (Infinite Scroll)
Tras el click, se inicia un bucle de 8 niveles de descenso.
- **Micro-ajustes**: Se usa `page.mouse.wheel(0, 1500)` para simular scrolls rápidos.
- **Delay Humano**: Pequeños `asyncio.sleep` para permitir que el motor de reactividad de Wallapop cargue nuevos fragmentos del DOM.

---

## 🔎 3. Extracción y Normalización

### Selectores de Datos
Debido a la ofuscación de clases, el script utiliza selectores basados en estructura de URL:
- **Items**: `a[href*='/item/']` (Captura todos los productos cargados, incluso los nuevos).
- **Precios/Títulos**: Se extraen mediante navegación relativa dentro del contenedor del item.

### Atribución de Datos
Cada oferta se inyecta con metadatos de auditoría:
- `source_type = "Peer-to-Peer"`: Identificador crítico para la UI del Oráculo.
- `shop_name = "Wallapop"`.
- `receipt_id`: Hash SHA256 para evitar duplicidad forense.

---

## 🛠️ 4. Verificación de Éxito

La efectividad del motor se mide por la profundidad del "Abismo":
- **Pre-Optimización**: ~19-20 items (Superficie).
- **Post-Optimización (Nexus)**: **170+ items** (Descenso Profundo).

---

*Desarrollado bajo el estándar de seguridad 3OX para el Oráculo de Nueva Eternia.*

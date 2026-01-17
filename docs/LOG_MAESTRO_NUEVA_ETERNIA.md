# LOG MAESTRO: Oráculo Nueva Eternia

## Estado Actual: [SISTEMA OPERATIVO, AUDITADO Y REVERSIBLE]

Este documento registra la evolución técnica y estratégica del Oráculo. La Phase 4 ha sido completada con éxito, transformando la herramienta en una SPA moderna orientada a la inteligencia de mercado y la gestión de colecciones, con capacidad de auditoría total.

---

## CRONOLOGÍA DE VICTORIAS

### Fase 1: Despertar de la Conciencia (Backend Core)
- **Hitos**: Scrapers para 10 tiendas, base de datos SQLite y SmartMatcher original.
- **Estado**: ✅ COMPLETADO Y MIGRADÓ

### Fase 2: El Eco de las Reliquias (Frontend MVP)
- **Hitos**: Interfaz Streamlit, visualización básica y sistema de auditoría.
- **Estado**: ✅ COMPLETADO

### Fase 3: Puente hacia las Nubes (Cloud Architecture)
- **Hitos**: Preparación para Supabase, GitHub Actions y arquitectura de sincronización.
- **Estado**: ✅ COMPLETADO

### Fase 4: Revolución UX (La Nueva Era)
- **Hitos**: Migración a React 19, Tailwind CSS y Dashboard de Inteligencia.
- **Estado**: ✅ VALIDADO

#### 4.1 Core UX & Navegación
- **Hitos**: Sidebar dinámica, Navbar premium y sistema de Tabs (SPA).
- **Estado**: ✅ VALIDADO

#### 4.2 La Fortaleza (Colección)
- **Hitos**: Sistema de "Captura" de items, gestión de stock personal y valoración de colección.
- **Estado**: ✅ VALIDADO

#### 4.3 El Espejo (Purgatorio)
- **Hitos**: SmartMatcher manual, control de scrapers protegido y bitácora de incursiones.
- **Estado**: ✅ VALIDADO

#### 4.4 Tablero de Inteligencia (Dashboard)
- **Hitos**: Centro de mando con métricas de valor, radar de Eternia y Top Deals.
- **Estado**: ✅ VALIDADO

#### 4.5 Radar de Vínculos (Trazabilidad)
- **Hitos**: Registro persistente de vínculos manuales, conteo por tienda y historial de actividad.
- **Estado**: ✅ VALIDADO

#### 4.6 Bastión de Justicia (Reversión)
- **Hitos**: Implementación del sistema de "Deshacer" para vínculos y descartes. Restauración íntegra de metadatos al Purgatorio.
- **Estado**: ✅ VALIDADO

### Fase 5: Refinamiento Táctico (La Gran Purificación)
- **Hitos**: Reingeniería de calidad de datos y "Verdad del Oráculo".
- **Estado**: ✅ VALIDADO

#### 5.1 La Gran Purificación (Reset Total)
- **Hitos**: Capacidad de enviar TODAS las ofertas vinculadas al Purgatorio para re-verificación masiva.
- **Estado**: ✅ COMPLETADO

#### 5.2 Purgatorio v2 (Inteligencia Guiada)
- **Hitos**: Motor de sugerencias en tiempo real. Muestra coincidencias ordenadas por score (30%+).
- **Estado**: ✅ COMPLETADO

#### 5.3 SmartMatch 2.0 (Umbral de Calidad)
- **Hitos**: Elevación del estándar de auto-vinculación al 75%. Lo que no es seguro, va al Purgatorio.
- **Estado**: ✅ COMPLETADO

#### 5.4 Sincronización de Métricas (Real-Time Truth)
- **Hitos**: Tablero conectado directamente a `OfferModel`. Las métricas de "Vínculos Sagrados" y "Conquistas" son dinámicas al instante.
- **Estado**: ✅ COMPLETADO

- **Hitos**: Indicadores "Live" (brillo cyan) y badge para productos con ofertas de mercado activas.
- **Estado**: ✅ COMPLETADO

### Fase 6: Innovación (El Tesoro de Grayskull)
- **Hitos**: Motor Financiero, Detección de Griales y Estabilización de Infraestructura.
- **Estado**: 🏗️ EN PROGRESO

#### 6.1 Motor Financiero (Market Value)
- **Hitos**: Cálculo de valor real de colección vs inversión. Métricas financieras en Dashboard.
- **Estado**: ✅ COMPLETADO Y ESTABILIZADO (PostgreSQL)

#### 6.2 Detector de Griales (High Value)
- **Hitos**: Identificación automática de tesoros (ROI > 50% o Valor > 150€). UI Premium (Borde Dorado/Trofeo) en Mi Fortaleza. Estandarización a Euro (€).
- **Estado**: ✅ COMPLETADO

#### 6.3 Visionary Dashboard (Inteligencia de Mercado)
- **Hitos**: Implementación del endpoint `/hall-of-fame` y widgets frontend "Griales del Reino" (Top Valor) y "Potencial Oculto" (Top ROI).
- **Estado**: ✅ COMPLETADO


---

### Fase 7: Adaptación Híbrida (Mobile First)
- **Hitos**: Responsive Design integral, Widgets compactos y Estabilidad de datos.
- **Estado**: ✅ COMPLETADO Y ESTABILIZADO

#### 7.1 Navegación Líquida
- **Hitos**: Sidebar/Drawer móvil y Navbar táctil.
- **Estado**: ✅ COMPLETADO

#### 7.2 Optimización Táctil (UI Compacta)
- **Hitos**: Layouts "Compact Ticket" en Purgatorio y Grillas 2-Col en Colección. Reintegración de Enlace Externo.
- **Estado**: ✅ COMPLETADO

#### 7.3 Estabilidad del Purgatorio (Atomic Safety)
- **Hitos**: Solución definitiva a `Duplicate Key Error` mediante transacciones anidadas. Blindaje CSS contra desbordamientos.
- **Estado**: ✅ COMPLETADO

#### 7.4 Integridad de Dashboard (Data Consistency)
- **Hitos**: Corrección de discrepancia visula entre contadores y gráficos. Implementación de cálculo derivado (`sum(distribución)`) para garantizar coherencia matemática absoluta y corrección de `NameError` en runtime.
- **Estado**: ✅ COMPLETADO

#### 7.5 Refinamiento UX Purgatorio (Auto-Clear)
- **Hitos**: Mejora de calidad de vida. El buscador manual ahora se reinicia automáticamente al completar una vinculación o cambiar el foco a otro item, eliminando la fricción de borrar texto anterior.
- **Estado**: ✅ COMPLETADO

> [!NOTE]
> **Norma Operativa**: A partir de este hito, todos los títulos y descripciones para commits de GitHub deberán redactarse estrictamente en **ESPAÑOL** para mantener la coherencia con el idioma nativo del proyecto "Oráculo de Eternia".

---

### Fase 8: Omnipresencia (Dockerización)
- **Hitos**: Encapsulamiento total en contenedores y preparación para despliegue industrial (NAS/VPS).
- **Estado**: ✅ COMPLETADO (Estructura)

#### 8.1 El Arca (Dockerización Integral)
- **Hitos**: Creación de `Dockerfile` para Backend (Python/Playwright) y Frontend (Nginx). Implementación de `launch_ark.ps1` y accesos directos.
- **Estado**: ✅ COMPLETADO

#### 8.2 Blindaje de Producción (Grado Industrial)
- **Hitos**: Orquestación estable con `docker-compose.prod.yml`, persistencia de datos via volúmenes y creación del sistema "Guardián de Datos" para backups automáticos. Apertura de CORS para acceso universal móvil.
- **Estado**: ✅ COMPLETADO

#### 8.2.1 Sincronización Universal (Cloud Jump)
- **Hitos**: Transvase exitoso de toda la colección local y catálogo a Supabase.
- **Estado**: ✅ COMPLETADO

#### 8.2.2 Gestión de Identidad y Restauración
- **Hitos**: Activación del usuario "David" (ID 2). Reasignación atómica de los 75 items de "La Fortaleza" desde el admin al perfil personal de David. Verificación del esquema `UserModel`.
- **Estado**: ✅ COMPLETADO

#### 8.2.3 Multiusuario Fluido (Inyectando Conciencia)
- **Hitos**: Implementación del "Interruptor de Héroes" en la Navbar con persistencia en `localStorage`. Filtrado atómico por `user_id` en los motores del Dashboard (Stats, Top Deals, Hall of Fame). El sistema ahora distingue entre la colección de David y la vista de gestión del Admin.
- **Estado**: ✅ COMPLETADO

### 🏰 Fase 9: El Legado de Eternia (Poderes por Perfil)
Esta fase ha dividido el Oráculo en dos experiencias potentes y diferenciadas:

#### 9.1 El Arquitecto (Poderes de Admin)
- **Mando de Scrapers**: Central de control para activar incursiones manuales por tienda con visualización de logs de ejecución en tiempo real (Items encontrados, errores, tiempos).
- **Editor de la Verdad**: Herramienta de edición directa en el catálogo para corregir metadatos (Nombres, EANs, Categorías).
- **Radar de Duplicados & Fusión**: Motor de detección por EAN que permite fusionar dos productos transfiriendo ofertas y registros de propiedad sin pérdida de datos.
- **Descarte Masivo**: Interfaz de selección múltiple en el Purgatorio con barra de acciones flotante para limpieza a gran escala.
- **Estado**: ✅ COMPLETADO

#### 9.2 El Guardián (Experiencia David)
- **Lista de Deseos (Wishlist)**: Implementación de la lógica de "Target" donde David puede marcar futuras adquisiciones sin ensuciar sus métricas de inversión reales.
- **La Fortaleza 2.0**: Rediseño de la página de colección con sistema de pestañas (Poseído/Deseado) y estéticas premium con efectos de brillo y tarjetas dinámicas.
- **Upgrade de Reliquias**: Al adquirir un item de la wishlist, el sistema permite "Reclamarlo" con un clic, marcándolo como poseído y solicitando el precio de compra real.
- **Estado**: ✅ COMPLETADO

### 🛠️ Mecánica Técnica y Dockerización (Resumen de Arquitectura)

Para garantizar que el Oráculo sea indestructible y portable, hemos implementado las fases 8.2 y 8.3 bajo estos pilares:

#### 👤 Gestión de Identidad (Multi-Hero System)
*   **Restauración Atómica**: El perfil de **David** fue activado y sus 75 items reasignados mediante el script `restore_david.py`. La base de datos en Supabase ahora vincula cada item al `owner_id` correspondiente.
*   **Identidad Persistente**: El Frontend usa `localStorage` (`active_user_id`) para recordar quién ha entrado. Al cambiar de usuario en la Navbar, se refresca la sesión para inyectar el ID en todas las llamadas de la API.
*   **Filtrado en el Backend**: Los endpoints de la API (`/stats`, `/top-deals`, `/hall-of-fame`) han sido actualizados para filtrar resultados por el `user_id` recibido, garantizando que David vea su ROI personal y el Admin vea la salud global.

#### 🐳 Sincronización en el Arca (Docker)
*   **Desarrollo Líquido**: El entorno Docker está vinculado a la carpeta del proyecto mediante volúmenes. Esto permite que cualquier cambio en el código (como el nuevo selector de perfiles) se refleje en los contenedores al instante sin reconstruir imágenes.
*   **Persistencia Blindada**: Aunque los contenedores se detengan o actualicen, la base de datos local y los logs están mapeados fuera del Docker. Esto asegura que la "Fortaleza de Datos" sea inmune a reinicios.
*   **Escalabilidad NAS/VPS**: Al estar 100% Dockerizado, el Oráculo puede migrar a un servidor externo simplemente copiando la carpeta y lanzando el script, manteniendo todas las identidades y configuraciones intactas.

---

## PLAN DE VERIFICACIÓN (PÚLSAR)
1. **Radar**: Los vínculos manuales se reflejan instantáneamente en el Tablero.
- **8.3 Cronos**: Histórico de Precios premium integrado en Catálogo. ✅ COMPLETADO
- **8.4 Expansión Continental**: Integración de tiendas TOP europeas.

---

### 🔍 Fase 10: Infiltración en los Grandes Mercados (APIs & Scraping)
Iniciada tras la consolidación de Cronos, esta fase busca el dominio de los precios globales.
- **Inteligencia Amazon**: Definida estrategia para amazon.es centrada en monitoreo de precios (PA-API 5.0).
- **Inteligencia eBay**: Preparado conector OAuth 2.0 para Browse API (Búsqueda de subastas y ventas directas).
- **Inteligencia Wallapop**: Identificada API interna v3 y headers críticos para bypass de seguridad.
- **Monitorización de Ventas**: Investigando métodos para rastrear no solo precios, sino transacciones reales de MOTU Origins.

---

### 🧠 Sabiduría de los Grandes Mercados (Marketplace Intelligence)

Para la expansión a los "Tres Titanes" (Amazon, eBay, Wallapop), el Oráculo ha sintetizado las siguientes reglas de infiltración:

#### 📦 Amazon.es (El Gigante de la Logística)
*   **Misión**: Vigilancia de precios en España para detectar bajadas repentinas de stock oficial de Mattel.
*   **Técnica**: Uso de `PA-API 5.0` via `python-amazon-paapi`. Requiere cuenta de Afiliados con 3 ventas previas.
*   **Enfoque**: No ventas, solo extracción de `LowestNewPrice` y `OfferListingId`.

#### 🏛️ eBay (La Sala de Subastas Global)
*   **Misión**: Capturar el valor real de mercado mediante subastas y ventas históricas.
*   **Técnica**: `Browse API` con flujo `Client Credentials`. Búsqueda por palabras clave con filtros de categoría específicos de coleccionismo.
*   **Valor**: eBay es el estándar de oro para valorar piezas antiguas o raras de MOTU Origins.

#### 🤝 Wallapop (El Mercado del Pueblo)
*   **Misión**: Rastrear el pulso de la segunda mano y coleccionistas locales en España.
*   **Técnica**: Infiltración en la API interna (`api.wallapop.com/api/v3`) usando headers de dispositivo (`X-DeviceOS`) y User-Agents específicos.
*   **Desafío**: Gestión de proxies para evitar el ban de Cloudflare/DataDome.

#### 📊 Espionaje de Ventas Reales (Sales Monitoring)
Para capturar no solo el precio de oferta, sino el precio de transacción real, el Oráculo empleará estas tácticas:

*   **Action Figure 411 (El Oráculo Aliado)**: Es la fuente más limpia. Scrapearemos su guía de precios de MOTU Origins para obtener promedios de venta y listados de subastas finalizadas ya filtrados de ruido.
*   **eBay (Sold Listings)**: Infiltración mediante scraping de `&LH_Sold=1&LH_Complete=1`. Esto nos dará el pulso exacto de lo que los coleccionistas españoles están pagando **hoy**.
*   **Wallapop (Status Tracker)**: Monitorización selectiva de productos. Cuando un item desaparece o cambia a `status: sold`, el Oráculo registrará la última cifra conocida como precio de venta probable.
*   **Amazon (BSR Analysis)**: Seguimiento del `SalesRank` via PA-API. Una caída brusca en el ranking es un indicador directo de volumen de ventas.

---

## PLAN DE VERIFICACIÓN (PÚLSAR)
1. **Radar**: Los vínculos manuales se reflejan instantáneamente en el Tablero.
2. **Justicia**: Cada acción en el historial permite reversión inmediata con un clic.
3. **Métricas**: El Tablero calcula el valor total basándose en los items de "La Fortaleza".
4. **Movilidad**: Operatividad total verificada en resoluciones móviles y acceso via Docker/Nginx.

## PRÓXIMOS PASOS (EL OJO DE SAURON)
### Fase 8.4 & 8.4b: Expansión Continental y Avanzada
- **Hitos**: Integración de 6 nuevas tiendas internacionales (Holanda, Alemania, Italia, Europa, USA) y optimización stealth para GitHub Actions.
- **Estado**: ✅ COMPLETADO Y VERIFICADO

#### 🌍 El Oráculo Global (11 Tiendas Activas)
El Oráculo ahora monitoriza 11 fuentes de datos con tecnologías específicas para cada una:

1.  **España (5)**: ActionToys, Fantasia, Frikiverso, Pixelatoy, Electropolis (WooCommerce/Prestashop).
2.  **Europa (3)**: 
    *   `DeToyboys_scraper.py` (Holanda): Gestión de stock NL.
    *   `Motuclassics_de_scraper.py` (Alemania): Shopware crawler.
    *   `Vendiloshop_scraper.py` (Italia): Precios en Euros competitivos.
3.  **Avanzado (3)**:
    *   `Toymi_scraper.py` (EU): Paginación optimizada (102 productos detectados mediante `?af=60`).
    *   `Time4ActionToys_scraper.py` (Alemania): Gran volumen (273 productos) con paginación industrial.
    *   `BBTS_scraper.py` (USA): **Stealth Mode** avanzado (Playwright, fingerprint spoofing, init scripts anti-detección) para saltar Cloudflare desde GitHub Actions.

#### 🔧 Mejoras de Infraestructura y Datos
*   **Bypass de Cloudflare**: Implementación de técnicas de evasión en `BBTS_scraper.py` (Timezone USA, Geo-spoofing, movimientos humanizados).
*   **Corrección de BaseScraper**: Reparado bug crítico de importación en `base.py` que afectaba a la generación de User-Agents aleatorios.
*   **Optimización de Carga**: Configuración de `af=60` en Toymi para maximizar la eficiencia por cada incursión.
*   **Blindaje de Build (Docker)**: Corrección de errores de TypeScript en `Catalog.tsx`, `Config.tsx` y `Dashboard.tsx` para garantizar el despliegue industrial.
*   **Restauración de Propiedad**: Reasignación atómica de 75 items a la cuenta de David (ID 2), corrigiendo la discrepancia financiera en el Dashboard personal.
*   **Inteligencia de Mercado (Top Deals)**: Implementación de deduplicación por producto y filtrado dinámico por `owner_id`. El widget ahora solo muestra "lo mejor de lo que no tienes".

---

## PLAN DE VERIFICACIÓN (PÚLSAR)
1. **Radar**: Los vínculos manuales se reflejan instantáneamente en el Tablero.
2. **Justicia**: Cada acción en el historial permite reversión inmediata con un clic.
3. **Métricas**: El Tablero calcula el valor total basándose en los items de "La Fortaleza".
4. **Scrapers**: Verificados mediante `test_european_scrapers.py` y logs de `daily_scan.py`.

---

### Fase 10: Infiltración en los Grandes Mercados
- **Hitos**: Inteligencia de mercado extendida a plataformas de segunda mano y marketplaces globales.
- **Estado**: 🏗️ EN PROGRESO

#### 10.3 Inteligencia Wallapop (Segunda Mano)
- **Hitos**: Sistema de importación manual integrado en la web del Oráculo. Pestaña "Wallapop" en Admin → Config. Formato de entrada: `Nombre | Precio | URL`. Endpoint API: `POST /api/wallapop/import`.
- **Verificado**: 57 productos importados exitosamente al Purgatorio.
- **Limitación Técnica**: Wallapop usa CloudFront WAF que bloquea scraping automatizado. Solución híbrida: el usuario navega manualmente y pega los datos en la app.
- **Archivos Creados**:
  - `frontend/src/components/admin/WallapopImporter.tsx` - Componente React con preview en tiempo real.
  - `frontend/src/api/wallapop.ts` - Cliente API y parseador de texto.
  - `src/infrastructure/scrapers/wallapop_manual_importer.py` - Motor de importación CLI.
  - `import_wallapop.bat` - Script de acceso rápido.
  - `docs/GUIA_WALLAPOP_MANUAL.md` - Guía de uso.
  - `chrome-extension/` - Extensión de navegador (opcional, experimental).
- **Estado**: ✅ COMPLETADO (Importación Manual Integrada)

---

## FASE 11: ESTABILIZACIÓN Y AUDITORÍA EUROPEA (17/01/2026)

### 🛡️ Corrección Crítica: El Bastión de la Fortaleza (ID Sequence Fix)
- **Problema**: El endpoint `/api/collection/toggle` devolvía Error 500 para usuarios no-admin.
- **Causa**: Desincronización de la secuencia de IDs en PostgreSQL (`collection_items_id_seq`). La secuencia intentaba insertar ID 26 en una tabla que ya tenía items hasta el ID 75.
- **Solución**: Ejecución de `ALTER SEQUENCE collection_items_id_seq RESTART WITH 76`.
- **Resultado**: Registro y captura de items corregido para todos los usuarios.

### 🕸️ Auditoría Ejecutiva de Scrapers Continentales
- **ToymiEU (EU)**: Auditoría real exitosa. 106 items encontrados y procesados.
- **Time4ActionToys (DE)**: Auditoría real exitosa. 273 items encontrados y procesados.
- **Verificación**: Confirmación de los 11 scrapers europeos en `daily_scan.py` y configuración en GitHub Actions.

### 🛡️ Blindaje Atómico y Evolución de Precios (Bypass de Duplicados)
- **Inserción Atómica**: Implementado sistema de transacciones anidadas (Savepoints) en el `ScrapingPipeline`. El Arca ya no se detiene ante errores de `UniqueViolation` (duplicados de URL) en PostgreSQL, garantizando incursiones 100% resilientes.
- **Evolución en el Purgatorio**: Si una oferta ya existente en el Purgatorio cambia de precio, el sistema la actualiza automáticamente en lugar de ignorarla. Esto permite capturar fluctuaciones de mercado incluso antes de que el item sea vinculado manualmente.
- **Telegram Sync**: Las alertas de Telegram ahora operan sobre datos actualizados dinámicamente, reflejando rebajas en tiempo real.

### 🔗 Refinamiento de Wallapop (Anti-Bot Bypass)
- **Problema**: Wallapop bloquea enlaces directos (Error 403).
- **Mejora**: Implementación de botón **"Copiar URL"** en el Purgatorio y Dashboard.
- **UX**: Feedback visual ("¡Copiado!") para una navegación sin fricciones.

### 🛡️ Auditoría de Código y Refinamiento (The Oracle's Eye)
- **Corrección de Lints**: Eliminación de importaciones no utilizadas (`LinkIcon`) en `Dashboard.tsx`.
- **Blindaje de Rollback**: Corregido `AttributeError` en el script de reversión ejecutiva.
- **Verificación de Pipeline**: Confirmado que `daily_scan.py` integra correctamente los 11 scrapers activos (España + Europa).

### 🕸️ Operación "Purgatorio Limpio" (Rollback Total Europeo)
- **Acción**: Rollback extendido para **Time4ActionToysDE**, **Time4ActionToys** y **ToymiEU**.
- **Resultado**: +234 items de `Time4ActionToysDE` enviados al Purgatorio. Total acumulado de ~300+ items devueltos para auditoría manual tras detectar errores de SmartMatch y precios.
- **Limpieza de Alias**: Se han eliminado los `ProductAliasModel` para evitar que el sistema los vuelva a vincular automáticamente de forma inmediata.

### 🧩 Estabilidad del Arca (Fixes Técnicos)
- **Docker**: Limpieza de cache corrupto mediante `fix_docker_cache.bat` para resolver errores de `snapshot parent`.
- **Frontend**: Eliminación de importaciones huérfanas (`Upload`, `LinkIcon`) en `Config.tsx` y `Dashboard.tsx` que bloqueaban la compilación de producción de Vite.

### 🌍 Refinamiento Europeo (ToymiEU "Spanien" Fix)
- **Lógica de Precios**: El scraper `ToymiEUScraper` ahora detecta el selector OSS y fuerza la región a **España (ES)** antes de iniciar el escaneo.
- **Precisión**: Mejora en la extracción de precios priorizando tags `meta[itemprop="price"]` de Schema.org para asegurar que se capture el PVP con IVA español.

---

- [x] **11.1 Rollback masivo**: Auditoría europea completada y items devueltos al Purgatorio.
- [x] **11.2 Fix ToymiEU**: Lógica de selección de precios por país (España) implementada.
- [x] **11.3 Blindaje Atómico**: Inserción resiliente y actualización de precios en Purgatorio.
- [ ] **11.5 IA SmartMatcher**: Implementación de LLM ligero para mejorar el reconocimiento automático.
- [ ] **12.1 Infiltración Amazon**: Monitoreo de precios amazon.es.
- [ ] **12.2 Inteligencia eBay**: Conector Browse API + OAuth 2.0.

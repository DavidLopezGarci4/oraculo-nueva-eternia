import os

def update_3ox_log():
    log_line = "\n2026-06-09 09:50:00 | ARCHITECT: Implemented local product image caching system. Added StaticFiles mount at /api/static/images/ in FastAPI. Created background downloader task, status tracking, and cancellation APIs in vault router. Integrated custom React component MOTUImage supporting localStorage toggle (use_local_images) and runtime hotlink fallback. Integrated settings card and status progress bar in Config page, and swapped image tags across Showcase, Collection, Catalog, Vintage, and Dashboard pages. - [Estatus: Validado]\n"
    with open("3ox.log", "a", encoding="utf-8") as f:
        f.write(log_line)
    print("Updated 3ox.log")

def update_log_maestro():
    section = """

### ¿Y>¿? Fase 68: Caché Local de Imágenes y Fallback Híbrido (09/06/2026)

- **Hitos**: Servidor de imágenes estáticas FastAPI, descargas en segundo plano de bóveda con API de control, componente React MOTUImage con fallback automático a hotlink remoto, e integración de descargas en Configuración.
- **Estado**: COMPLETADO
- **Logros Técnicos**:
  - **Servidor de Estáticos en Backend**: Configurada e inicializada la ruta de montura `/api/static/images` usando `StaticFiles` en `main.py` de FastAPI para servir imágenes de disco local desde `data/image_cache`.
  - **APIs de Descarga en Bóveda**: Implementados tres nuevos endpoints en `vault.py`: `POST /api/vault/download-images` para iniciar una tarea asíncrona de descarga de imágenes en lote, `GET /api/vault/download-images/status` para monitorear el progreso (total, actual, errores, último error) y `POST /api/vault/download-images/cancel` para interrumpir el proceso de forma segura y consistente ante hilos concurrentes.
  - **Componente React MOTUImage**: Creado `MOTUImage.tsx` para interceptar la carga de imágenes. Lee la preferencia del localStorage (`use_local_images`). Si está activa, intenta cargar la imagen local `/api/static/images/{productId}.jpg` y, en caso de fallar o retornar error 404, cae inmediatamente al hotlink remoto original (onError fallback), previniendo imágenes rotas.
  - **Integración de Ajustes de Caché**: Añadida una tarjeta de control premium en la pestaña Ajustes de `Config.tsx` que permite activar/desactivar el caché local de imágenes y muestra el progreso de descarga de imágenes en tiempo real mediante una barra de progreso HSL/glassmorphism interactiva con botón de cancelación.
  - **Transición de Vistas del Frontend**: Reemplazadas las etiquetas `<img>` estándar por `<MOTUImage productId={...}>` en las páginas del Tablero (`Dashboard.tsx`), Catálogo (`Catalog.tsx`), Colección (`Collection.tsx`), Showcase Público (`Showcase.tsx`) y Vintage (`Vintage.tsx`).
"""
    with open("docs/narrative/LOG_MAESTRO_NUEVA_ETERNIA.md", "a", encoding="utf-8") as f:
        f.write(section)
    print("Updated LOG_MAESTRO_NUEVA_ETERNIA.md")

def update_architecture_map():
    path = "docs/technical/architecture_map.md"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update tests table
    target_tests = '| `tests/integration/test_api_showcase.py` | Integración (API) | Control de acceso y privacidad del Santuario (showcase público). |'
    replacement_tests = '| `tests/integration/test_api_showcase.py` | Integración (API) | Control de acceso y privacidad del Santuario (showcase público). |\n| `tests/integration/test_api_image_cache.py` | Integración (API) | Endpoints de descarga, estado y cancelación del caché local de imágenes. |'
    content = content.replace(target_tests, replacement_tests)

    # 2. Update interface description
    target_api = '  - `routers/vault.py` — `/api/vault/*`, `/api/excel/sync`.'
    replacement_api = '  - `routers/vault.py` — `/api/vault/*`, `/api/excel/sync`, `/api/vault/download-images/*`.\n  - Mount `/api/static/images` — montura de StaticFiles para servir imágenes locales desde data/image_cache.'
    content = content.replace(target_api, replacement_api)

    # 3. Update audit notes at the end
    target_audit = """- **Phase 67**: Optimización Extrema, Bypass de proxies en Amazon y Trazabilidad Operativa (09/06/2026):
  - Implementación de Lazy Keep-Alive en `App.tsx` para persistencia en memoria de pestañas y aceleración de transiciones a 0ms.
  - Refactorización de inputs de inversión en `CollectionItemDetailModal.tsx` (vacíos por defecto) y badges de compra en `Collection.tsx`.
  - Configuración de ScraperAPI con proxies residenciales en España (`premium=true`, `country_code=es`) para eludir bloqueos WAF en Amazon.es.
  - Sanitización robusta de comillas en la cadena de conexión de `database_cloud.py`.
  - Reducción de workers de Uvicorn a 1 en contenedores de producción para eliminar colisiones del receptor de Telegram.
  - Corrección de advertencias Node.js 20 en GitHub Actions (`ci.yml`).

*Última actualización: 2026-06-09 - Phase 67: Carga Instantánea, Proxies Premium Amazon y Resiliencia Operativa.*"""

    replacement_audit = """- **Phase 67**: Optimización Extrema, Bypass de proxies en Amazon y Trazabilidad Operativa (09/06/2026):
  - Implementación de Lazy Keep-Alive en `App.tsx` para persistencia en memoria de pestañas y aceleración de transiciones a 0ms.
  - Refactorización de inputs de inversión en `CollectionItemDetailModal.tsx` (vacíos por defecto) y badges de compra en `Collection.tsx`.
  - Configuración de ScraperAPI con proxies residenciales en España (`premium=true`, `country_code=es`) para eludir bloqueos WAF en Amazon.es.
  - Sanitización robusta de comillas en la cadena de conexión de `database_cloud.py`.
  - Reducción de workers de Uvicorn a 1 en contenedores de producción para eliminar colisiones del receptor de Telegram.
  - Corrección de advertencias Node.js 20 en GitHub Actions (`ci.yml`).

- **Phase 68**: Caché Local de Imágenes y Fallback Híbrido (09/06/2026):
  - Servidor de estáticos FastAPI en `/api/static/images` apuntando a `data/image_cache`.
  - APIs de descarga de imágenes en lote, estado y cancelación asíncrona segura en `routers/vault.py`.
  - Componente React `MOTUImage` con soporte para toggle `use_local_images` en localStorage y fallback instantáneo a hotlink original en error.
  - Integración de barra de progreso e interruptor en `Config.tsx`.
  - Reemplazo de etiquetas `<img>` estándar por `<MOTUImage>` en Showcase, Collection, Catalog, Vintage y Dashboard.
  - Creación de prueba de integración `test_api_image_cache.py` con cobertura completa del ciclo de vida de la descarga.

*Última actualización: 2026-06-09 - Phase 68: Caché Local de Imágenes y Fallback Híbrido.*"""

    content = content.replace(target_audit, replacement_audit)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated architecture_map.md")

def update_project_codex():
    path = "docs/narrative/PROJECT_CODEX.md"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = "*Última actualización: 09/06/2026 - Fase 67: Optimización Extrema, Bypass de proxies en Amazon y Trazabilidad Operativa.*"
    replacement = """### 13. Caché Local de Imágenes y Fallback Híbrido (Fase 68)

El ecosistema cuenta con un sistema híbrido de caché y descarga local de imágenes para las figuras del catálogo:
- **FastAPI Static Mount**: Montura de la ruta `/api/static/images` apuntando a `data/image_cache/` en FastAPI.
- **Background Downloader**: Tareas asíncronas en segundo plano en `vault.py` para descargar imágenes de productos, rastreando el progreso (conteo total, descargados, errores) y soportando cancelación segura.
- **Componente React MOTUImage**: Reemplazo de etiquetas `<img>` tradicionales por un componente con lógica de fallback. Intenta leer localmente si `use_local_images` está activo en localStorage. Si la carga falla (error 404/red), cambia instantáneamente al hotlink remoto original mediante el evento `onError` del navegador, garantizando consistencia visual absoluta y cero imágenes rotas.

*Última actualización: 09/06/2026 - Fase 68: Caché Local de Imágenes y Fallback Híbrido.*"""

    content = content.replace(target, replacement)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated PROJECT_CODEX.md")

def update_master_roadmap():
    path = "docs/MASTER_ROADMAP.md"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = """  - [x] **Prevención de conflictos de Telegram**: Reducción a 1 worker de Uvicorn en docker-compose para evitar errores de colisión 409 webhook/listener.
  - [x] **CI Actions (Node 20)**: Actualización de workflows de GitHub Actions para silenciar advertencias de obsolescencia.

---

## ✅ Plan de Verificación"""

    replacement = """  - [x] **Prevención de conflictos de Telegram**: Reducción a 1 worker de Uvicorn en docker-compose para evitar errores de colisión 409 webhook/listener.
  - [x] **CI Actions (Node 20)**: Actualización de workflows de GitHub Actions para silenciar advertencias de obsolescencia.

- [x] **Phase 68: Caché Local de Imágenes y Fallback Híbrido (09/06/2026)**
  - [x] **FastAPI Static Mount**: Montaje de StaticFiles en `/api/static/images` apuntando a `data/image_cache/` para servir imágenes locales de figuras.
  - [x] **APIs de Descarga**: Implementados endpoints de descarga en lote, status de progreso en tiempo real y cancelación en `vault.py`.
  - [x] **Componente React MOTUImage**: Creado componente con lógica de fallback automático. Intenta cargar del cache local de imágenes si está habilitado en localStorage (`use_local_images`), y recurre al hotlink remoto original en caso de fallo o error 404.
  - [x] **Integración en Configuración**: Tarjeta de ajustes en Configuración con toggle de habilitación de imágenes locales y barra interactiva de progreso de descarga con opción de cancelación.
  - [x] **Etiquetas de Imagen Actualizadas**: Swappeados los elementos `<img>` tradicionales por `<MOTUImage>` en Showcase, Collection, Catalog, Vintage y Dashboard.

---

## ✅ Plan de Verificación"""

    content = content.replace(target, replacement)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated MASTER_ROADMAP.md")

def update_documentacion_maestra():
    path = "docs/DOCUMENTACION_MAESTRA.md"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add variable to table
    target_table = """| `SUPABASE_DATABASE_URL` | Connection string a la base de datos maestra en la nube. | Requerida (Cloud) |"""
    replacement_table = """| `SUPABASE_DATABASE_URL` | Connection string a la base de datos maestra en la nube. | Requerida (Cloud) |\n| `IMAGE_CACHE_DIR` | Directorio local donde se guardarán las imágenes de productos (caché local). Por defecto data/image_cache. | Opcional |"""
    content = content.replace(target_table, replacement_table)

    # 2. Add bullet point to Notes for the Future
    target_notes = """- **Módulo Radar P2P**: El módulo Radar P2P ha sido desactivado del menú principal del frontend ya que actuaba como un visor independiente de oportunidades P2P (Teoría de Cuarentena P25) y no se le estaba dando uso continuo. El código subyacente (`RadarP2P.tsx` y endpoint `/api/radar/p2p-opportunities`) permanece en el proyecto por si se desea reactivar en el futuro, pero no interfiere con el flujo principal ni el enrutado de React."""
    replacement_notes = """- **Módulo Radar P2P**: El módulo Radar P2P ha sido desactivado del menú principal del frontend ya que actuaba como un visor independiente de oportunidades P2P (Teoría de Cuarentena P25) y no se le estaba dando uso continuo. El código subyacente (`RadarP2P.tsx` y endpoint `/api/radar/p2p-opportunities`) permanece en el proyecto por si se desea reactivar en el futuro, pero no interfiere con el flujo principal ni el enrutado de React.
- **Caché Local de Imágenes**: Para mejorar el rendimiento, el sistema cuenta con un caché local de imágenes (Phase 68) que se sirve a través de FastAPI en `/api/static/images`. Si se activa `use_local_images` en el frontend, se cargan estas imágenes locales con fallback automático en error al hotlink de origen."""
    
    content = content.replace(target_notes, replacement_notes)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated DOCUMENTACION_MAESTRA.md")

if __name__ == "__main__":
    update_3ox_log()
    update_log_maestro()
    update_architecture_map()
    update_project_codex()
    update_master_roadmap()
    update_documentacion_maestra()
    print("All docs updated successfully!")

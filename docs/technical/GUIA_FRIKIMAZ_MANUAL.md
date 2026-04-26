# 🦅 Guía de Incursión: Frikimaz.es

Esta guía detalla el funcionamiento del motor de búsqueda para **Frikimaz.es**, tienda española de figuras y coleccionables construida sobre PrestaShop.

---

## 🛠️ ¿Cómo funciona?

El motor de **Frikimaz** utiliza una estrategia de doble capa optimizada para plataformas PrestaShop con renderizado servidor:

1. **Infiltración Rápida (curl-cffi)**: Realiza la búsqueda directamente contra el endpoint `?controller=search&s=` de PrestaShop usando impersonación TLS Chrome120, sin necesidad de navegador real. Es la ruta de mínima latencia y máximo sigilo.
2. **Paginación Automática**: Itera por todas las páginas de resultados (`?page=N`) hasta agotar el catálogo o alcanzar el límite configurado, detectando la presencia del enlace `rel="next"` para determinar si hay más páginas.
3. **Extracción de Metadatos**: Por cada producto (`article.product-miniature`) captura:
   - **Nombre**: selector `h2.h3.product-title a`
   - **Precio**: selector `span.price` → normalizado al formato decimal europeo (`"25,99 €"` → `25.99`)
   - **Imagen**: primer `img` dentro de `a.thumbnail.product-thumbnail`
   - **URL**: `href` del enlace de miniatura
   - **Disponibilidad**: ausencia de la clase `li.product-flag.out_of_stock` en la tarjeta del producto
4. **EAN desde Página de Producto** _(deep harvest)_: Si se activa la extracción profunda, navega a la página del producto y localiza el EAN13 en la sección `section.product-features dl.data-sheet`, buscando el `dt.name` cuyo texto contenga `"ean"` y extrayendo el `dd.value` adyacente.
5. **Fallback Playwright**: Si curl-cffi falla (bloqueo o timeout), se activa un navegador Chromium headless con la misma lógica de paginación para garantizar la extracción.
6. **Depósito**: Los resultados se envían al Purgatorio para revisión del Arquitecto.

## 🔧 Selectores Técnicos

| Campo | Selector CSS | Notas |
| :--- | :--- | :--- |
| Contenedor de producto | `article.product-miniature` | Estándar PrestaShop 1.7+ |
| Nombre | `h2.h3.product-title a` | Texto del enlace |
| URL | `a.thumbnail.product-thumbnail[href]` | Absoluta |
| Precio | `span.price` | Texto: `"25,99 €"` |
| Imagen | `a.thumbnail.product-thumbnail img[src]` | URL directa |
| Sin stock | `li.product-flag.out_of_stock` | Presencia = agotado |
| EAN (producto) | `dl.data-sheet dt.name` + `dd.value` | Donde `dt` contiene `"ean"` |

## 🚀 Pasos para la Incursión

1. **Ejecución Manual**:
   - Desde el panel de **Configuración**, selecciona **Frikimaz**.
   - Introduce el término de búsqueda o deja el campo vacío para usar el término predefinido (`masters of the universe`).
2. **Revisión**: Comprueba en el Purgatorio los resultados extraídos y aprueba las vinculaciones sugeridas por SmartMatch.

## 🔁 Flujo Automático

Frikimaz forma parte del ciclo de escaneo diario (`daily_scan.py`), ejecutado automáticamente dos veces al día (02:00 UTC y 14:30 UTC) mediante GitHub Actions.

---

> [!NOTE]
> Frikimaz utiliza renderizado servidor (SSR) — no requiere JavaScript para cargar el catálogo, lo que hace que curl-cffi sea suficiente en la práctica y Playwright sea raramente necesario.

> [!TIP]
> Al ser PrestaShop, la estructura HTML es idéntica a DVDStoreSpain y Frikiverso. Los selectores son reutilizables entre estas tres fuentes.

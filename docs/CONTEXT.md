# 🏛️ Contexto de Dominio: Clasificación Multidivisión desde el Purgatorio

Este documento define el vocabulario de negocio, los conceptos y las restricciones técnicas relativas a la clasificación y creación manual de artículos desde el Purgatorio hacia las diferentes divisiones del catálogo del Oráculo.

---

## 1. Glosario de Términos

### Purgatorio (Purgatory)
Espacio temporal del Oráculo donde residen los artículos y ofertas escaneados de plataformas externas (Wallapop, eBay, etc.) que aún no han sido verificados ni vinculados a una figura del catálogo.

### Mazo (Card Stack)
Interfaz visual interactiva en forma de pila de tarjetas deslizables que permite tomar decisiones optimistas rápidas sobre los artículos del Purgatorio (aprobar, descartar, re-encolar, clasificar).

### Clasificación Manual (Custom Creation)
El proceso de coger un anuncio/artículo sin coincidencia exacta en el catálogo y crear un nuevo artículo independiente en el catálogo global con un nombre personalizado, vinculando inmediatamente el anuncio como su primera oferta activa.

### Divisiones del Catálogo
El catálogo del Oráculo se divide conceptualmente en dos secciones:
1. **Eternia Vintage**: Colección retro que incluye figuras clásicas de Masters of the Universe de los años 80. Se distingue técnicamente por tener la bandera `is_vintage = True` en el producto y en sus ofertas, y su subcategoría por defecto es `"Vintage"`.
2. **Nueva Eternia (Origins / Versión Actual)**: Colección moderna que incluye reliquias contemporáneas de MOTU (Origins, Masterverse, Turtles of Grayskull). Se distingue técnicamente por tener la bandera `is_vintage = False` (o `None`), y su subcategoría habitual es `"Origins"`.

---

## 2. Restricciones Técnicas del Dominio

1. **Campos del Modelo de Producto (`ProductModel`)**:
   * Para la división **Vintage**: el campo `is_vintage` es `True`. El nombre de la figura suele llevar la palabra " Vintage" al final (ej. `He-Man Vintage`). La subcategoría por defecto es `"Vintage"`. Su identificador único (`figure_id`) se genera con el formato `VINT-[4 dígitos aleatorios]`. Se inserta en la tabla auxiliar `vintage_products`.
   * Para la división **Nueva Eternia**: el campo `is_vintage` es `False`. El nombre de la figura se mantiene tal cual es introducido por el usuario sin añadir sufijos. La subcategoría por defecto es `"Origins"`. Su identificador único (`figure_id`) se genera con el formato `ORIG-[4 dígitos aleatorios]`. No se inserta en `vintage_products`.

2. **Ofertas asociadas (`OfferModel`)**:
   * Las ofertas deben heredar el estado de división del producto al que se vinculan. Si el producto es Vintage, la oferta debe tener `is_vintage = True`. Si es Nueva Eternia, `is_vintage = False`.

3. **Historial de Ofertas (`OfferHistoryModel`)**:
    * El registro en el historial de ofertas debe auditar la acción correctamente:
      * Para Vintage: `action_type = "LINKED_VINTAGE"`.
      * Para Nueva Eternia: `action_type = "LINKED_MANUAL"`.

---

## 3. Reglas de Fusión y Consolidación (Merge Rules)

Cuando se realiza la fusión de dos productos (un producto origen `source` absorbido por un producto destino `target`):

1. **Propagación de `is_vintage` en Ofertas**:
   * Las ofertas del producto origen se transfieren al producto destino.
   * Si el producto destino tiene `is_vintage = True` (Eternia Vintage), todas las ofertas transferidas deben actualizarse a `is_vintage = True`.
   * Si el producto destino tiene `is_vintage = False` o `None` (Nueva Eternia / Origins), todas las ofertas transferidas deben actualizarse a `is_vintage = False`.

2. **Área de Gestión Centralizada**:
   * El panel de administración para la gestión de fusiones se ubicará en la sección de **Configuración > Inventario** (`Config.tsx` bajo la pestaña `inventory`), accesible exclusivamente para usuarios con rol `admin` o usuario `David`.
   * Ofrecerá un listado directo de ítems temporales (con prefijo de `figure_id` `VINT-` u `ORIG-`) con sus correspondientes conteos de ofertas y pertenencias de colección para facilitar la consolidación.
   * Dispondrá de una herramienta de fusión libre que permita asociar de manera manual cualquier par de ítems del catálogo mediante buscadores interactivos de Origen y Destino.

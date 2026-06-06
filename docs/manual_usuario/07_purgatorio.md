# Manual del Usuario: 07. El Purgatorio de Ofertas

El **Purgatorio** es el espacio de cuarentena obligatorio al que llegan todas las ofertas nuevas que los scrapers extraen de internet y que el sistema no puede emparejar de forma 100% inequívoca (por ejemplo, anuncios que carecen de códigos EAN o que tienen descripciones ambiguas). 

*Esta sección está reservada exclusivamente para los usuarios con el rol de **Master (Administrador)**.*

---

## El Proceso de Clasificación

El objetivo del Purgatorio es limpiar la cola de ofertas pendientes para alimentar el catálogo con datos reales y actualizados. Al ingresar en el Purgatorio, verás una lista de ofertas pendientes. Para cada una de ellas puedes realizar tres acciones:

1.  **Clasificar (Vincular al Catálogo)**:
    Al hacer clic en el botón de vincular, se abre el **Panel de Emparejamiento** (Matching Drawer). El sistema utiliza el algoritmo `SmartMatch` para analizar el texto del anuncio y sugerir las figuras del catálogo más probables (por orden de relevancia semántica).
    *   *Si la sugerencia es correcta*: Haces clic en el botón verde de vinculación de esa sugerencia para asociar el anuncio a la figura. El anuncio desaparecerá del Purgatorio y se integrará en el historial de precios y ofertas activas de esa figura.
    *   *Búsqueda Manual*: Si el sistema no sugiere la figura correcta, dispones de una barra de búsqueda en tiempo real dentro del panel para buscar la figura exacta en el catálogo y vincularla manualmente.
2.  **Descartar / Ignorar**:
    Si la oferta es basura (por ejemplo, una playera de He-Man, pegatinas, réplicas no oficiales o un artículo con precio absurdo), puedes descartarla. Esto la elimina de la cola de clasificación.
3.  **Enviar a Miscelánea (Lotes o Varios)**:
    *(Nueva Característica)*:
    Si la oferta representa un lote de varios muñecos vintage o accesorios que no corresponden a una única figura, dispones del botón destacado **"Enviar a Miscelánea (Lote / Varios)"** dentro del modal de clasificación.
    *   Al pulsarlo, el sistema retira la oferta del Purgatorio y la guarda en la sección aislada de **Miscelánea Vintage**, registrando el movimiento correspondiente en el historial del sistema.

---

## Detalle del Motor de Coincidencia (SmartMatch)

El backend procesa las sugerencias empleando varios filtros de seguridad:
*   **Vetos**: Evita sugerir figuras modernas en búsquedas marcadas estrictamente como vintage y viceversa. Por ejemplo, si una oferta tiene la bandera `is_vintage`, el sistema bloquea sugerencias modernas.
*   **Lógica de Cercanía Semántica**: Emplea pesos de palabras clave (sabiendo que nombres como "Skeletor" o "He-Man" son más importantes que palabras genéricas como "Figura" o "Muñeco").

---

## Prevención y Limpieza Automática de Duplicados

Para reducir el trabajo manual redundante del administrador y mantener la cola de clasificación libre de ruido, el Oráculo cuenta con un sistema de pre-filtrado inteligente y un motor de limpieza automática:

### 1. Normalización Universal de URLs
Toda URL de oferta que entra al sistema —ya sea obtenida de forma automatizada por los scrapers de fondo o importada manualmente desde la extensión del navegador— se somete a un proceso de normalización universal (`normalize_url`). 
*   Este proceso remueve parámetros de tracking (como `?utm_source=...`), fragmentos (`#...`) y barras diagonales finales.
*   Al unificar el formato de las URLs, se evita que un mismo anuncio ingrese al Purgatorio varias veces bajo diferentes variantes de string y se previene que la base de datos lance fallos de inserción de claves únicas.

### 2. Filtro de Relevancia MOTU y Exclusión de Marcas
Antes de permitir el ingreso de cualquier oferta nueva al Purgatorio, el sistema realiza un examen de relevancia semántica (`validate_motu_relevance`) sobre el título del anuncio:
*   **Marcas Excluidas (Blacklist Absoluta)**: Si el título contiene términos como `funko`, `pop` (como palabra completa), `big jim` / `bigjim`, `masterverse`, `gi joe`, `star wars`, `action man`, `madelman`, `geyperman`, `max steel` o `barbie`, se descarta de forma inmediata.
*   **Filtro de Inclusión MOTU**: Para ser aceptada, la oferta debe contener palabras clave que la vinculen directamente al universo de Masters of the Universe (como `motu`, `he-man`, `skeletor`, `grayskull`, `origins`, `eternia`, `shera`, `hordak`, etc., incluyendo términos franceses tradicionales de coleccionista como `maitres de l'univers`).
*   **Permiso para Crossovers Oficiales**: Aquellas marcas que tradicionalmente serían descartadas pero que representan líneas oficiales crossover de Origins (como `transformers`, `thundercats`, `stranger things`, `tmnt` o `turtles`) **no** se descartan de forma absoluta, sino que se aprueban siempre y cuando vengan acompañadas de palabras clave de Masters del Universo.
*   **Descarte Automático Silencioso**: Todo anuncio que falle el filtro de relevancia o pertenezca a marcas excluidas se añade directamente a la lista negra (`blackcluded_items`) indicando el motivo detallado. Esto evita que los scrapers vuelvan a procesarlo y mantiene la bandeja de entrada completamente limpia.

### 3. Auto-Saneamiento Proactivo Global
La limpieza del Purgatorio no es solo pasiva. El sistema cuenta con una rutina de saneamiento global (`clean_purgatory_globally`):
*   **Eliminación de Redundancias**: Borra automáticamente de la tabla de pendientes (`PendingMatchModel`) cualquier URL que ya figure con una acción asignada (sea como oferta activa en el catálogo, en la lista negra, o en la sección de Miscelánea Vintage).
*   **Garantía de Visualización**: Esta rutina se ejecuta de forma proactiva al inicio y fin de cada actualización de scrapers, al finalizar importaciones desde la extensión, y de forma instantánea al recargar la pantalla del Purgatorio en la UI. De este modo, la bandeja de entrada de clasificación siempre se muestra perfectamente limpia y libre de residuos del pasado.


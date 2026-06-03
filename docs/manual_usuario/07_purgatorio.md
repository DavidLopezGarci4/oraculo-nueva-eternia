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

# Manual del Usuario: 05. Los Catálogos (Nueva Eternia y Eternia Vintage)

Los **Catálogos** constituyen el núcleo bibliográfico del Oráculo. En ellos se encuentra la lista de referencia oficial de todas las figuras lanzadas al mercado. El Oráculo divide los catálogos en dos vistas con lógicas de ordenación diferentes para adaptarse al comportamiento de coleccionismo de cada época:

1.  **Nueva Eternia**: Catálogo de figuras modernas (*Origins* y similares).
2.  **Eternia**: Catálogo de figuras vintage clásicas de los años 80.

---

## Estructura de un Producto en el Catálogo

Al acceder a cualquier figura del catálogo, la aplicación muestra una ficha técnica de referencia que reúne:
*   **Detalles Base**: Nombre oficial, Wave (oleada), año de lanzamiento original, número de producto (EAN/SKU) y fabricante (Mattel).
*   **Historial de Precios**: Gráfico interactivo que muestra la evolución del precio estimado a lo largo de los meses.
*   **Métricas de Mercado**:
    *   *MSRP (Retail)*: Precio recomendado de venta al público en tiendas oficiales.
    *   *Precio Medio del Mercado Secundario*: Calculado a partir del percentil 25 (P25) de las ofertas activas en el mercado P2P.
*   **Ofertas Activas**: Un listado de todas las ofertas que están a la venta actualmente en portales online (Wallapop, Vinted, eBay o tiendas de distribución) que han sido enlazadas a esta figura. Cada oferta muestra su precio, gastos de envío calculados, procedencia y un enlace de redirección directa al portal de venta original.

---

## Ordenación Híbrida Retro (Catálogo Eternia Vintage)

Para facilitar la caza de ofertas clásicas (ya que las figuras de los 80 tienen menos stock y son más difíciles de localizar), el catálogo de **Eternia Vintage** emplea un **Algoritmo de Ordenación Híbrida** en el backend. 

Este algoritmo coloca primero las figuras que representan un interés de acción inmediato mediante las siguientes tres reglas secuenciales:

1.  **Regla de Ofertas Activas (Prevalente)**:
    Cualquier figura del catálogo vintage que posea al menos una oferta activa a la venta en el mercado secundario (con precio P2P válido) se coloca en la parte superior del listado. Esto garantiza que las figuras que puedes comprar hoy lideren siempre la interfaz.
2.  **Regla de Coincidencias en el Purgatorio (Secundaria)**:
    Las figuras que no tienen ofertas activas validadas, pero que tienen ofertas sin clasificar esperando en el Purgatorio (`purgatory_match_count`), se muestran inmediatamente después, ordenadas de mayor a menor cantidad de coincidencias. Esto te avisa de qué figuras vintage están recibiendo mucho flujo en los portales pero aún no han sido aprobadas por el administrador.
3.  **Regla del ID (Orden Histórico/Fallback)**:
    Si hay empate (por ejemplo, múltiples figuras con 0 ofertas activas y 0 coincidencias en el Purgatorio), se ordenan de menor a mayor en base a su ID interno de base de datos (`id`), respetando el orden cronológico original con el que fueron catalogadas en el sistema.

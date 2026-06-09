# Manual del Usuario: 06. Ofertas Activas (El Pabellón) y Miscelánea Vintage

Este módulo agrupa la información comercial en tiempo real recopilada de los portales de venta. Se compone de dos secciones independientes adaptadas al tipo de producto detectado en internet:

---

## 1. El Pabellón

**El Pabellón** es el visor central de todas las ofertas que ya han sido vinculadas a una figura específica del catálogo (tanto Nueva Eternia como Eternia Vintage). 

### Funcionalidades clave:
*   **Buscador y Filtros Avanzados**:
    Permite filtrar los anuncios por palabra clave, rango de precios, procedencia (tiendas específicas o plataformas como Wallapop/Vinted) y por el estado de conservación del artículo anunciado (`MOC`, `LOOSE`, etc.).
*   **Filtro Solo Deseos (Wishlist Cross-Filter)**:
    Un botón premium con el icono de estrella (`[★ Solo Deseos]`) que permite filtrar de forma reactiva todas las ofertas y subastas activas para mostrar únicamente aquellas que coinciden con figuras marcadas en tu **Lista de Deseos** de la Fortaleza, ahorrándote tiempo de búsqueda manual y reduciendo el ruido en el pabellón.
*   **DealScore**:
    Cada tarjeta de oferta calcula un indicador numérico (del 1 al 100) que califica la oportunidad financiera. El cálculo tiene en cuenta el descuento frente al precio original (MSRP) y la diferencia frente a la media de precios de segunda mano recopilada por el sistema. Las ofertas con puntuaciones excelentes se destacan visualmente con bordes brillantes.
*   **Redirección Externa**:
    Cada oferta cuenta con un botón directo para abrir el anuncio original en la web externa, lo que facilita comprar el artículo de forma inmediata.

---

## 2. Miscelánea Vintage (Lotes y Varios)

A diferencia de las ofertas individuales enlazadas a un único muñeco de colección, en el coleccionismo clásico es sumamente habitual encontrar anuncios de "Lotes de figuras", "Packs familiares" o "Accesorios sueltos de Masters of the Universe" que no corresponden a un único registro del catálogo.

Para gestionar esto de forma limpia sin corromper las métricas de las figuras individuales, se ha introducido la sección **Miscelánea** dentro del área de **Eternia Vintage**.

### Características de Miscelánea Vintage:
*   **Destino Isolado**:
    Es un almacén para ofertas del Purgatorio que corresponden a lotes retro variados o anuncios que carecen de una ficha de catálogo única.
*   **Interfaz Glassmorphic**:
    Muestra los lotes en un listado especial con tarjetas premium que detallan el título del lote, el precio, la plataforma de procedencia (ej. Wallapop, eBay), la foto del lote y un enlace externo.
*   **Reversión al Purgatorio (Acción de Administrador)**:
    Si una oferta fue enviada a Miscelánea por error, o si más adelante se decide catalogar por separado sus figuras, los usuarios administradores (Master) disponen de un botón titulado **"Revertir"** (o icono de flecha de retorno color ámbar). Al pulsarlo, el backend extrae el lote de Miscelánea y lo recrea en la tabla de emparejamientos pendientes del Purgatorio para que pueda volver a ser evaluado.
*   **Eliminación Permanente (Acción de Administrador)**:
    Si la oferta no es de interés o es errónea, los administradores (Master) disponen de un botón de **"Eliminar"** (o icono de papelera roja). Al pulsarlo, el sistema solicita una doble confirmación de seguridad para evitar borrados accidentales antes de eliminar el registro de la base de datos de manera definitiva e irreversible.

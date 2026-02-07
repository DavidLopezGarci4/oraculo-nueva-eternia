# 🦅 Guía de Incursión: Electropolis

Esta guía explica el funcionamiento del motor de búsqueda para la tienda **Electropolis**.

---

## 🛠️ ¿Cómo funciona?

El motor de **Electropolis** utiliza selectores robustos para garantizar la precisión de los datos:

1.  **Identificación Robusta**: Utiliza atributos `data-price-amount` de Magento 2 para evitar ambigüedades en el precio.
2.  **Búsqueda Técnica**: El sistema es capaz de extraer el código EAN (GTIN13) directamente del JSON-LD de la página o de la pestaña de especificaciones técnicas.
3.  **Limpieza de DOM**: Cierra automáticamente banners de cookies para asegurar que los elementos de producto sean visibles antes de la captura.

## 🚀 Pasos para la Incursión

1.  **Operación**:
    - Ve al panel de **Configuración** > **Electropolis**.
    - Pulsa **"Lanzar Scraper"**.
2.  **Resultados**: El sistema procesará hasta 5 páginas de resultados por defecto.
3.  **Validación**: Comprobarás que muchos items se vinculan al instante gracias a la captura del EAN.

---

> [!NOTE]
> Electropolis suele tener stock de figuras que desaparecen rápido de las tiendas generalistas.

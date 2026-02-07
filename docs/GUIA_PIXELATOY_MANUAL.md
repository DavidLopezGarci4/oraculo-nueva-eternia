# 🦅 Guía de Incursión: Pixelatoy

Esta guía detalla el funcionamiento del motor de búsqueda para **Pixelatoy**, recientemente optimizado.

---

## 🛠️ ¿Cómo funciona?

El motor de **Pixelatoy** utiliza una estrategia de navegación por categorías para máxima eficiencia:

1.  **Acceso Directo**: Navega por la categoría de **Masters del Universo** por defecto para saltar las debilidades del buscador interno.
2.  **Extracción PrestaShop**: Utiliza selectores de alta precisión basados en atributos `content` para capturar precios exactos en EUR.
3.  **Identificación Técnica**: Extrae el código SKU/Referencia de la página de detalle para asegurar un match perfecto en el catálogo.
4.  **Resiliencia**: Implementa una espera activa de 10s para asegurar que el DOM de productos esté totalmente renderizado.

## 🚀 Pasos para la Incursión

1.  **Activación**:
    - Ve a **Configuración** > **Pixelatoy**.
    - El término "auto" disparará el escaneo de la categoría MOTU completa (~120 items).
2.  **Control**: Revisa los logs en tiempo real para ver el progreso página a página.
3.  **Validación**: Los items vinculados aparecerán instantáneamente en Nueva Eternia.

---

> [!IMPORTANT]
> Tras la última actualización, Pixelatoy ha pasado de 0 a 120 items detectables, convirtiéndose en una fuente crítica de stock.

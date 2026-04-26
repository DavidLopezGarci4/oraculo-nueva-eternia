# 🦅 Guía de Incursión: Action Toys

Esta guía detalla el funcionamiento del motor de búsqueda para **Action Toys** dentro del ecosistema de Nueva Eternia.

---

## 🛠️ ¿Cómo funciona?

El motor de **Action Toys** utiliza una estrategia de infiltración directa basada en protocolos HTTP ligeros.

1.  **Infiltración**: Realiza peticiones asíncronas a la URL de búsqueda de la tienda.
2.  **Extracción**: Analiza el DOM buscando contenedores de producto específicos de su plataforma.
3.  **Identificación**: Captura el nombre, precio y disponibilidad.
4.  **Procesamiento**: Los hallazgos se depositan en el Purgatorio para su validación definitiva.

## 🚀 Pasos para la Incursión

1.  **Escaneo Diario**: El sistema inicia automáticamente la incursión cada día vía GitHub Actions.
2.  **Disparador Manual**:
    - Ve al panel de **Configuración** en el Oráculo.
    - Selecciona **Action Toys**.
    - Ingresa el término (ej: "origins") y pulsa **"Lanzar Scraper"**.
3.  **Validación**: Revisa los resultados en el **Purgatorio**.

---

> [!TIP]
> Action Toys es una de las fuentes más rápidas del sistema por su bajo peso en el renderizado del DOM.

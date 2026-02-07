# 🦅 Guía de Incursión: Toymi

Esta guía explica el funcionamiento del motor de búsqueda para la tienda **Toymi**.

---

## 🛠️ ¿Cómo funciona?

El motor de **Toymi** opera mediante una infiltración directa en su buscador interno:

1.  **Búsqueda Táctica**: Realiza peticiones asíncronas para el término "Master of the Universe".
2.  **Captura de Datos**: Extrae el nombre, precio y URL de la imagen de cada figura.
3.  **Determinación de Stock**: Verifica los indicadores de disponibilidad de la plataforma para evitar falsos positivos.
4.  **Validación**: Los hallazgos se envían al Purgatorio para su revisión manual.

## 🚀 Pasos para la Incursión

1.  **Lanzamiento**:
    - Desde el panel de **Configuración**, selecciona **Toymi**.
    - Pulsa el botón de ejecución del scraper.
2.  **Seguimiento**: Observa los niveles de `SUCCESS` en los logs del Oráculo.
3.  **Revisión**: Valida los vínculos sugeridos por el SmartMatch en el Purgatorio.

---

> [!NOTE]
> Toymi es una excelente fuente de redundancia para confirmar precios de mercado en España.

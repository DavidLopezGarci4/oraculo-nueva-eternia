# 🦅 Guía de Incursión: DVD Store Spain

Esta guía detalla el funcionamiento del motor de búsqueda avanzado para **DVD Store Spain**.

---

## 🛠️ ¿Cómo funciona?

El motor utiliza la estrategia **Eternia Shield (Sitemap Fallback)** debido a la inestabilidad del buscador interno de la web:

1.  **Búsqueda Dual**: Intenta la búsqueda por término y, si falla, recurre a la sección directa de MOTU Origins.
2.  **Extracción de Alta Fidelidad**: Captura el EAN (código de barras) siempre que esté disponible para lograr un match del 100%.
3.  **Procesamiento**: Detecta etiquetas de "Preventa" o "Agotado" para ajustar la disponibilidad en tiempo real.

## 🚀 Pasos para la Incursión

1.  **Ejecución**:
    - Desde el panel de **Configuración**, selecciona **DVDStoreSpain**.
    - El disparador manual usará el término predefinido para máxima precisión.
2.  **Revisión**: Comprueba en el Purgatorio las vinculaciones automáticas por EAN.

---

> [!IMPORTANT]
> DVD Store Spain es una de las fuentes más fiables para la vinculación automática gracias a la presencia constante de identificadores EAN.

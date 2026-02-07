# 🦅 Guía de Incursión: BigBadToyStore (BBTS)

Esta guía detalla el funcionamiento del motor de búsqueda para la incursión transatlántica en **BBTS**.

---

## 🛠️ ¿Cómo funciona?

El motor de BBTS está optimizado para la captura de stock internacional y precisión en el cálculo logístico:

1.  **Acceso de Sigilo**: Usa Playwright para eludir las protecciones de CloudFront mediante rotación de User-Agents.
2.  **Paginación Táctica**: Recorre hasta 25 páginas de catálogo para asegurar que ninguna preventa o grial sea ignorado.
3.  **Extracción Pura**: Utiliza selectores BeautifulSoup para una extracción de alta fidelidad una vez cargado el DOM.
4.  **Lógica Logística**: Los precios se marcan para el cálculo de **Landed Price** (Envío USA + Aduanas).

## 🚀 Pasos para la Incursión

1.  **Configuración**: Accede al panel en el Oráculo.
2.  **Disparo**: Selecciona **BBTS** y lanza el escaneo.
3.  **Interpretación**: Los precios aparecerán en USD originalmente pero el sistema los normalizará a EUR en el Purgatorio.

---

> [!TIP]
> BBTS es ideal para detectar preventas de figuras que aún no han llegado a Europa.

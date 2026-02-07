# 🦅 Guía de Incursión: eBay.es

Esta guía detalla el funcionamiento del motor de búsqueda masiva para **eBay España**, especializado en el mercado de coleccionistas.

---

## 🛠️ ¿Cómo funciona?

El motor de eBay utiliza la estrategia **Sirius-E**, diseñada para capturas de alto volumen:

1.  **Infiltración Rápida**: Comienza con protocolos ligeros (curl-cffi) para una captura veloz.
2.  **Escalamiento Táctico**: Si la infiltración rápida falla, escala automáticamente a **Playwright Nexus**.
3.  **Filtrado de Pureza**: Clasifica automáticamente los ítems como `Peer-to-Peer` y distingue entre anuncios de precio fijo (`Fixed_P2P`) y subastas (`Auction`).
4.  **Cálculo de Envío**: Extrae el coste logístico de cada anuncio para calcular el precio total real.

## 🚀 Pasos para la Incursión

1.  **Activación Permanente**: El sistema monitoriza eBay a intervalos regulares.
2.  **Lanzamiento Manual**:
    - Selecciona **Ebay.es** en el panel de **Configuración**.
    - Ingresa el término (ej: "origins") o usa "auto" para el escaneo de catálogo maestro.
3.  **Validación**: Los resultados fluyen directamente hacia **"El Pabellón"** e incluyen el número de pujas activas.

---

> [!TIP]
> eBay es la fuente principal para encontrar griales y variantes que ya no están disponibles en tiendas retail.

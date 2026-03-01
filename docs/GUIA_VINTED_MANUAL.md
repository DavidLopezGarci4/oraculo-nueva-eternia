# 🦅 Guía de Incursión: Vinted

Esta guía explica el funcionamiento del motor de búsqueda para el mercado **Peer-to-Peer** de Vinted.

---

## 🛠️ ¿Cómo funciona?

El motor de Vinted utiliza una estrategia de infiltración vía API interna para máxima velocidad:

1. **Warm-up de Cookies**: Visita la home para obtener los tokens de sesión necesarios.
2. **Consulta de API**: Realiza peticiones directas al catálogo v2 de Vinted, evitando la carga pesada de interfaces visuales.
3. **Filtrado P2P**: Marca automáticamente todos los hallazgos como `Peer-to-Peer` para su visualización en **"El Pabellón"**.
4. **Preservación**: El sistema mantiene la fecha de publicación y el estado del artículo para ayudar en la toma de decisiones.
5. **Refugio de Valor (Teoría de Cuarentena)**: Todos los precios extraídos de este mercado secundario se comparan con el límite inferior histórico (**Percentil 25**) y operan en **cuarentena**, es decir, no promedian ni afectan a la baja la tasación patrimonial oficial de tu colección en Mi Legado.

## 🚀 Pasos para la Incursión

1. **Monitorización**: El sistema escanea Vinted automáticamente en busca de nuevas ofertas.
2. **Búsqueda Manual**:
    - Selecciona **Vinted** en el panel de **Configuración**.
    - Ingresa el término de búsqueda (ej: "he-man origins").
3. **Revisión**: Los resultados aparecerán en el Purgatorio resaltados como items de subasta/segunda mano.

---

> [!TIP]
> Vinted es ideal para encontrar lotes o figuras sueltas (loose) a precios significativamente inferiores al retail.

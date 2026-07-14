# 🦅 Guía de Incursión: Wallapop Automático (Elite Scan)

Esta guía detalla el funcionamiento del motor de búsqueda masiva automatizada para **Wallapop**.

---

## 🛠️ ¿Cómo funciona?

A diferencia de la importación manual, el **Elite Scan** de Wallapop utiliza una cascada de bypass en varios niveles (Apify → **API v3 Firmada** → ScraperAPI → Proxies → **Playwright Nexus**):

1. **Bypass Estructural**: Salta la protección 403 mediante la simulación de navegación humana compleja (nivel Playwright) o mediante firma real `X-Signature` de la API v3 (nivel intermedio, sin gastar créditos de pago — ver `docs/GUIA_TECNICA_WALLAPOP_NEXUS.md`).
2. **Expansión Infinitia**: Realiza scrolls profundos e interactúa con el botón "Cargar más" para extraer hasta **150+ items** por incursión.
3. **Ruteo P2P**: Los datos fluyen con su ADN de subasta preservado directamente hacia **"El Pabellón"**.
4. **Inteligencia de Precios**: El sistema extrae el precio del artículo y lo separa de los costes de gestión de Wallapop para una comparación pura.
5. **Refugio de Valor (Teoría de Cuarentena)**: Todas las ofertas detectadas por el escaneo masivo son contrastadas contra el **Percentil 25** histórico. Su tasación no afecta a la baja al valor acumulado de tu colección, aislando la volatilidad de los remates entre particulares.

## 🚀 Pasos para la Incursión

1. **Ciclo Diario**: Se ejecuta automáticamente dos veces al día para capturar las novedades del mercado.
2. **Configuración**:
    - Selecciona **Wallapop** en el panel administrativo.
    - Asegura que el término de búsqueda coincida con los intereses de la colección.
3. **Resultados**: Supervisa los hallazgos en la sección de subastas del oráculo.

---

> [!IMPORTANT]
> Esta guía se refiere al scraper automático de sistema. Para importar anuncios específicos uno a uno, utiliza la [Guía de Captura Manual](file:///c:/Users/dace8/OneDrive/Documentos/Antigravity/oraculo-nueva-eternia/docs/GUIA_WALLAPOP_MANUAL.md).

> [!NOTE]
> Existe además un spider **"WallapopManual"** disparable desde el panel de Configuración
> (`spider_name="WallapopManual"`), pensado como alternativa cuando las cuotas gratuitas de
> Apify se agotan. Usa la misma API v3 firmada que el Nivel 1.5 del Elite Scan automático,
> pero se ejecuta bajo demanda en vez de esperar al cascade completo. Ver
> `docs/technical/PLAN_WALLAPOP_NEXUS_LOCAL.md` para la arquitectura completa.

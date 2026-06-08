# Auditoría de Telemetría e Integración del Bot de Telegram (08/06/2026)

Este documento realiza un estudio técnico y de utilidad sobre el flujo de datos del bot de Telegram (`@DacemanBot` / *Nueva_Eternia*) tras la integración del bot bidireccional y las alertas multi-usuario. Su propósito es servir de base para evaluar si cada funcionalidad es útil o debe ser descartada para evitar sobrecarga o fatiga en el canal.

---

## 📊 1. Estudio del Flujo y Uso de Datos

La integración de Telegram genera dos flujos de datos principales (Salida/Notificaciones y Entrada/Comandos). A continuación, analizamos su impacto técnico:

### A. Consumo de API y Ancho de Banda
*   **Long Polling (Escucha de Comandos)**: El loop asíncrono realiza una petición `getUpdates` cada 2-5 segundos.
    *   *Tráfico diario*: Aprox. 20,000 llamadas HTTP. La inmensa mayoría devuelven un JSON vacío (`{"ok":true,"result":[]}`) con un peso inferior a 50 bytes por petición, lo que representa menos de **1 MB de tráfico diario**.
    *   *Límite de la API*: Telegram no limita las peticiones de `getUpdates` vacías, por lo que el riesgo de rate-limiting por parte del servidor de Telegram en este flujo es nulo.
*   **Envío de Alertas (`sendMessage`)**:
    *   *Tráfico promedio*: Estimado en 5-15 mensajes diarios dependiendo de la frecuencia de scraping de Wallapop/eBay.
    *   *Peso*: Aprox. 1.2 KB por mensaje (debido a las etiquetas HTML y las URLs de los enlaces).

### B. Relación Señal/Ruido y Fatiga del Canal
*   **Alertas de Alta Precisión (Wishlist / Price Alerts)**: 
    *   *Ruido*: **Muy bajo**.
    *   *Explicación*: Al estar filtradas estrictamente por palabras clave de figuras deseadas o precios objetivo inferiores a los de mercado, solo se disparan ante coincidencias reales.
*   **Alertas de Candidatos Vintage en el Purgatorio**:
    *   *Ruido*: **Alto**.
    *   *Explicación*: Al enviar *cualquier* figura o lote clásico no vinculado a revisión, si el scraper de Wallapop se ejecuta con búsquedas genéricas, podría inundar el chat del administrador con decenas de alertas repetitivas de ítems sin interés real.

---

## 💾 2. Esquema de Registro de Telemetría

Para auditar y estudiar el uso del bot, el sistema registra cada evento en formato JSON en la ruta:
[telegram_telemetry.json](file:///c:/Users/dace8/OneDrive/Documentos/Antigravity/oraculo-nueva-eternia/data/telegram_telemetry.json) (con un tope de 1,000 registros rotativos).

### Formato de Entrada de Datos:
```json
{
  "timestamp": "2026-06-08T09:12:45.781Z",
  "event_type": "MESSAGE_SENT",
  "payload": {
    "chat_id": "7931331",
    "text_preview": "<b>🔔 Test de Conexión del Oráculo</b>\n\nEl sistema de alertas de..."
  }
}
```

---

## ⚖️ 3. Matriz de Utilidad vs. Descarte

Esta tabla clasifica las funcionalidades para evaluar su continuidad tras un periodo de prueba de 15 días:

| Funcionalidad / Alerta | Usuario Destinatario | Impacto en Datos | Relación Beneficio/Ruido | Acción Recomendada (Plan de Pruebas) |
| :--- | :--- | :--- | :--- | :--- |
| **`/register`** | Guardianes | Despreciable | Excelente | **MANTENER**: Es el único método seguro para que un nuevo guardián se autoregistre sin tocar el archivo `.env`. |
| **`/purgatorio`** | Todos | Despreciable | Alto | **MANTENER**: Evita entrar a la web para comprobar si hay trabajo pendiente de vinculación. |
| **`/buscar`** | Todos | Medio | Alto | **MANTENER**: Permite una consulta rápida de stock y precios locales desde el móvil en movilidad. |
| **`/run` / `/stop`** | Administradores | Despreciable | Medio | **EVALUAR**: Útil para lanzar/parar scrapers en remoto, pero puede descartarse si se prefiere controlar 100% desde la web. |
| **Alertas Wishlist** | Todos | Bajo | Excelente | **MANTENER**: Avisa a los guardianes en tiempo real del stock que buscan activamente. |
| **Alertas Precio** | Todos | Bajo | Excelente | **MANTENER**: Es la esencia del sistema de inversión del Centinela. |
| **Alertas Vintage Purgatorio** | Administrador | Alto | Medio-Bajo | **LIMITAR / DESCARTAR**: Si genera más de 10 notificaciones por ciclo de scraping, se aconseja migrar a un reporte resumen diario en lugar de alertas individuales instantáneas. |

---

## 🛠️ 4. Criterios de Descarte y Modificación

Para actuar frente a los datos recogidos en `telegram_telemetry.json`:
1.  **Regla de Silencio (Spam Gate)**: Si un usuario recibe más de 5 alertas de wishlist en menos de 10 minutos para el mismo producto, el servicio enmudecerá alertas similares durante las siguientes 2 horas.
2.  **Desactivación Rápida**: Si deseas desactivar por completo la escucha de comandos sin reiniciar la API, puedes enviar el comando `/stop` (como administrador) o quitar temporalmente las variables del `.env`.

# Preguntas Frecuentes y Guía de Herramientas (FAQ) - Oráculo de Nueva Eternia

> Guía de referencia rápida y resolución de dudas sobre todas las funciones y herramientas activas en la versión actual de la app.

---

## Índice Rápido
1. [Mi Fortaleza & Gestión de Colección](#1-mi-fortaleza--gestión-de-colección)
2. [Nueva Eternia & Catálogo Maestro](#2-nueva-eternia--catálogo-maestro)
3. [Alertas Push de Telegram & El Ojo de Sauron](#3-alertas-push-de-telegram--el-ojo-de-sauron)
4. [Centinela Autónomo & Caza en Vinted](#4-centinela-autónomo--caza-en-vinted)
5. [El Purgatorio & Vinculación de Ofertas](#5-el-purgatorio--vinculación-de-ofertas)
6. [Seguridad, Dispositivos & Ajustes](#6-seguridad-dispositivos--ajustes)

---

## 1. Mi Fortaleza & Gestión de Colección

### ¿Cómo aseguro una figura en mi colección o lista de deseos?
* **Asegurar en la Fortaleza:** Pulsa el botón con icono de verificación `✓ En Sanctum` o el lateral de la tarjeta en el Catálogo para confirmar que ya posees la figura física.
* **Lista de Deseos:** Pulsa el icono de la estrella `☆ Deseo` para seguir una figura en tu radar de compras pendientes.
* **Liberar o Desvincular:** Si vendes o retiras una figura, al pasar el cursor o pulsar sobre el botón de posesión cambiará a `Liberar`, removiéndola inmediatamente de tu búnker.

### ¿Qué es el Modo Incógnito y cómo se activa?
* **Propósito:** Oculta y difumina instantáneamente todos los precios de compra, valoraciones financieras y totales coleccionados.
* **Activación:** Pulsa el icono del ojo `👁️` en la barra superior (Navbar) de la app.
* **Protección:** Ideal para capturas de pantalla, grabaciones o para mostrar tu colección a terceros sin revelar tu inversión monetaria.

### ¿Cómo puedo exportar mi inventario?
* **Exportación a Excel:** Pulsa el botón verde `📥 Excel` en la cabecera de Mi Fortaleza para descargar una hoja de cálculo con nombres, estados, valoraciones y costes.
* **Bóveda SQLite:** Pulsa el botón `🗄️ SQLite` para generar un volcado portátil en base de datos relacional estándar de tu inventario.

---

## 2. Nueva Eternia & Catálogo Maestro

### ¿Cómo busco figuras por su identificador numérico (ID)?
* **Búsqueda por ID:** Escribe el número en el buscador superior (por ejemplo `12033` o `#12033`). El catálogo filtrará al instante a 0ms la figura correspondiente.
* **Búsqueda por Nombre o Sub-categoría:** Puedes combinar búsquedas por nombre de personaje (ej. `He-Man`, `Skeletor`) o por línea (`Origins`, `Turtles of Grayskull`).

### ¿Cómo funciona la ordenación simétrica de la barra de controles?
* **Botón NOM:** Ordena el catálogo alfabéticamente por el nombre canónico de la figura.
* **Botón ID:** Ordena las piezas cronológica y numéricamente por su identificador único de base de datos.
* **Botón OFERTAS:** Prioriza las figuras que cuentan con oportunidades activas o coincidencias en el Purgatorio.
* **Botón SET:** Ordena según el porcentaje de completitud de la sub-categoría a la que pertenece la pieza.
* **Alternar Sentido:** Pulsa la flecha `↑` o `↓` para conmutar entre orden ascendente y descendente.

### ¿Cómo utilizo el Comparador Cronos de precios?
* **Acceso:** En la vista del Catálogo, selecciona la pestaña `Cronos` en la barra de sub-navegación.
* **Comparación Dual:** Selecciona dos figuras para comparar en un gráfico de líneas sus evoluciones de precios y diferenciales de mercado.
* **Filtrado por Tiendas:** Puedes activar o silenciar tiendas específicas (Wallapop, Vinted, Smyths, eBay) para aislar curvas de precios.

---

## 3. Alertas Push de Telegram & El Ojo de Sauron

### ¿Cómo configuro para recibir SOLO alertas de figuras que NO tengo?
* **Desde la App Web:** Ve a **Configuración** (`Ajustes`), localiza la tarjeta **Alertas Push de Telegram** y activa el interruptor `Solo Figuras NO Poseídas`.
* **Desde el móvil por Telegram:** Envía el comando `/alertas` a tu bot de Telegram y pulsa el botón interactivo inline para alternar el filtro.
* **Resultado:** Se silenciarán automáticamente todas las alertas de compras obligatorias y chollos para piezas que ya consten como aseguradas en tu Fortaleza.

### ¿Qué tipos de alertas automáticas envía el bot?
* **🚨 Compras Obligatorias:** Oportunidades excepcionales con Opportunity Score de 90+ puntos y alto descuento respecto a mercado.
* **⭐ Lista de Deseos:** Notificación instantánea cuando se detecta a la venta una figura que tienes marcada en deseos.
* **🎯 Precio Objetivo:** Alerta personalizada si el precio de una figura cae por debajo del umbral que fijaste en El Centinela.
* **🔥 Gangas de Vinted:** Notificaciones de incursiones del cazador autónomo cuando el coste total (Landed Price) es inferior al precio de referencia.

---

## 4. Centinela Autónomo & Caza en Vinted

### ¿Qué es el Centinela de Vinted y cómo trabaja?
* **Incursiones 24/7:** Ejecuta batidas automáticas a intervalos aleatorios de 100 a 120 minutos para eludir bloqueos.
* **IP Rotatoria:** Opera a través de proxys y entornos protegidos para consultar el mercado de segunda mano en tiempo real.
* **Landed Price Real:** Calcula el coste final sumando precio de producto + gastos de envío (5,00€) + tasa de seguro de comprador (2%).

### ¿Cómo lanzo una incursión de caza manual?
* **Caza Canónica:** Envía `/caza` por Telegram para rastrear las 4 familias principales de Masters of the Universe.
* **Caza Específica:** Envía `/caza [nombre]` (ej. `/caza trap jaw origins`) para buscar una figura puntual.
* **Pausar o Reanudar:** Usa `/centinela on` o `/centinela off` para controlar el piloto automático.

---

## 5. El Purgatorio & Vinculación de Ofertas

### ¿Qué es el Purgatorio y por qué van ofertas allí?
* **Cámara de Validación:** Las ofertas extraídas por scrapers que no alcanzan un 90% de coincidencia automática se depositan en el Purgatorio para revisión humana.
* **Protección Vintage Estricta:** Ninguna figura o lote de los años 80 se vincula automáticamente al catálogo; todas pasan obligatoriamente por el Purgatorio para garantizar rigor histórico.
* **Emparejamiento Rápido:** Puedes pulsar `Vincular` para asociar la oferta a la figura correcta del catálogo o `Bloquear` para enviarla a la lista negra permanente.

---

## 6. Seguridad, Dispositivos & Ajustes

### ¿Cómo autorizo un nuevo dispositivo o navegador?
* **Alerta Soberana:** Al iniciar sesión desde un nuevo navegador, el sistema enviará un mensaje con botones `[ ✅ Permitir ]` y `[ 🚫 Bloquear ]` a tu Telegram.
* **Gestión de Dispositivos:** Puedes auditar y revocar huellas dactilares autorizadas en la pestaña **Dispositivos** de Configuración o con `/devices` en Telegram.

### ¿Cómo se gestionan los certificados SSL (HTTPS)?
* **Guardián Automatizado:** El servidor comprueba diariamente la caducidad del certificado Let's Encrypt para `oraculo-eternia.duckdns.org`.
* **Renovación Anticipada:** Si faltan 14 días o menos para expirar, GitHub Actions o el backend ejecutan la renovación remota por SSH.
* **Diagnóstico Remoto:** Puedes escribir `/ssl` en Telegram para conocer los días restantes de validez o `/renew_ssl` para forzar la renovación inmediata.

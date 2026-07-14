# 🦅 Guía de Incursión Asistida: Wallapop CDP (Chrome DevTools Protocol)

Esta guía documenta el uso del script de PowerShell `run_wallapop_attached.ps1`, el cual permite realizar búsquedas y extracciones en **Wallapop** de manera sigilosa y resiliente usando tu propia ventana de Google Chrome.

---

## 🛠️ ¿Por qué usar este método?

Debido a que Wallapop implementa cortafuegos (WAF) y capas de seguridad de CloudFront sumamente agresivas, las consultas automatizadas directas desde servidores web en la nube suelen ser bloqueadas con errores `403 Forbidden` o solicitudes de CAPTCHA.

Al utilizar el **Chrome DevTools Protocol (CDP)**, el Oráculo se conecta a una ventana de Chrome **real** en tu máquina local. Esto permite:
1. Utilizar tu **IP residencial** legítima (no la de un hosting/VPS).
2. Aprovechar tu **sesión activa** y tus cookies de navegación.
3. Simular navegación humana pura y scroll táctico en tiempo real.
4. **Cero costes**: Al usar tu propio navegador, no consumes cuotas de proxies de pago ni créditos de Apify.

---

## 🚀 Pasos para realizar la Incursión

Sigue estos pasos ordenadamente desde tu sistema Windows:

### Paso 1: Cerrar todas las ventanas de Google Chrome
Para activar el puerto de depuración, Chrome no debe tener ningún proceso en segundo plano activo en el puerto estándar. Cierra Google Chrome por completo.

### Paso 2: Lanzar Chrome en Modo Depuración
Abre una terminal de **PowerShell** en la carpeta del proyecto y ejecuta el script preparador:
```powershell
.\launch_chrome_debug.ps1
```
*Este script abrirá una ventana de Chrome especial configurada para escuchar peticiones en el puerto `9222` con un perfil aislado en `C:\temp\chrome_dev`.*

### Paso 3: Navegar y Preparar las Búsquedas
En la ventana de Chrome que se acaba de abrir, entra a Wallapop y abre una o varias de las búsquedas que te interese monitorizar (ordenadas por novedades para captar los remates más rápidos):
*   [Masters del Universo Origins en Wallapop](https://es.wallapop.com/search?keywords=masters+del+universo+origins&order_by=newest)
*   [MOTU Origins en Wallapop](https://es.wallapop.com/search?keywords=motu+origins&order_by=newest)
*   [Masters of the Universe Origins en Wallapop](https://es.wallapop.com/search?keywords=masters+of+the+universe+origins&order_by=newest)

### Paso 4: Ejecutar la Extracción
Vuelve a tu terminal de PowerShell en la carpeta del proyecto y lanza el script de inyección asistida:
```powershell
.\run_wallapop_attached.ps1
```

---

## 📈 ¿Qué hace el script por debajo?

1. **Conexión CDP**: Se conecta al puerto local `9222` y detecta todas las pestañas abiertas que coincidan con búsquedas de Wallapop.
2. **Scroll Táctico**: Realiza de forma automática scrolls progresivos para cargar las imágenes y los anuncios diferidos (lazy load).
3. **Parseo Resiliente**: Ejecuta un script de JS en el DOM del navegador del usuario que extrae el título, precio original, enlace e imagen del artículo sin depender de clases CSS dinámicas.
4. **Filtrado de Ruido (Junk Clean)**: Filtra automáticamente palabras clave de ruido como *camisetas*, *pósters*, *tazas*, *fundas*, etc.
5. **Inyección en el Purgatorio**: Envía los anuncios válidos directamente hacia el **Purgatorio** (Supabase/Producción) con la marca de tipo `Peer-to-Peer`, listos para que los vincules manualmente en el Oráculo.

---

> [!TIP]
> Puedes dejar las pestañas preparadas en esa ventana especial de Chrome y simplemente ejecutar `.\run_wallapop_attached.ps1` cuando quieras capturar las novedades del día.

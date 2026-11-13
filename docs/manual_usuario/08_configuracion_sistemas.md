# Manual del Usuario: 08. Configuración de Sistemas

El panel de **Configuración** reúne tanto las preferencias personales de cada coleccionista como la cabina de control técnico del Oráculo.

*   **Vista `Guardián` (Coleccionista):** Accede directamente a una vista despejada de **Ajustes Personales** (sin botonera administrativa), con control sobre su Santuario Público, país para cálculo de envíos (*Landed Price*), caché local de imágenes en el navegador, efectos visuales 3D y la píldora **`Acerca de & Novedades`** en la cabecera.
*   **Vista `Master` (Administrador):** Desbloquea la **botonera superior de 6 pestañas** (*Ajustes, Scrapers, Inventario, Héroes, Grimorio Lore y Cromos TCG*), los controles globales del servidor (`Shield Layer 2`) y el visor interactivo **`TecnoRed v2.0`**.

---

## 1. Gestión de Héroes (Usuarios)

En esta pestaña se listan todos los usuarios ("Héroes") registrados en el Oráculo. Los administradores pueden:
*   **Crear Nuevos Usuarios**: Registrar a un coleccionista asignándole un nombre de usuario, correo electrónico, rol (`Guardián` o `Master`) y una contraseña inicial.
*   **Modificar Roles (Estilo Outline)**: Ascender o degradar roles directamente. La interfaz visualiza el rango de forma homogeneizada usando los iconos outline monocromáticos `Swords` (Maestro) y `Shield` (Guardián) en lugar de emojis coloridos para encajar con el diseño premium de la aplicación.
*   **Eliminar Cuentas**: Revocar el acceso de forma definitiva a cualquier usuario del sistema.

---

## 2. Centro de Mando: Telemetría FinOps y Control de Arañas

El Oráculo extrae información comercial mediante un conjunto de arañas web automatizadas (`scrapers`) y runners efímeros en la nube que simulan navegación humana para evitar bloqueos.

### 2.1 Cuota de Ejecución en la Nube (GitHub Actions)
En la parte superior de la pestaña de Scrapers, los administradores disponen de un panel de **Telemetría FinOps en Vivo**:
*   **Contador y Barra de Progreso:** Visualiza los minutos consumidos en tiempo real sobre la cuota mensual de **2.000 minutos gratuitos** de GitHub Actions.
*   **Saldo y Días de Reposición:** Muestra los minutos disponibles y la fecha exacta en la que se reinicia el ciclo mensual (el día 1 de cada mes a las 00:00 UTC con cuenta atrás en días).
*   **Desglose por Proceso:** Detalla cuántos minutos han consumido el *Daily Scan* (`scrapers.yml`), el *Centinela / Cazador de Vinted* (`vinted_hunter.yml`) y las suites de integración (*CI / Tests*).
*   **Diagnóstico Inteligente de Cadencia:** Analiza el ritmo diario y proyecta el cierre de mes, confirmando con insignias visuales (🟢 *Óptimo*, 🟡 *Precaución*, 🔴 *Ajustar Cadencia*) si la cadencia de 50-75 min es segura.
*   **Descarga de Logs (CSV):** Botón `[ 📥 Descargar Log (CSV) ]` para exportar el historial forense de ejecuciones directamente a la carpeta de Descargas del dispositivo.

### 2.2 Control Operativo de Scrapers
*   **Listado de Arañas**: Visualiza las tiendas y portales soportados por el sistema (como Wallapop, eBay, Vinted, Amazon.es, BigBadToyStore, Frikimaz, etc.).
*   **Incursión Manual**: Dispara un escaneo en caliente para una tienda concreta o inicia una **Incursión Total**.
*   **Consola de Telemetría Homogeneizada**: Visualiza la telemetría en tiempo real con iconos outline limpios y sin emojis en bruto.
*   **Cancelación Cooperativa**: Si una incursión está tardando demasiado, puedes pulsar **"Detener Incursión"** para detener ordenadamente las arañas al terminar su ciclo de tienda actual.

---

## 3. Logs de Auditoría e Historial

El Oráculo lleva una bitácora forense de todas las acciones importantes realizadas en el sistema. Esto permite saber exactamente quién clasificó un producto, cuándo ocurrió y qué cambios hubo.

*   **Tipos de Eventos Registrados**:
    *   `LINKED_OFFER`: Cuando una oferta del Purgatorio es vinculada al catálogo.
    *   `LINKED_MISCELLANEOUS`: Cuando una oferta es desviada a la sección de Miscelánea Vintage.
    *   `REVERTED_MISCELLANEOUS`: Cuando un lote de Miscelánea es devuelto al Purgatorio.
    *   `DISCARDED_OFFER`: Cuando una oferta es descartada del Purgatorio.
*   **Detalles del Log**: Cada entrada del historial registra el nombre del usuario que realizó la acción, la fecha y hora exacta, la descripción del artículo involucrado y el identificador de la oferta.

---

## 4. Ajustes Generales del Sistema (`Guardián` vs `Master`)

La pestaña de **Ajustes** adapta automáticamente sus tarjetas según el rol activo para ofrecer al coleccionista (`Guardián`) un panel limpio de preferencias personales sin exponer parámetros internos del servidor ni generar errores de permisos:

### 4.0 Ficha `Acerca de & Novedades` (`Guardián` y `Master`)
*   **Píldora `vX.Y.Z · Novedades` en Cabecera**: Muestra siempre la versión SemVer instalada (con indicador luminoso cuando hay mejoras sin leer) y abre bajo demanda el modal de identidad, novedades explicadas en lenguaje humano, historial de versiones en acordeón y garantía de privacidad (*Modo Incógnito* y *Santuario Público*).
*   **Enlace a Salud de la Arquitectura (`Solo Master`)**: Dentro del modal *Acerca de* (y al pie de *Ajustes* para administradores), el botón *"Inspeccionar Salud de la Arquitectura"* lanza el visor topológico **`TecnoRed v2.0`**, con sondas pasivas de latencia, rutas de flujo y casos de uso reales en el Oráculo (`useCases`).

### 4.1 Santuario Público (`Guardián` y `Master`)
*   **Toggle de Habilitación**: Permite encender o apagar la visibilidad pública de tu colección.
*   **Enlace de Compartir**: Muestra el enlace exclusivo a tu Showcase y un botón rápido para copiarlo al portapapeles (ocultando siempre precios, inversión y ROI).

### 4.2 Ubicación del Guardián y Reglas Logísticas (`Guardián` y `Master`)
*   Permite seleccionar el país de residencia (España, Alemania, Italia, Francia o USA). El sistema cruza esta ubicación y las directivas logísticas del Oráculo para calcular de forma dinámica el costo real puesto en casa (*Landed Price*) de cada oferta de subasta o tienda.
*   **Reglas Logísticas por Tienda y Marketplace:**
    *   **BigBadToyStore (BBTS):** Tarifa fija de $8.00 USD de envío a España con conversión de divisa a EUR y recargo del 21% de IVA/aduanas sobre el importe total.
    *   **Marketplaces P2P (Wallapop, Vinted, eBay):** Tarifa base de envío de 5.00€ + 2% adicional en concepto de seguro y protección al comprador.
    *   **Frikimaz:** Coste de envío de 5.00€, siendo gratuito en pedidos a partir de 69.00€.
    *   **Smyths Toys:** Tarifa de envío estándar de 4.00€.
    *   **Triguetech:** Tarifa plana inamovible de 7.00€ por expedición.
    *   **Toymi / ToymiEU:** Coste estándar consolidado europeo.

### 4.3 Caché Local de Imágenes y Efectos Visuales 3D (`Guardián` y `Master`)
El Oráculo cuenta con un sistema de almacenamiento en caché en el navegador (Cache API) y ajuste de efectos gráficos por dispositivo:
*   **Preferencia en Local (`use_local_images`)**: Al activarse, el frontend lee y cachea de forma local en el navegador (`motu-image-cache`) las imágenes de las figuras al visualizarlas.
*   **Descarga Reactiva en Lote**: Descarga secuencialmente las imágenes faltantes o actualiza toda la caché del navegador del cliente, con barra de progreso e informe de reintentos. *(La descarga empaquetada de archivo **ZIP de imágenes WebP** del servidor está reservada exclusivamente al rol **Master**).*
*   **Efectos Hover 3D e Iluminación Neón**: Conmutador local (`Activados` / `Clásicos`) para optimizar fluidez y batería en dispositivos móviles.
*   **Fallback Híbrido**: Cualquier componente de imagen (`MOTUImage`) resuelve contra la caché local o estáticos y cae automáticamente al CDN original si no está disponible.

### 4.4 Vinculación con el Guardián de Telegram y Filtro Global
Para recibir alertas personalizadas directamente en tu móvil (`Guardián` y `Master`):
1.  Busca el bot del Oráculo en Telegram.
2.  Escribe el comando `/register [tu_nombre_de_usuario]` (el nombre de usuario con el que inicias sesión en el Oráculo).
3.  El bot asociará automáticamente tu cuenta y comenzarás a recibir notificaciones enriquecidas en HTML cuando una oferta coincida con tu **Lista de Deseos** o con una **Alerta de Precio** configurada.
*   **Filtro Inteligente Global (`Solo Master`):** En la pestaña *Ajustes*, el administrador dispone además del interruptor global del servidor (*Solo Figuras NO Poseídas*) y del visor de **Parámetros del Servidor (`.env`)**.

### 4.5 Escudo de Dispositivos y Autorización Soberana (`Solo Master`)
*   **Seguridad de Acceso:** Cada vez que un nuevo navegador, móvil o PC intenta acceder a la aplicación, el Escudo de Seguridad (`SecurityShield`) lo bloquea de forma preventiva y envía una notificación instantánea a Telegram exclusivamente al Soberano (Administrador).
*   **Aprobación en 1 Clic:** El Soberano puede pulsar directamente `[ ✅ Permitir Acceso ]` o `[ 🚫 Bloquear ]` en el propio mensaje de Telegram.
*   **Comandos de Gestión:**
    *   `/devices`: Lista los dispositivos registrados con botones interactivos para autorizar o eliminar.
    *   `/approve [id]`: Autoriza manualmente un dispositivo por su identificador.
    *   `/deny [id]`: Bloquea y purga un dispositivo.

### 4.6 Telemetría y Renovación de Certificados SSL
*   **Monitor en Vivo:** En la pestaña *Sistema*, una tarjeta dedicada muestra el estado del certificado SSL HTTPS (`DuckDNS`), emisor (`Let's Encrypt`) y días exactos restantes antes del vencimiento.
*   **Forzar Renovación:** Permite disparar la renovación inmediata de Certbot. Si ocurre cualquier eventualidad, se abre un modal de diagnóstico con el registro de terminal y un botón para copiar los logs.
*   **Control Remoto desde Telegram:** Los comandos `/ssl` (diagnóstico de estado) y `/renew_ssl` (forzar renovación) permiten mantener los certificados al día desde cualquier lugar.

### 4.7 Nexus Local Bridge (Worker Residencial de Wallapop)
*   **Panel de Trabajos:** Visualiza el historial y estado de los trabajos de extracción delegados al PC local.
*   **Disparo desde Móvil (`/nexus`):** Encola búsquedas masivas ejecutadas con la IP residencial de tu hogar (evitando bloqueos WAF de CloudFront). Al terminar, Telegram envía un resumen de las ofertas recolectadas.

### 4.8 Centinela Autónomo 24/7 de Vinted y Cazador Móvil
*   **Vigilancia Continua 24/7:** Servicio singleton que lanza incursiones automáticas con intervalos dinámicos aleatorios (de 50 a 75 minutos), evitando ventanas de solapamiento (*Blackout*) con los Daily Scans de las 02:00 y 14:30 UTC.
*   **Ejecución Efímera en Microsoft Azure:** Utiliza runners de GitHub Actions con IPs públicas dinámicas limpias para evitar bloqueos por tasa de peticiones.
*   **Deduplicación Diaria Anti-Spam:** Si una ganga ya te fue notificada durante el día de hoy, el sistema la silencia hasta el día siguiente para evitar spam en Telegram.
*   **Filtro Estricto de Ofertas Descartadas:** Omite automáticamente cualquier oferta marcada como rechazada o bloqueada en el Purgatorio o en la lista negra.
*   **Comandos de Control en Telegram:**
    *   `/centinela`: Consulta el estado de la vigilancia, total de incursiones, chollos descubiertos y tiempo para la próxima incursión.
    *   `/centinela on` / `/centinela off`: Activa o pausa la vigilancia 24/7.
    *   `/caza`: Dispara una incursión manual inmediata con el cuarteto canónico oficial MOTU (*"motu origins"*, *"masters del universo"*, *"masters of the universe"*, *"he-man origins"*).
    *   `/caza [figura]`: Ejecuta una búsqueda personalizada en tiempo real.

---

## 5. Grimorio de Lore Canónico MOTU (Pestaña "Grimorio Lore")

Esta sección permite auditar, editar y validar las historias, técnicas especiales y estadísticas canónicas de combate de todos los personajes del multiverso MOTU vinculados al catálogo. Solo el rol `Master` (administrador) puede modificar el canon global; el resto de usuarios únicamente lo consulta y personaliza sus cromos en su navegador (`localStorage`).

*   **Dos vistas:** `Figuras Origins` (ficha 1:1 del reverso de blíster para las **338+ figuras** de la línea Origins enlazadas por su identificador único `products.figure_id`, excluyendo figuras Vintage; cuenta con paginación real de **50 ítems por página** y totales exactos en cabecera) y `Personajes Arquetípicos` (perfil base de cada personaje, usado también como respaldo de las figuras Vintage en el visor de cromos).
*   **Buscador y Filtros Avanzados:** Localiza al instante cualquier héroe o villano por nombre, subtítulo, frase de blíster, identificador de catálogo (`AF411` / `figure_id`) o `#ID`, filtrando por las **8 facciones** del Grimorio (*Guerreros Heroicos*, *Guerreros del Mal*, *La Horda del Terror*, *Los Hombres Serpiente*, *La Gran Rebelión*, *Guardianes Cósmicos*, *Gobernantes de Solaria* y *Alianzas del Multiverso* — las dos últimas reutilizan el marco gráfico de *Castle Grayskull*), además de **Subcategoría / Wave** y **Estado editorial** (*Canon del Sistema* o *Editadas por Master*).
*   **Selector Rápido de Bando (1 Clic):** Desde cada fila de `Figuras Origins` el administrador puede reasignar directamente el bando mediante un desplegable optimista sin abrir el formulario completo; actualiza automáticamente el `theme_key` del marco y marca la figura como editada (`is_customized = true`).
*   **Filtro de Pendientes de Revisión:** Permite aislar con 1 clic los personajes recién descubiertos por el Daily Scan que requieren revisión humana.
*   **Editor Visual:** Modal interactivo para ajustar facción, nombre de la habilidad especial, cita del reverso y su autor, coste de maná (texto simbólico, p. ej. `{2}{W}{W}`), estadísticas de combate (FUE, MAG, DEF, AGI; valores de 1 a 100) y el texto de historia con contador de caracteres integrado (180 caracteres recomendados para el encaje en el cromo TCG; es un aviso visual que no bloquea el guardado).
*   **Regla de Inmutabilidad:** Los textos cosechados de la wiki quedan siempre como *pendientes de revisión*. Al guardar un personaje o modificar una figura Origins (incluso cambiando solo su bando), queda marcado como **curado por Master** (`is_customized = true`) y ni el sembrado automático ni una re-cosecha lo sobrescriben. Para re-cosechar un personaje ya verificado la interfaz pide confirmación explícita (`force`), y el resultado vuelve a quedar pendiente de revisión.
*   **Impacto Cero en Catálogo y Colección (`0 ms`):** El enlace por `figure_id` y el catálogo JSON maestro viven cacheados en memoria (`@lru_cache`) y son consumidos únicamente por `/api/lore/*` y por el sembrador; las consultas principales (`/api/products`, `/api/auctions/products`) permanecen intactas sin `JOIN` adicionales.
*   **Paridad de bases de datos:** Los cambios se guardan primero en Supabase (fuente primaria) y se replican a SQLite local. La opción `[12]` del Centro de Control compara los conteos de ambas.

---

## 6. Taller de Calibración de Cromos Digitales (Pestaña "Cromos TCG")

Herramienta WYSIWYG de precisión milimétrica reservada para administradores que permite posicionar y formatear la geometría de cada una de las 6 plantillas de cromos coleccionables:

*   **Selector de Plantilla:** Selecciona la facción a calibrar (*Castle Grayskull*, *Snake Mountain*, *Evil Horde*, *Snake Men*, *Great Rebellion*, *Cosmic Enforcers*).
*   **Simulador en Vivo a 60fps:** Visualiza en tiempo real los cambios sobre un cromo a escala con figuras canónicas de prueba.
*   **Controles Deslizantes por Secciones:**
    *   **Cabecera:** Posición vertical (`top`), horizontal (`left`), ancho (`width`) y tamaño tipográfico del título.
    *   **Losa de Piedra Unificada:** Ajuste del marco físico inferior (`top`, `left`, `width`, `height`) que aloja el poder, lore y tipo.
    *   **Placa de Poder:** Altura y tamaño de fuente de la técnica especial.
    *   **Lore Canónico:** Tamaño de fuente e interlineado (`line-height`).
    *   **Categorización de Tipo:** Tamaño de fuente y color temático.
    *   **Sockets de Combate:** Altura vertical y márgenes de las casillas de piedra `FUE|MAG` y `DEF|AGI`.
*   **Gestión de Estados:**
    *   `[ 💾 Guardar Coordenadas ]`: Persiste la configuración en Supabase y SQLite (`SystemConfigModel`).
    *   `[ 🔄 Restablecer Facción ]`: Restaura la plantilla actual a sus valores canónicos por defecto.
    *   `[ 🔁 Restablecer Todas ]`: Restablece las 6 facciones completas.
    *   `[ 📋 Copiar JSON ]`: Copia la matriz de coordenadas al portapapeles.





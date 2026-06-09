# Manual del Usuario: 08. Configuración de Sistemas

El panel de **Configuración** es la cabina de control técnico del Oráculo. Desde aquí, los administradores (Master) gestionan los engranajes de la aplicación, controlan la actividad de las arañas de extracción y supervisan las cuentas de acceso.

*Esta sección está reservada exclusivamente para los usuarios con el rol de **Master (Administrador)**.*

---

## 1. Gestión de Héroes (Usuarios)

En esta pestaña se listan todos los usuarios ("Héroes") registrados en el Oráculo. Los administradores pueden:
*   **Crear Nuevos Usuarios**: Registrar a un coleccionista asignándole un nombre de usuario, correo electrónico, rol (`Guardián` o `Master`) y una contraseña inicial.
*   **Modificar Roles**: Ascender a un Guardián a Master en caso de que necesite acceso al Purgatorio o a la configuración, o rebajar sus privilegios.
*   **Eliminar Cuentas**: Revocar el acceso de forma definitiva a cualquier usuario del sistema.

---

## 2. Panel de Control de Scrapers (Incursiones)

El Oráculo extrae información comercial mediante un conjunto de arañas web automatizadas (`scrapers`) que simulan navegación humana para evitar baneos de IPs.

Desde este panel, los administradores pueden gestionar el ciclo de recolección de forma interactiva:
*   **Listado de Arañas**: Visualiza todas las tiendas y portales soportados por el sistema (ej. Wallapop, eBay, Vinted, El Corte Inglés, etc.) junto con el estado del portal.
*   **Incursión Manual**: Dispara un escaneo en caliente para una tienda concreta o inicia una **Incursión Total** que ejecutará secuencialmente todos los scrapers del sistema.
*   **Cancelación Cooperativa**: Si una incursión está tardando demasiado o deseas detener el tráfico de scraping, puedes pulsar el botón **"Detener Incursión"**. Esto enviará una señal cooperativa de parada en el backend que detendrá ordenadamente las arañas al terminar su ciclo de tienda actual, sin corromper la base de datos ni dejar procesos colgados.

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

## 4. Ajustes Generales del Sistema (Todos los Usuarios)

La pestaña de **Ajustes de Sistema** está abierta tanto a Guardianes como a Administradores (Masters) y contiene configuraciones personalizadas del cliente y automatizaciones del perfil:

### 4.1 Santuario Público (Santuario Compartido)
*   **Toggle de Habilitación**: Permite encender o apagar la visibilidad pública de tu colección.
*   **Enlace de Compartir**: Muestra el enlace exclusivo a tu Showcase y un botón rápido para copiarlo al portapapeles.

### 4.2 Ubicación del Guardián (Cálculo de Envíos)
*   Permite seleccionar el país de residencia (ej. España, Francia). El sistema cruzará esta ubicación con las reglas logísticas para calcular de forma dinámica y precisa el costo real de envío consolidado (Landed Price) de cada oferta de subasta o tienda.

### 4.3 Caché Local de Imágenes (Acelerador de Carga)
El Oráculo cuenta con un sistema híbrido e inteligente de almacenamiento local de imágenes para erradicar los tiempos de espera causados por la descarga de imágenes externas:
*   **Preferencia en Local (`use_local_images`)**: Si se activa, la aplicación cargará las imágenes de las figuras directamente desde el almacenamiento local del PC/servidor (`/api/static/images/[id].jpg`), logrando transiciones instantáneas y fluidas.
*   **Gestión de Descargas en Lote**: Un botón para iniciar la descarga en segundo plano de todas las imágenes de productos a la caché local.
*   **Barra de Progreso y Control**: Muestra el progreso de descargas en tiempo real (conteo total, descargados, errores). Incluye un botón para **cancelar la descarga** en cualquier momento de forma segura.
*   **Fallback Automático**: Si una imagen local no existe (error 404) o falla la carga, el componente React (`MOTUImage`) realiza un fallback transparente e instantáneo al hotlink de internet original, garantizando que el usuario nunca vea imágenes rotas.

### 4.4 Vinculación con el Guardián de Telegram (Alertas Bidireccionales)
Para recibir alertas personalizadas directamente en tu móvil:
1.  Busca el bot del Oráculo en Telegram.
2.  Escribe el comando `/register [tu_nombre_de_usuario]` (el nombre de usuario con el que inicias sesión en el Oráculo).
3.  El bot asociará automáticamente tu cuenta y comenzarás a recibir de inmediato notificaciones enriquecidas en HTML cada vez que una nueva oferta en el Purgatorio coincida con una figura de tu **Lista de Deseos** o con una **Alerta de Precio** configurada.


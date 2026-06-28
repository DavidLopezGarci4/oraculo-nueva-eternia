# Manual del Usuario: 08. Configuración de Sistemas

El panel de **Configuración** es la cabina de control técnico del Oráculo. Desde aquí, los administradores (Master) gestionan los engranajes de la aplicación, controlan la actividad de las arañas de extracción y supervisan las cuentas de acceso.

*Esta sección está reservada exclusivamente para los usuarios con el rol de **Master (Administrador)**.*

---

## 1. Gestión de Héroes (Usuarios)

En esta pestaña se listan todos los usuarios ("Héroes") registrados en el Oráculo. Los administradores pueden:
*   **Crear Nuevos Usuarios**: Registrar a un coleccionista asignándole un nombre de usuario, correo electrónico, rol (`Guardián` o `Master`) y una contraseña inicial.
*   **Modificar Roles (Estilo Outline)**: Ascender o degradar roles directamente. La interfaz visualiza el rango de forma homogeneizada usando los iconos outline monocromáticos `Swords` (Maestro) y `Shield` (Guardián) en lugar de emojis coloridos para encajar con el diseño premium de la aplicación.
*   **Eliminar Cuentas**: Revocar el acceso de forma definitiva a cualquier usuario del sistema.

---

El Oráculo extrae información comercial mediante un conjunto de arañas web automatizadas (`scrapers`) que simulan navegación humana para evitar baneos de IPs.

Desde este panel, los administradores pueden gestionar el ciclo de recolección de forma interactiva:
*   **Listado de Arañas**: Visualiza las tiendas y portales soportados por el sistema (como Wallapop, eBay, Vinted, Amazon.es -habiéndose limpiado la versión duplicada de Amazon-, etc.).
*   **Incursión Manual**: Dispara un escaneo en caliente para una tienda concreta o inicia una **Incursión Total**.
*   **Consola de Telemetría Homogeneizada**: Visualiza la telemetría en tiempo real. Para conservar la atmósfera premium y el tono oscuro monocromático, cualquier emoji producido por los logs del backend es parseado dinámicamente al vuelo en el cliente y presentado como un icono vectorial de contorno limpio (Lucide icons).
*   **Cancelación Cooperativa**: Si una incursión está tardando demasiado, puedes pulsar **"Detener Incursión"** para detener ordenadamente las arañas al terminar su ciclo de tienda actual, sin dejar procesos colgados.

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

### 4.3 Caché Local de Imágenes (Acelerador de Carga en Cliente)
El Oráculo cuenta con un sistema de almacenamiento en caché en el navegador (utilizando Cache API / IndexedDB) para erradicar por completo los tiempos de carga:
*   **Preferencia en Local (`use_local_images`)**: Al activarse, el frontend lee y cachea de forma local en el navegador (`motu-image-cache`) las imágenes de las figuras al visualizarlas. Esto elimina la necesidad de configurar rutas de directorios físicos en el servidor o PC del usuario.
*   **Descarga Reactiva en Lote**: Un botón que descarga secuencialmente todas las imágenes de productos (modernos y vintage combinados) directamente a la caché del navegador del cliente, con una barra de progreso exacta y soporte de cancelación interactiva.
*   **Fallback Híbrido**: Cualquier componente de imagen (`MOTUImage`) resolverá la foto contra la caché local del navegador o de estáticos del servidor y, ante cualquier error 404, caerá inmediatamente al hotlink web original.

### 4.4 Vinculación con el Guardián de Telegram (Alertas Bidireccionales)
Para recibir alertas personalizadas directamente en tu móvil:
1.  Busca el bot del Oráculo en Telegram.
2.  Escribe el comando `/register [tu_nombre_de_usuario]` (el nombre de usuario con el que inicias sesión en el Oráculo).
3.  El bot asociará automáticamente tu cuenta y comenzarás a recibir de inmediato notificaciones enriquecidas en HTML cada vez que una nueva oferta en el Purgatorio coincida con una figura de tu **Lista de Deseos** o con una **Alerta de Precio** configurada.


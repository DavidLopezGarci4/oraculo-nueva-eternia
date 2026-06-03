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

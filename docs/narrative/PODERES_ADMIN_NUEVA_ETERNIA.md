# 🗝️ El Cetro de Poder: Funciones de Administrador

> [!NOTE]
> **Documento de Roles y Herramientas**. Este documento resume las capacidades de la interfaz para usuarios Administradores. Para entender la arquitectura técnica que sustenta estos poderes, consulta la **[DOCUMENTACION MAESTRA](DOCUMENTACION_MAESTRA.md)**.

He refinado las herramientas administrativas para que tengas el mando absoluto sobre la infraestructura técnica y la integridad del catálogo.

Aquí tienes el inventario de tus poderes actuales:

## 1. Gestión de Metadatos y "Fusión Molecular" 🧬
Directamente desde el **Catálogo Maestro**, como Administrador puedes:
- **Edición en Caliente**: Modificar nombres, categorías, EANs y URLs de imágenes.
- **Fusión Molecular**: Unificar productos duplicados transfiriendo automáticamente todas sus ofertas e histórico de precios al registro maestro.

## 2. Operaciones Nucleares: Purga y Blacklist ☢️
Herramientas de limpieza profunda en el Purgatorio y Catálogo:
- **Purga Nuclear (Unlink)**: Desvincular ofertas erróneas devolviéndolas al Purgatorio para su re-revisión.
- **Blacklist (Destierro)**: Bloqueo permanente de URLs "basura" para que nunca vuelvan a contaminar el sistema.
- **Reset de SmartMatch**: Posibilidad de reiniciar masivamente las vinculaciones automáticas si se detectan patrones de error.

## 3. Mando de Incursiones (Bitácora en Vivo) 📡
Tu centro de mando para los 13 scrapers activos:
- **Incursión Individual**: Disparar manualmente cualquier motor (Amazon, Tradeinn, ActionToys, etc.) con un clic.
- **Logs de Ejecución**: Visualización técnica en tiempo real integrada en la consola táctica, permitiendo ver qué está procesando el robot en cada instante.
- **Registro Automático**: El sistema autodetecta nuevos motores al arrancar y los registra en el panel de control.

- **Ajustes de Mercado**: Cambiar tu ubicación (España/USA/Europa) para recalcular instantáneamente el **Landed Price** de todo el catálogo.
- **Importación Manual**: El Wallapop Importer permite procesar hallazgos de segunda mano sorteando bloqueos anti-bot.

## 5. Gestión de Héroes (Mando de Personal) 🛡️
Como Arquitecto, tienes el control sobre quién accede al Oráculo y con qué permisos:
- **Control de Rangos**: Promover Guardianes a Maestros o degradar perfiles dinámicamente.
- **Protocolo de Reseteo**: Iniciar solicitudes de cambio de contraseña para otros héroes.
- **Eliminación Definitiva**: Borrado permanente de usuarios y todos sus datos de colección asociados (**protección anti-borrado de admins integrada**).
- **Auditoría de Fortaleza**: Visualización del tamaño de la colección y actividad de cada usuario.
- **Expulsión Reactiva**: El sistema monitoriza en tiempo real los cambios de identidad; si un Administrador cambia a un perfil de Guardián mientras está en el Mando, el sistema lo expulsará automáticamente al Tablero por seguridad.

## 6. Blindaje de Secretos (Zero-Leak) 🛡️
Como Arquitecto, la integridad del Reino depende de la discreción:
- **Zero-Leak Policy**: Prohibición de claves hardcoded en el código. Todas las llaves maestras residen en la Bóveda de Secretos (.env / GitHub Secrets).
- **Limpieza de Rastro**: El sistema ignora y purga automáticamente cualquier rastro de diagnóstico (.html, .png) generado durante las incursiones para no dejar huellas en los registros del Código.

## 7. El Bastión de Datos (Auditoría) 🏛️
- **Ghost Sync**: Gestión del búfer de acciones pendientes para asegurar que ningún cambio administrativo se pierda por fallos de red.
- **Trazabilidad Sirius**: Registro inmutable de quién y cuándo realizó cada acción crítica en el Reino.
- **Diagnóstico SMTP**: El endpoint `/api/system/audit` reporta el estado de la configuración de correo electrónico.

## 8. Control de Incursiones (Parada & Cancelación) 🛑
- **Cancelación Cooperativa**: El botón "Detener Scrapers" envía una señal de cancelación que aborta la incursión entre scrapers sin pérdida de datos.
- **Persistencia Parcial**: Las ofertas recolectadas antes de la cancelación se guardan automáticamente en la base de datos.
- **Hardware Kill**: Los procesos hijos de Playwright/Chromium se eliminan como respaldo para liberar recursos del servidor.
- **Reset de Cola**: Tras una parada, el sistema queda libre para iniciar nuevas incursiones inmediatamente.

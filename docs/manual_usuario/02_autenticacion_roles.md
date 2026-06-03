# Manual del Usuario: 02. Autenticación y Roles de Acceso

El acceso al Oráculo de Nueva Eternia está protegido y segmentado mediante un sistema de autenticación seguro basado en tokens web JSON (JWT). Los usuarios ingresan con sus credenciales y se les asigna un perfil con permisos específicos para proteger la integridad del catálogo y las configuraciones de la infraestructura.

---

## Roles en la Aplicación

Existen dos tipos de perfiles definidos en el sistema:

### 1. Guardián (Usuario Estándar)
Es el perfil de lectura y control personal.
*   **Permisos**:
    *   Visualizar el **Tablero** general y sus estadísticas de mercado.
    *   Gestionar su colección personal en **Mi Fortaleza** y **Mi Fortaleza Vintage** (añadir figuras a su inventario, modificar precios pagados, estado de conservación, notas).
    *   Consultar los **Catálogos** de Nueva Eternia y Eternia Vintage.
    *   Ver las mejores ofertas del mercado en **El Pabellón**.
*   **Restricciones**: No tiene acceso a herramientas de administración, no puede iniciar incursiones (scraping), ni reclasificar artículos en el Purgatorio.

### 2. Master (Administrador / David)
Es el rol de control total de la infraestructura y mantenimiento de datos.
*   **Permisos (Adicionales a los del Guardián)**:
    *   Acceso a la sección de **Configuración** (gestión de usuarios, inicio manual de scrapers, visualización de logs del sistema).
    *   Acceso a **El Purgatorio** para validar, emparejar o descartar las ofertas que el sistema descarga.
    *   Clasificar artículos generales en **Miscelánea** y revertirlos de vuelta al Purgatorio.
    *   Gestión completa de usuarios (añadir nuevos héroes, modificar sus roles o eliminarlos).

---

## Inicio de Sesión y Sesiones de Usuario

Para acceder a la aplicación:
1. Introduce tu nombre de usuario y tu contraseña en la pantalla de bienvenida.
2. Al iniciar sesión, el backend genera un token de seguridad que se almacena localmente y expira automáticamente a las 24 horas.
3. Si deseas cerrar la sesión manualmente, puedes usar el botón **"Cerrar Sesión"** situado en la parte inferior de la barra lateral.

---

## Acceso de Emergencia: Sovereign Login (Bypass del Escudo)

Si por algún motivo la base de datos se corrompe, pierdes tus credenciales o el servidor de Supabase experimenta problemas que impiden el acceso regular de administración, el Oráculo incluye una puerta trasera de emergencia de alta seguridad conocida como **Sovereign Login** o **ShieldBypass**.

*   **¿Cómo funciona?**:
    Si intentas iniciar sesión utilizando el correo configurado en la variable de entorno `SOVEREIGN_EMAIL` del servidor backend, el sistema de seguridad omitirá temporalmente la comprobación estricta de la base de datos y te concederá acceso inmediato con privilegios de **Master (Admin)**.
*   **Seguridad**: Este correo de emergencia está estrictamente definido en la configuración inmutable del backend. Solo quien tenga acceso al archivo `.env` físico del servidor puede conocer o modificar esta credencial.

# ⚖️ Jerarquía de Poder: Guardianes vs. Masters

> [!NOTE]
> **Documento de Roles**. Este documento detalla la lógica de permisos interna de la aplicación. Para ver cómo se implementan técnicamente o cómo el flujo interactúa con la base de datos, consulta la **[DOCUMENTACION MAESTRA](DOCUMENTACION_MAESTRA.md)**.

He mapeado la jerarquía exacta de permisos implementada en la Nueva Eternia para respetar la seguridad de tu colección.

## 🛡️ Guardián de Eternia (Perfil: David / User)
Este es tu espacio personal de consulta y gestión de colección.
- **Acceso Permitido**:
  - **Dashboard**: Ver métricas vivas, oportunidades ROI y salud de motores.
  - **Catálogo Maestro**: Consultar figuras, historiales Cronos y disponibilidad.
  - **La Fortaleza**: Gestionar tu colección (Poseído/Wishlist) y calcular ROI personal.
- **Restricciones**: No puedes acceder al panel de Configuración, no puedes disparar incursiones manuales ni realizar ediciones administrativas en el catálogo.

---

## 🔮 Master del Universo (Perfil: Arquitecto / Admin)
Este perfil posee la **Llave Maestra** para la gestión total del sistema.
- **Poderes Únicos**:
  - **Control de Incursiones**: Disparar scrapers manualmente desde el Purgatorio y ver logs en vivo.
  - **Gestión Administrativa**: Editar metadatos, fusionar productos y gestionar el Blacklist.
  - **Configuración Profunda**: Importación manual de Wallapop y ajustes de sistema.
  - **Sincronización Total**: Control del búfer Ghost Sync y reconexión con Supabase.

---

### 🧬 Implementación en la Interfaz Actual

El sistema detecta automáticamente tu rango mediante una **Validación de Identidad** al arrancar la aplicación (`App.tsx`):

1.  **Si eres Guardián**: El menú lateral se simplifica. El panel de **Configuración** y las herramientas de disparo en el **Purgatorio** permanecen ocultos.
2.  **Si eres Maestro**: Se desbloquean todas las capacidades de gestión, permitiéndote actuar como el Arquitecto de los Datos.
3.  **Dinamismo Total**: El rango ya no es estático por ID de usuario. Un Administrador puede promover a un Guardián a Maestro desde la **Gestión de Héroes**, y los cambios de interfaz se reflejan al instante.
4.  **Bóveda de Seguridad (Expulsión)**: Si un Guardián intenta permanecer en una zona de Maestro tras un cambio de identidad, el Oráculo lo detectará de inmediato y lo redirigirá al Tablero (Home), cerrando el acceso a las herramientas administrativas.


# ⚖️ Jerarquía de Poder: Guardianes vs. Masters

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

El sistema detecta automáticamente tu rol al cargar la sesión:

1.  **Si eres Guardián**: El menú lateral se simplifica. El panel de **Configuración** y las herramientas de disparo en el **Purgatorio** están ocultas.
2.  **Si eres Master**: Se desbloquean todas las capacidades de gestión, permitiéndote actuar como el Arquitecto de los Datos.

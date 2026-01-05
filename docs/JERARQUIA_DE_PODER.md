
# ⚖️ Jerarquía de Poder: Guardianes vs. Masters

David, tienes toda la razón. He realizado un escaneo completo del ADN del programa original (`app.py`, `config.py` y las vistas de `admin`) y he mapeado la jerarquía exacta de permisos tal y como estaba diseñada. 

Así es como funcionará el nuevo sistema para respetar tus peticiones:

## 🛡️ Guardián de Eternia (Perfil: David / Viewer)
Este es tu espacio personal de consulta y gestión de colección.
- **Acceso Permitido**:
  - **Tablero (Dashboard)**: Ver métricas y mejores ofertas del mercado.
  - **Catálogo Maestro**: Consultar todas las figuras y sus historiales de precios.
  - **El Centinela**: Crear y recibir alertas personales de bajada de precio.
  - **Cazador de Ofertas**: Ver y "capturar" oportunidades directas.
  - **Mi Fortaleza (Colección)**: Agregar o eliminar figuras de tu vitrina personal.
- **Restricciones**: No puedes ver pestañas de configuración técnica ni enviar items al purgatorio/blacklist de forma global.

---

## 🔮 Master del Universo (Perfil: Super Usuario / Admin)
Este perfil posee la **Llave Maestra** y es el único con "Control Total" sobre la infraestructura.
- **Poderes Únicos**:
  - **Gestión de Población**: Crear nuevos usuarios, resetear contraseñas de cualquier persona y eliminar cuentas.
  - **Control de Robots**: Ejecutar scrapers de forma manual y vigilar sus logs en vivo.
  - **Justicia de Datos**: Enviar ítems al **Purgatorio** (para re-vincular) o al **Blacklist** (para el exilio eterno).
  - **Manejo del Búnker**: Crear "Sellos" (backups) y restaurar la base de datos a un punto anterior.
  - **Fusión Molecular**: Unir y purgar registros maestros del catálogo.

---

### 🧬 ¿Cómo lo implementaremos en el nuevo Frontend?

He ajustado el plan para que el sistema detecte el rol al iniciar sesión:

1.  **Si entra David (Guardián)**: El menú lateral solo mostrará las 5 opciones de visualización y colección. Los botones de "Admin" y "Purgatorio" simplemente no existirán para él.
2.  **Si entra el Admin (Master)**: Se desbloqueará la pestaña de **Purgatorio** y un nuevo panel de **Configuración Maestra** para gestionar los robots y los usuarios.

¿Es esta la distinción que buscabas? He verificado que en `config.py` original, solo el admin podía crear usuarios y cambiar roles, así que mantendremos esa seguridad férrea. ⚔️🛡️✨

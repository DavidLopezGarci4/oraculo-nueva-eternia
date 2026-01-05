
# 🗝️ El Cetro de Poder: Funciones de Administrador

David, he analizado minuciosamente las "Funciones Especiales" que solo tú, como Admin, tenías en el programa original. No solo las mantendremos, sino que las hemos diseñado para que sean más intuitivas y rápidas en la **Nueva Eternia**.

Aquí tienes el inventario de tus poderes actuales y cómo evolucionarán:

## 1. Gestión de Metadatos y "Fusión Molecular" 🧬
En el programa original, podías editar cada figura desde el catálogo.
- **En React**: Implementaremos un "Modo Admin" en el **Catálogo Maestro**. Al activarlo, cada tarjeta de figura mostrará botones para:
  - **Editar nombre, categoría y foto** al instante.
  - **Fusión Molecular**: ¿Tienes dos "Skeletors" duplicados? Con un clic los fusionarás en uno, arrastrando todas sus ofertas e historial de precios.

## 2. Operaciones Nucleares: Purga y Blacklist ☢️
Estas son tus herramientas de limpieza profunda.
- **Purga Nuclear**: Elimina una figura del catálogo pero **no tira la información a la basura**. Envía sus ofertas de vuelta al Purgatorio por si quieres re-vincularlas a otra figura.
- **Blacklist (Destierro)**: Bloquea una URL para siempre. Si un robot encuentra una oferta "basura", el Blacklist asegura que nunca más vuelva a molestarte.

## 3. Control de Misión (Los Robots) 📡
Tu centro de mando para los scrapers.
- **Despliegue Manual**: Podrás elegir qué tienda atacar (ActionToys, Frikiverso, etc.) o lanzarlos a todos.
- **Circuit Breaker**: El sistema te avisará si intentas escanear una tienda que ya fue visitada hace poco para evitar baneos.
- **Limpieza de Sistema**: Si un robot se queda "colgado", tendrás un botón para resetear su estado y que todo vuelva a la normalidad.

## 4. La Cámara de Grayskull (Backups y Búnker) 🏰
Esta es la parte más crítica de tu poder: la seguridad de los datos.
- **Sellado Manual**: Antes de hacer un cambio grande, podrás crear un "Sello" (Backup) con un clic.
- **Máquina del Tiempo**: Si algo sale mal, podrás elegir un sello anterior y **restaurar toda la base de datos** (ya sea en Local o en Supabase) en segundos.
- **Caja Negra**: Acceso a los "Snapshots" crudos; los datos tal cual los leyeron los robots antes de ser procesados.

## 5. El Bastión de Datos (Auditoría) 🛡️
Un registro inborrable de cada movimiento.
- Sabrás exactamente cuándo se vinculó o desvinculó cada oferta, manteniendo la integridad total de la información.

---

### 💡 Mi compromiso contigo:
Estas funciones no estarán a la vista de un usuario normal (si en el futuro decides compartir el Oráculo con otros coleccionistas). Solo tú, con tu perfil, verás aparecer estos botones y paneles adicionales.

**¿Hay alguna de estas funciones de "Superusuario" que sea tu favorita o que uses con más frecuencia?** Me gustaría priorizar su implementación en la interfaz React para que te sientas cómodo desde el primer día.

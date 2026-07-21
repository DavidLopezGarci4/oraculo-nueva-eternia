---
name: aaa-buenas-practicas
description: Úsala SIEMPRE que continúes el trabajo de elevación AAA (seguridad/arquitectura/rendimiento/diseño) de El Oráculo de Nueva Eternia en la rama refactor/aaa-uplift, en cualquier máquina o modelo. Define el protocolo de arranque de sesión, los límites de seguridad no negociables, y las convenciones de código, testing, migraciones y documentación establecidas — para que el trabajo entre sesiones/máquinas/LLMs distintos sea coherente y no corrompa el proyecto.
---

# Buenas prácticas — Elevación AAA de El Oráculo de Nueva Eternia

Este documento es el manual operativo del trabajo de elevación AAA (seguridad, arquitectura,
rendimiento, diseño) que se está ejecutando **fase a fase, commit a commit**, en la rama
`refactor/aaa-uplift`. Se ha escrito porque el usuario alterna entre **máquinas distintas y
modelos/LLMs distintos** de una sesión a otra — este archivo viaja con el repo (está versionado
en `.claude/skills/`, no en `.gitignore`) precisamente para que cualquier sesión nueva, en
cualquier máquina, arranque con el mismo contrato de trabajo.

**No duplica el backlog.** El backlog vivo, priorizado por "olas", con el detalle de qué está
hecho y qué falta, vive en **[docs/REPORTE_MEJORAS_AAA.md](../../docs/REPORTE_MEJORAS_AAA.md)**
— sección "🎯 BACKLOG CONSOLIDADO Y PRIORIZADO". Este documento es el CÓMO; ese otro es el QUÉ.

---

## 1. Protocolo de arranque de sesión (obligatorio, primer paso, siempre)

Antes de asumir NADA sobre el estado del proyecto — incluso si el usuario dice "sigue donde lo
dejaste" — ejecuta, en este orden:

1. `git status` y `git log --oneline -20` en la rama actual. La rama de trabajo es
   `refactor/aaa-uplift`; si `git status` muestra que estás en otra rama o hay cambios sin
   commitear que no reconoces, PARA y pregunta antes de tocar nada — puede ser trabajo en curso
   de otra sesión/máquina.
2. Lee la sección **"Estado de ejecución"** (arriba del todo) y la tabla de
   **"BACKLOG CONSOLIDADO Y PRIORIZADO"** en `docs/REPORTE_MEJORAS_AAA.md`. Es la única fuente de
   verdad sobre qué Ola/ítem está `✅ COMPLETA`, cuál está en curso y cuál falta. No confíes en el
   resumen de una conversación anterior si contradice lo que dice el propio documento o el
   `git log` — el documento y el historial de commits son lo que persiste entre máquinas, la
   conversación no.
3. Corre la suite completa (`pytest tests/ -q` desde la raíz, con el venv del proyecto —
   `.venv/Scripts/python.exe -m pytest tests/ -q` en Windows) para confirmar que partes de un
   estado verde. Si algo falla ANTES de que hayas tocado nada, es una regresión heredada: repórtala,
   no la arrastres silenciosamente a tu propio trabajo.

Razón: el usuario ha reportado más de una vez confusión al retomar trabajo desde una máquina o
modelo distinto sin este paso — es la causa más probable de que un cambio "corrompa" el proyecto
sin que nadie se dé cuenta hasta mucho después.

---

## 2. Límites de seguridad no negociables

- **Nunca gestiones secretos reales.** El usuario rota `.env` (JWT_SECRET, ORACULO_API_KEY,
  EXTENSION_API_KEY, credenciales de Supabase, etc.) y despliega vía Docker **en su otra máquina**,
  fuera de esta sesión. Tu trabajo aquí es preparar/verificar código, migraciones y guías — nunca
  generar, pedir, leer, ni escribir un valor de secreto real. `.env.example` sí se mantiene (son
  plantillas con placeholders `CHANGE-ME-...`, nunca valores reales).
- **Nunca hagas `git push` ni merges a `main`** sin que el usuario lo pida explícitamente en ese
  turno. Todo el trabajo vive en `refactor/aaa-uplift`; `main` sigue teniendo el estado antiguo
  (incluida la clave `eternia-shield-2026` expuesta en el bundle histórico) hasta que el usuario
  decida desplegar — eso es una decisión suya, de Ola 0/Ola 1 del backlog, no tuya.
- **Nunca ejecutes de verdad `/scrapers/run` ni `/scrapers/stop` en tests.** El primero dispara
  scraping real con red y hasta 30 min de timeout; el segundo mata procesos reales del sistema vía
  `psutil`. Sus `response_model` se verifican solo por construcción del schema, nunca por
  invocación real — está documentado así en `test_api_response_schemas.py` y debe seguir así.
- **Ninguna clave de bajo privilegio debe poder escalar a admin.** Ejemplo real de este patrón:
  `EXTENSION_API_KEY` (extensión de Chrome, vive en el navegador del usuario, puede filtrarse) es
  deliberadamente un secreto DISTINTO de `ORACULO_API_KEY` (admin, server-to-server). Si añades un
  nuevo cliente no confiable (otra extensión, un webhook externo, un script de terceros), dale su
  propia clave de alcance mínimo — nunca reutilices la clave de admin "para no complicarlo".
- **Nunca borres ni muevas carpetas de la raíz "para limpiar" sin confirmación explícita del
  usuario, aunque tu propia investigación te diga que no tienen ninguna referencia en el código.**
  El usuario alterna con otras herramientas de IA (3OX.Ai, Gemini/Antigravity, y otras) que pueden
  usar esas carpetas como su propio workspace aunque esta app no las toque — un `git rm` es
  potencialmente no recuperable si esa herramienta guardaba ahí estado que no está en ningún otro
  sitio. Antes de proponer nada, lee
  **[docs/technical/AUDITORIA_CARPETAS_RAIZ.md](../../docs/technical/AUDITORIA_CARPETAS_RAIZ.md)**
  — ya tiene el veredicto por carpeta (usada / operación manual / otra herramienta confirmada en
  uso / sin ninguna referencia detectada) para no repetir la investigación desde cero.

---

## 3. Convenciones de código establecidas

### 3.1 `response_model` estricto en todo endpoint FastAPI que devuelva JSON

Todo endpoint que devuelve JSON debe declarar `response_model=` con un schema Pydantic en
`src/interfaces/api/schemas.py` (usa `ConfigDict(from_attributes=True)` cuando el handler devuelve
objetos ORM de SQLAlchemy directamente en vez de un dict). Excepciones deliberadas y documentadas
inline con un comentario que explique por qué:
- Respuestas binarias/streaming (excel, sqlite, zip de imágenes, logs descargables).
- Datos genuinamente dinámicos/externos que no tienen una forma estable predecible
  (`get_market_intelligence`, `get_wallapop_preview`, `system_audit`, `get_sword_configs`).

Si el handler devuelve un dict simple `{"status": "success", "message": "..."}`, reutiliza
`StatusMessageOutput` — no crees un schema nuevo para cada endpoint que devuelve esa misma forma.

### 3.2 Guardianes de autenticación: patrón dual, nunca "todo o nada"

Cuando un endpoint tiene más de un llamante legítimo con mecanismos de auth distintos, no fuerces
un único guardián — compón uno dual que pruebe cada camino y caiga al siguiente. Dos ejemplos reales
ya en el código, en `src/interfaces/api/deps.py`:
- `verify_api_key`: acepta la API key servidor-a-servidor (scrapers/workers) O un JWT de admin.
- `verify_wallapop_import`: acepta la clave propia de la extensión de Chrome (`X-Extension-Key`) O
  el flujo normal `verify_device` (para el import manual desde la SPA ya autenticada, que manda
  `X-Device-ID`/JWT automáticamente vía el interceptor global de axios — ver §5).

Al componer, llama a la función del guardián existente directamente (`await verify_device(...)`)
en vez de reimplementar su lógica — así un cambio futuro en `verify_device` se propaga sin tener
que recordar actualizar el compuesto también.

### 3.3 Scoping de usuario (anti-IDOR)

Cualquier endpoint parametrizado por `{user_id}` o similar debe pasar por `scope_user_id(current_user,
user_id)` (`deps.py`) para que un usuario no-admin solo pueda operar sobre su propia cuenta. Esto
fue el hallazgo más grave de la Fase 2.1 (cualquiera podía activar el escaparate público de otro
usuario sin autenticación) — no lo reintroduzcas al añadir un endpoint nuevo sobre datos de usuario.

### 3.4 Accesibilidad de modales (frontend): un solo hook, no reimplementar por componente

Cada modal de la app es un componente independiente (`CacheWelcomeModal`, `QuickPreviewModal`,
`MarketIntelligenceModal`, `CollectionItemDetailModal`, los internos de `Config.tsx`/`Purgatory.tsx`
— no hay un wrapper `<Modal>` compartido, cada uno reimplementa a mano el overlay `fixed inset-0` +
`AnimatePresence`). Antes de la Fase AAA-3c ninguno tenía foco atrapado, cierre con Escape, ni
`role="dialog"`. En vez de parchear cada uno con lógica distinta, usa el hook compartido
`frontend/src/hooks/useModalA11y.ts` (foco atrapado Tab/Shift+Tab, Escape cierra, foco devuelto al
elemento que abrió el modal al cerrar) — es aditivo, no cambia el JSX visual de cada modal:

```tsx
const containerRef = useRef<HTMLDivElement>(null);
useModalA11y(isOpen, onClose, containerRef);
// ...
<motion.div ref={containerRef} role="dialog" aria-modal="true" aria-labelledby="mi-titulo-id" tabIndex={-1} className="... outline-none">
  <h2 id="mi-titulo-id">Título</h2>
  <button onClick={onClose} aria-label="Cerrar">...</button>
</motion.div>
```

Reglas asociadas encontradas de verdad en esta auditoría, aplícalas a cualquier componente nuevo:
- Todo botón/enlace que solo contiene un icono (`lucide-react` sin texto visible) necesita
  `aria-label` explícito — `title` solo NO basta (falla la regla `label-title-only` de axe).
- Todo `<select>`/`<input>` necesita nombre accesible: o un `<label htmlFor="id">` con `id` en el
  control, o `aria-label`/`aria-labelledby`. Un `<label>` como hermano visual sin `htmlFor` NO
  cuenta — es el bug más repetido que se encontró (LoginPage, MasterLogin, Config.tsx).
- Un toggle real (`<button onClick={...}>` que cambia un booleano) necesita `role="switch"` +
  `aria-checked` + `aria-labelledby`/`aria-label` — no basta con el estilo visual de interruptor.
- Todo el contenido de una página debe estar dentro de un landmark (`<main>`, `<nav>` con
  `aria-label` si hay más de uno). Fondos decorativos (`position: fixed`, sin texto) llevan
  `aria-hidden="true"` para no contar en absoluto.
- Un `<div onClick=...>` sin `<button>` real necesita `role="button"` + `tabIndex={0}` +
  `onKeyDown` para Enter/Espacio — si no, es inalcanzable por teclado aunque el ratón funcione.

### 3.5 Cómo verificar accesibilidad: axe-core inyectado en vivo, no solo lectura de código

El método que encontró TODOS los problemas reales en la Fase 3c fue inyectar `axe-core` (CDN,
`https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js`) en la página real con el
dev server corriendo (`javascript_tool` del navegador embebido), no solo leer el JSX. La lectura de
código por sí sola se equivoca: un botón con `title` parece etiquetado a simple vista pero falla en
runtime (`label-title-only`); un `<label>` que visualmente está "junto" al input puede no estar
asociado en el DOM. Patrón de verificación:

```js
await new Promise((resolve, reject) => {
  const s = document.createElement('script');
  s.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js';
  s.onload = resolve; s.onerror = reject;
  document.head.appendChild(s);
});
const r = await window.axe.run(document, { resultTypes: ['violations'] });
```

Para páginas que exigen sesión/dispositivo aprobado, la única forma de probar el camino real es
registrar una cuenta desechable de verdad y aprobar su dispositivo vía la API admin real
(`POST /api/admin/devices/{device_id}/authorize` con `X-API-Key`) — no asumas que un fixture o un
mock representa lo que un usuario real ve. Esto también aplica a páginas públicas sin sesión
(`/santuario/:username`): actívalas de verdad (usa la propia UI ya arreglada) y escanéalas sin login.

---

## 4. Convenciones de testing

### 4.1 Datos reales, no mocks, para verificar `response_model`

Los tests de `tests/integration/test_api_response_schemas.py` existen para que un mismatch entre
el schema Pydantic y lo que el handler realmente devuelve se detecte como un 500
(`ResponseValidationError`) real, no solo por inspección. Al añadir un endpoint con `response_model`
nuevo (sobre todo si tiene estructuras anidadas, como `PurgatoryItemOutput.suggestions`), siembra
datos reales vía `SessionCloud` del router correspondiente y golpea el endpoint de verdad — no te
limites a comprobar que el import no falla.

### 4.2 `tests/conftest.py::_SESSION_TARGETS` debe cubrir TODOS los módulos que importan
`SessionCloud` a nivel de módulo

Bug real encontrado y corregido en esta sesión: 5 módulos de `src/application/services/*.py`
importaban `SessionCloud` a nivel de módulo pero no estaban en `_SESSION_TARGETS`, así que
usaban silenciosamente la BD real local (`oraculo.db`) durante los tests en vez de la BD de test.
**Si añades o modificas un servicio/router que hace `from src.infrastructure.database_cloud import
SessionCloud` a nivel de módulo, añádelo a `_SESSION_TARGETS` en `conftest.py`.** Si el import está
DENTRO de una función (como en `backfill_intelligence.py`), no hace falta — el atributo no existe
en el módulo hasta que la función corre, así que `unittest.mock.patch` no tiene nada que parchear
a nivel de módulo (verifica esto leyendo el archivo antes de asumir cualquiera de los dos casos).

### 4.3 Por qué la BD de test usa `NullPool` + shared-cache URI + keepalive, no `StaticPool` + `:memory:`

`StaticPool` sobre `sqlite:///:memory:` da una única conexión física compartida por todos los
`Session` de SQLAlchemy. Eso rompe en cuanto dos `Session` independientes abren un
`db.begin_nested()` (SAVEPOINT) al mismo tiempo sobre la misma conexión literal —
`sqlite3.OperationalError: no such savepoint`. Pasó de verdad al corregir el bug de §4.2 (un
handler de `purgatory.py` abre un SAVEPOINT y, dentro, `LogisticsService` abre su propio
`SessionCloud()`). La solución actual —
`file:oraculo_test_db?mode=memory&cache=shared&uri=true` + `NullPool` + una conexión keepalive
permanente— da a cada `Session` su propia conexión física (como en Postgres real) mientras todas
ven los mismos datos en memoria. **No vuelvas a `StaticPool`/`:memory:` simple aunque parezca más
simple** — ya se demostró que rompe con el patrón de sesiones anidadas que usa este código.

### 4.4 Antes de cada commit: suite COMPLETA en verde, no solo el test nuevo

`pytest tests/ -q` (todos, no solo el módulo que tocaste) antes de cualquier commit. La BD de test
es compartida entre módulos de test (session-scoped), así que un schema mal definido en un router
puede pasar limpio en un test aislado y romper cuando otro test anterior ya insertó datos con una
forma distinta — el "camino vacío" oculta mismatches que el estado compartido revela.

---

## 5. Convenciones de migraciones Alembic

- **Toda migración debe ser idempotente.** Ninguna base de datos real (ni la local `oraculo.db`
  ni, con toda probabilidad, la de producción en Supabase) ha sido nunca versionada con Alembic
  desde el principio — el esquema se ha ido creando en caliente vía `Base.metadata.create_all` /
  `ALTER TABLE` en `database_cloud.py::init_cloud_db`. Por eso cada migración debe comprobar el
  estado real antes de actuar: `sa.inspect(bind).get_columns(tabla)` antes de `add_column`,
  `sa.inspect(bind).get_indexes(tabla)` antes de `create_index`/`drop_index`. Sigue el patrón ya
  usado en `migrations/versions/d4283e0fbed1_*.py` y `feac3ac24f77_*.py`.
- **Nombra los índices igual que lo haría SQLAlchemy por defecto** (`ix_<tabla>_<columna>`) para
  que coincidan con lo que generaría `index=True` en el modelo — así una BD creada por
  `create_all` y una migrada por Alembic acaban con el mismo nombre de índice y la comprobación de
  idempotencia de la migración los reconoce como "ya existe" en vez de duplicar.
- **Verifica cada migración nueva contra una COPIA de la BD real local**, nunca contra la propia
  `oraculo.db` directamente: copia el archivo, apunta `DATABASE_URL` a la copia
  (`sqlite:///<ruta-a-la-copia>`), haz `alembic stamp <revisión-anterior>` (simula que esa copia ya
  tenía aplicado todo hasta el head previo — así el chequeo de idempotencia se prueba de verdad, en
  vez de disparar toda la cadena de migraciones desde cero contra un esquema que el `initial_migration`
  no espera), luego `alembic upgrade head`, confirma el resultado, prueba `alembic downgrade
  <revisión-anterior>` y vuelve a hacer `alembic upgrade head` para confirmar reversibilidad e
  idempotencia real.
- **Gotcha de Windows/Git Bash**: al construir la URL sqlite para una ruta de copia temporal, una
  ruta estilo Git Bash (`/c/Users/...`) NO la entiende el `sqlite3` nativo de Windows — conviértela
  primero con `cygpath -w <ruta>` y sustituye `\` por `/` antes de montar `sqlite:///<ruta>`.

---

## 6. Convenciones de commits y documentación

- **Formato de commit**: `feat(aaa-olaN-Xy): resumen corto` (p.ej. `feat(aaa-ola3-3e): indices de
  BD para cerrar huecos de EXPLAIN QUERY PLAN`), cuerpo explicando QUÉ se encontró, QUÉ se cambió y
  CÓMO se verificó (comandos/resultados concretos, no "se verificó" sin más). Termina con
  `Co-Authored-By: Claude <...>` cuando lo pida el flujo de commit estándar de la herramienta.
- **Actualiza `docs/REPORTE_MEJORAS_AAA.md` al terminar CADA ítem del backlog**, no al final de
  toda una Ola ni de tiempo en tiempo. Marca la fila con ✅ **COMPLETA (fecha)**, y sustituye la
  descripción del problema por un resumen de qué se encontró/cambió/verificó (columnas exactas,
  archivos exactos, nº de tests, resultado de la suite). Una fila que dice "pendiente" cuando ya
  está hecho es peor que no tener el documento — hace que una sesión nueva repita trabajo o, peor,
  lo deshaga por error.
- **Nunca dejes commiteado nada de `Apuntes a llevar a cabo.txt`** — es el archivo de notas
  personales del usuario, deliberadamente fuera de git (`.gitignore`), y aparece como `??` en
  `git status` en cada sesión. No lo añadas a `git add` aunque uses `git add -A` por descuido; añade
  archivos por nombre explícito.
- **Nivel de detalle exigido explícitamente por el usuario**: cada cambio debe quedar documentado
  con detalle suficiente para que otra máquina, con otro LLM, sin memoria de esta conversación,
  entienda el contexto completo solo leyendo el commit y la fila del backlog — qué se rompía antes,
  qué arregla el cambio, qué archivos toca, y cómo se comprobó que funciona.

---

## 7. Gotchas de plataforma aprendidos en esta sesión

- **El interceptor de axios es GLOBAL, no por instancia.** `frontend/src/api/client.ts` registra
  `axios.interceptors.request.use(attachAuth)` sobre el objeto `axios` importado por defecto — así
  que CUALQUIER módulo que haga `import axios from 'axios'; axios.post(...)` (como
  `frontend/src/api/wallapop.ts`) recibe automáticamente `Authorization: Bearer <jwt>` y
  `X-Device-ID`/`X-Device-Name`, aunque no use la instancia compartida `apiClient`. No asumas que un
  módulo "no manda auth" solo por no ver `apiClient` en sus imports — comprueba si el axios global
  ya lleva el interceptor antes de decidir que un endpoint necesita un mecanismo de auth nuevo para
  ese llamante.
- **Backend Python en este repo corre desde `.venv/Scripts/python.exe`** (Windows), no desde el
  `python`/`python3` del PATH del sistema — ese suele apuntar a una instalación distinta sin
  `fastapi` instalado. Verifica con `.venv/Scripts/python.exe -c "from src.interfaces.api.main import
  app"` antes de asumir que un `ModuleNotFoundError` significa un problema real de dependencias.
- **El clasificador de permisos del entorno bloquea ciertas acciones locales aunque sean seguras**
  (ej. `sqlite3` leyendo emails de `users` de la BD local, o promover un usuario de prueba a admin
  vía la API local para verificar una página solo-admin). No es un bug tuyo ni intentes rodearlo con
  otra herramienta — es una barrera de seguridad intencional. Documenta el hueco de verificación
  honestamente (qué NO se pudo probar en vivo y por qué) en vez de fingir que sí se comprobó.
- **Rutas de archivo estilo Git Bash (`/c/Users/...`) no las entiende el `sqlite3`/Python nativo de
  Windows** al construir una URL `sqlite:///...` para probar una migración contra una copia de la BD.
  Conviértelas primero con `cygpath -w <ruta>` y sustituye `\` por `/` (ver §5).

---

## 8. Qué hacer si algo de esto entra en conflicto con lo que ves en el repo

Este documento describe patrones ya validados hasta la fecha de la última actualización de la Ola
en curso. Si el código, los tests o `docs/REPORTE_MEJORAS_AAA.md` contradicen algo escrito aquí,
**el código y el documento del backlog ganan siempre** — actualiza esta skill para reflejar la
realidad nueva en vez de seguir una regla obsoleta. Este archivo debe evolucionar junto al proyecto,
igual que el backlog.

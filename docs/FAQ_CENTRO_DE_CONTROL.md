# 🏰 FAQ y Guía de Uso Integral del Centro de Control (`oraculo.ps1`)
**Oráculo de Nueva Eternia — Centro de Mando e Infraestructura Unificada**

Este documento detalla en profundidad el funcionamiento, utilidad, criticidad y modo de uso de cada una de las opciones disponibles en el panel de control de consola `oraculo.ps1`.

---

## Índice Rápido de Opciones

1. [[1] Iniciar Oráculo en Local (Backend API + Frontend Nativo)](#1-iniciar-oráculo-en-local-backend-api--frontend-nativo)
2. [[2] Iniciar Oráculo en Docker (Stack Completo Contenedores)](#2-iniciar-oráculo-en-docker-stack-completo-contenedores)
3. [[3] Ejecutar Suite Completa de Tests y Diagnóstico de Código](#3-ejecutar-suite-completa-de-tests-y-diagnóstico-de-código)
4. [[4] Iniciar Nexus Local Bridge (Worker Residencial Wallapop)](#4-iniciar-nexus-local-bridge-worker-residencial-wallapop)
5. [[5] Abrir Google Chrome en Depuración (Puerto 9222)](#5-abrir-google-chrome-en-depuración-puerto-9222)
6. [[6] Incursión Asistida Universal (CDP Multi-tienda)](#6-incursión-asistida-universal-cdp-multi-tienda)
7. [[7] Incursión Directa Multi-Tienda (Smyths, Wallapop, Vinted, eBay...)](#7-incursión-directa-multi-tienda-smyths-wallapop-vinted-ebay)
8. [[8] Desplegar y Actualizar en Oracle Cloud (1 Clic)](#8-desplegar-y-actualizar-en-oracle-cloud-1-clic)
9. [[9] Conectar por Terminal SSH al Servidor en la Nube](#9-conectar-por-terminal-ssh-al-servidor-en-la-nube)
10. [[10] Renovar Certificados SSL en Oracle Cloud (Emergencia)](#10-renovar-certificados-ssl-en-oracle-cloud-emergencia)
11. [[11] Realizar Backup Dual Completo (SQLite Local + Supabase Cloud)](#11-realizar-backup-dual-completo-sqlite-local--supabase-cloud)
12. [[12] Diagnóstico de Paridad y Salud (SQLite vs Supabase)](#12-diagnóstico-de-paridad-y-salud-sqlite-vs-supabase)
13. [[13] Sincronizar Esquemas de Base de Datos (Universal Migrator)](#13-sincronizar-esquemas-de-base-de-datos-universal-migrator)
14. [[14] Sembrar / Sincronizar Grimorio Lore Canónico (Origins Dual)](#14-sembrar--sincronizar-grimorio-lore-canónico-origins-dual)
15. [[15] Refrescar Imagen de Figura desde ActionFigure411 (Dual)](#15-refrescar-imagen-de-figura-desde-actionfigure411-dual)
16. [[16] Menú FAQ y Guía de Uso del Centro de Control](#16-menú-faq-y-guía-de-uso-del-centro-de-control)
17. [[17] Crear Accesos Directos en el Escritorio](#17-crear-accesos-directos-en-el-escritorio)

---

### [1] Iniciar Oráculo en Local (Backend API + Frontend Nativo)
* **¿Qué hace exactamente?**
  1. Detecta y termina forzosamente cualquier proceso colgado en los puertos clave de desarrollo: `8000` (FastAPI), `3001` (Vite Frontend), `5173` y `5174`.
  2. Abre una ventana de terminal dedicada ejecutando el Backend FastAPI (`python -m src.interfaces.api.main`).
  3. Abre una segunda ventana de terminal ejecutando el Frontend Vite (`npm run dev` en `/frontend`).
* **Utilidad:** Es el comando diario indispensable para programar, probar nuevas funciones o navegar la aplicación en tu máquina con recarga en caliente (*hot-reload* instantáneo).
* **Criticidad:** **CRÍTICA**. Sin él no es posible correr el entorno de desarrollo local.
* **Modo de Uso:** Pulsa `1` y Enter. Las dos ventanas se abrirán automáticamente. Entra en tu navegador a `http://localhost:3001` para ver la web o a `http://localhost:8000/docs` para la documentación Swagger de la API.

---

### [2] Iniciar Oráculo en Docker (Stack Completo Contenedores)
* **¿Qué hace exactamente?**
  Ejecuta `docker-compose down` para limpiar contenedores antiguos y a continuación `docker-compose up --build -d` para compilar y levantar todo el sistema en contenedores aislados de Docker.
* **Utilidad:** Permite probar el comportamiento idéntico al de producción en la nube (incluyendo Nginx, Redis y la API dentro de contenedores) antes de subir cambios a Oracle Cloud.
* **Criticidad:** **MEDIA**. No es obligatoria para el desarrollo diario (la opción 1 es mucho más rápida y consume menos memoria), pero es vital para validar la imagen Docker.
* **Modo de Uso:** Asegúrate de tener Docker Desktop abierto en Windows. Pulsa `2` y Enter. Accede a `http://localhost:3001` o `http://localhost`.

---

### [3] Ejecutar Suite Completa de Tests y Diagnóstico de Código
* **¿Qué hace exactamente?**
  Lanza la suite de pruebas unitarias y de integración de Python (`pytest tests/ -v`), evaluando los 35 módulos de tests (autenticación, scrapers, permisos, algoritmos de precios, Grimorio Lore, SSL, etc.).
* **Utilidad:** Garantiza que ningún cambio reciente haya roto funcionalidades preexistentes (regresiones) antes de realizar commits en Git o desplegar en la nube.
* **Criticidad:** **ALTA**. Previene fallos silenciosos en producción.
* **Modo de Uso:** Pulsa `3` y Enter. Espera a que la barra de progreso de Pytest termine e indique `PASSED` en verde.

---

### [4] Iniciar Nexus Local Bridge (Worker Residencial Wallapop)
* **¿Qué hace exactamente?**
  Ejecuta `scripts/nexus_local_worker.py`. Este proceso hace sondeos periódicos a la API del Oráculo para consultar si hay trabajos pendientes de búsqueda en Wallapop o Smyths Toys. Si existen, los procesa **desde tu ordenador personal usando tu IP residencial** (no la IP del servidor de Oracle Cloud) y envía las ofertas capturadas de vuelta al Purgatorio.
* **Utilidad:** Wallapop bloquea implacablemente las direcciones IP de centros de datos (como Oracle Cloud, AWS o Hetzner). Con este worker local, puedes encolar búsquedas desde la web o Telegram y tu PC casero las resolverá con éxito sin ser bloqueado.
* **Criticidad:** **ALTA**. Es el único puente para que Wallapop funcione sin pagar proxies residenciales costosos.
* **Modo de Uso:** Pulsa `4` y Enter. Deja la terminal abierta mientras quieras que se resuelvan búsquedas de Wallapop en segundo plano. Para detenerlo, presiona `Ctrl + C`.

---

### [5] Abrir Google Chrome en Depuración (Puerto 9222)
* **¿Qué hace exactamente?**
  Localiza tu ejecutable de Google Chrome en Windows y lo abre con un perfil de usuario aislado (`scratch/chrome_dev`) escuchando en el puerto `--remote-debugging-port=9222` con las banderas de automatización desactivadas (`--disable-blink-features=AutomationControlled`).
* **Utilidad:** Prepara el navegador para la "Incursión Asistida" (Opción 6). Te permite navegar manualmente por tiendas protegidas por Cloudflare o Datadome (Wallapop, Vinted, eBay, Smyths Toys), iniciar sesión con tu cuenta humana y resolver captchas con total tranquilidad.
* **Criticidad:** **ALTA (para evasión antibot)**. Es el primer paso para raspar tiendas con bloqueos severos.
* **Modo de Uso:** Pulsa `5` y Enter. Se abrirá una ventana limpia de Chrome. Navega a la tienda que desees consultar, entra en la sección de figuras MOTU y déjala abierta. Luego pasa a la Opción 6.

---

### [6] Incursión Asistida Universal (CDP Multi-tienda)
* **¿Qué hace exactamente?**
  Ejecuta `scripts/scrape_multi_via_cdp.py`. Se conecta mediante Chrome DevTools Protocol (CDP) a la ventana de Chrome abierta previamente en el puerto 9222, detecta automáticamente la pestaña de la tienda que estás viendo (Smyths Toys, eBay, Amazon o BBTS) y extrae las figuras y precios renderizados directamente en el DOM real.
* **Utilidad:** Es la "bala de plata" antibloqueo definitiva. Como la página ya fue cargada y aprobada por tu sesión de Chrome real, los firewalls antibot no pueden detectarlo.
* **Criticidad:** **ALTA**. Salvavidas cuando los scrapers automáticos puros son bloqueados por cambios de seguridad en las webs.
* **Modo de Uso:** Primero abre la Opción 5 y ten abierta una pestaña en la tienda con los productos visibles. Luego pulsa `6` y Enter. El script leerá la pestaña activa y guardará las ofertas en la base de datos.

---

### [7] Incursión Directa Multi-Tienda (Smyths, Wallapop, Vinted, eBay...)
* **¿Qué hace exactamente?**
  Presenta un submenú para elegir la tienda objetivo (`SmythsToys`, `Wallapop`, `Vinted`, `Ebay`, `Amazon`, `BBTS`), solicita opcionalmente un término de búsqueda (o pulsa Enter para automático) y ejecuta `scripts/run_single_incursion.py` desde tu IP residencial.
* **Utilidad:** Permite lanzar extracciones rápidas de tiendas específicas sin necesidad de abrir Chrome manual ni esperar a los cronjobs de la nube.
* **Criticidad:** **MEDIA-ALTA**. Ideal para actualizar el catálogo de Smyths Toys o rastrear ofertas frescas de Wallapop o Vinted en 30 segundos.
* **Restricción de Negocio:** *Las búsquedas vintage en scrapers de segunda mano están estrictamente inhabilitadas por normativa del proyecto.*
* **Modo de Uso:** Pulsa `7`, elige el número de la tienda (1-6) y confirma la consulta de búsqueda. Las ofertas descubiertas se guardarán automáticamente en la base de datos.

---

### [8] Desplegar y Actualizar en Oracle Cloud (1 Clic)
* **¿Qué hace exactamente?**
  1. Conecta por SSH con la clave privada `nueva-eternia-produccion.key` a tu servidor en Oracle Cloud (`opc@79.72.50.244`).
  2. Ejecuta en el servidor: `git reset --hard origin/main && git pull origin main && sudo docker compose -f docker-compose.prod.yml up -d --build`.
* **Utilidad:** Despliega todos los cambios subidos a la rama `main` de GitHub directamente en el servidor de producción en la nube sin tener que escribir comandos de consola en el VPS.
* **Criticidad:** **CRÍTICA**. Es el canal oficial de entrega y actualización a producción.
* **Modo de Uso:** Asegúrate de haber hecho `git push origin main` con tus cambios aprobados. Pulsa `8` y Enter. Al finalizar, la web estará actualizada en `https://oraculo-eternia.duckdns.org`.

---

### [9] Conectar por Terminal SSH al Servidor en la Nube
* **¿Qué hace exactamente?**
  Abre una sesión interactiva de consola SSH directa en el VPS `opc@79.72.50.244` utilizando tu clave `.key`.
* **Utilidad:** Te sitúa dentro del servidor para realizar tareas de administración de sistemas, ver logs en vivo (`docker logs -f oraculo_backend_prod`), monitorizar el uso de disco (`df -h`) o gestionar servicios.
* **Criticidad:** **ALTA**. Muy útil para soporte, diagnóstico y mantenimiento del VPS.
* **Modo de Uso:** Pulsa `9` y Enter. Aparecerá el prompt `[opc@... ~]$`. Para salir y volver al menú principal, escribe `exit` y pulsa Enter.

---

### [10] Renovar Certificados SSL en Oracle Cloud (Emergencia)
* **¿Qué hace exactamente?**
  Ejecuta en el servidor en la nube el script de renovación forzada: `bash scripts/renew_ssl.sh --force` vía SSH.
* **Utilidad:** Es la herramienta de rescate cuando los certificados Let's Encrypt de `oraculo-eternia.duckdns.org` han caducado o Nginx bloquea el tráfico HTTPS. Permite restaurar el cifrado seguro incluso si el panel web está inaccesible.
* **Criticidad:** **MEDIA**. Uso ocasional para emergencias de conectividad HTTPS.
* **Modo de Uso:** Pulsa `10` y Enter. El script regenerará el certificado con Certbot y recargará Nginx de forma automática.

---

### [11] Realizar Backup Dual Completo (SQLite Local + Supabase Cloud)
* **¿Qué hace exactamente?**
  1. Realiza una copia de seguridad segura de la base de datos local SQLite (`oraculo.db`) usando la API nativa de SQLite `backup()` en caliente hacia `backups/oraculo_YYYYMMDD_HHmm.db`, rotando y conservando los 10 últimos backups.
  2. Ofrece la opción de descargar también un snapshot completo de Supabase Cloud (PostgreSQL) hacia `backups/supabase_YYYYMMDD_HHmm.db` mediante `scripts/backup_supabase.py`.
* **Utilidad:** Protege la integridad de tus datos tanto en local como en la nube. Puedes lanzarlo también de forma silenciosa desde un acceso directo o tarea programada con el parámetro `.\oraculo.ps1 -Backup`.
* **Criticidad:** **ALTA**. Previene cualquier pérdida catastrófica de datos, historiales de precios o colecciones personales.
* **Modo de Uso:** Pulsa `11` y Enter. Confirma si deseas respaldar también Supabase Cloud.

---

### [12] Diagnóstico de Paridad y Salud (SQLite vs Supabase)
* **¿Qué hace exactamente?**
  Compara en tiempo real los datos existentes en SQLite local (`oraculo.db`) contra Supabase Cloud (PostgreSQL):
  - Número de figuras y productos en catálogo.
  - Número de ofertas y oportunidades en el Purgatorio.
  - Conteo de perfiles canónicos en el Grimorio Lore.
  - Estado de las conexiones y verificación de variables críticas (`SUPABASE_DATABASE_URL`, `TELEGRAM_BOT_TOKEN`).
* **Utilidad:** Proporciona visibilidad instantánea de si ambos entornos están sincronizados o si existen datos desfasados antes de realizar migraciones o despliegues.
* **Criticidad:** **ALTA**. Detección temprana de discrepancias en la arquitectura dual.
* **Modo de Uso:** Pulsa `12` y Enter. En 2 segundos verás la tabla comparativa en la terminal.

---

### [13] Sincronizar Esquemas de Base de Datos (Universal Migrator)
* **¿Qué hace exactamente?**
  Ejecuta `python -m src.infrastructure.universal_migrator`. Analiza los modelos de SQLAlchemy y aplica automáticamente en ambas bases de datos (SQLite local y PostgreSQL Supabase) la creación de tablas nuevas o la adición de columnas faltantes.
* **Utilidad:** Elimina la necesidad de crear migraciones manuales complejas de Alembic cuando se añaden campos al modelo (por ejemplo, campos para las cartas coleccionables, lore, precios retail, etc.).
* **Criticidad:** **ALTA**. Asegura que ambas bases de datos compartan la misma estructura de datos sin errores de columnas faltantes.
* **Modo de Uso:** Pulsa `13` y Enter cada vez que modifiques archivos en `src/domain/models.py`.

---

### [14] Sembrar / Sincronizar Grimorio Lore Canónico (Origins Dual)
* **¿Qué hace exactamente?**
  Invoca `ProductLoreSeedService.seed_canonical_characters` y `seed_origins_products` para poblar simultáneamente en **SQLite local y en Supabase Cloud**:
  - Los 54 perfiles arquetípicos de personajes MOTU en español (`motu_canon_database.py`).
  - Las 338+ figuras exclusivas de la línea Origins con sus frases del reverso de blíster (*cardback bios*), subtítulos canónicos y estadísticas equilibradas.
  - Aplica la regla estricta del proyecto: **exclusivo para Origins, omitiendo figuras Vintage**.
* **Utilidad:** Rellena y unifica toda la información del Grimorio Lore y los cromos coleccionables en ambas bases de datos con coste cero (sin consumo de tokens de IA).
* **Criticidad:** **ALTA**. Resuelve el problema del Grimorio Lore vacío y sincroniza el texto de las tarjetas coleccionables.
* **Modo de Uso:** Pulsa `14` y Enter. Se te preguntará si deseas sobreescribir los textos que no hayan sido editados manualmente.

---

### [15] Refrescar Imagen de Figura desde ActionFigure411 (Dual)
* **¿Qué hace exactamente?**
  Solicita el ID de un producto o figura (ej. `14038`), consulta ActionFigure411 para descargar la imagen en alta resolución, la optimiza y la actualiza tanto en el almacenamiento de Supabase Storage como en los registros de **SQLite local y Supabase Cloud**.
* **Utilidad:** Permite corregir rápidamente imágenes rotas o de baja calidad de una figura concreta en ambas bases de datos sin tener que buscar la URL manualmente.
* **Criticidad:** **MEDIA-BAJA**. Uso quirúrgico bajo demanda.
* **Modo de Uso:** Pulsa `15`, introduce el ID numérico de la figura y pulsa Enter.

---

### [16] Menú FAQ y Guía de Uso del Centro de Control
* **¿Qué hace exactamente?**
  Muestra una interfaz interactiva de ayuda en la propia terminal para consultar la ficha técnica de cualquiera de las opciones del menú, ver un resumen general o abrir este documento completo en tu editor de texto.
* **Utilidad:** Permite consultar qué hace cada botón sin salir de la consola y entender su utilidad y modo de uso antes de ejecutarlo.
* **Criticidad:** **INFORMATIVA**.
* **Modo de Uso:** Pulsa `16` y selecciona la opción que deseas consultar o pulsa `A` para ver el resumen completo.

---

### [17] Crear Accesos Directos en el Escritorio
* **¿Qué hace exactamente?**
  Crea o repara dos accesos directos `.lnk` en tu Escritorio de Windows:
  1. `Oraculo - Centro de Control.lnk`: lanza este menú interactivo en una ventana de PowerShell.
  2. `Oraculo - Guardian de Backups.lnk`: ejecuta una copia de seguridad inmediata silenciosa sin abrir el menú completo (`.\oraculo.ps1 -Backup`).
* **Utilidad:** Facilidad de acceso para abrir el Centro de Control con doble clic desde el escritorio sin abrir la terminal manualmente.
* **Criticidad:** **BAJA**. Se usa principalmente una vez tras clonar o reinstalar el proyecto.
* **Modo de Uso:** Pulsa `17` y Enter. Los accesos directos aparecerán en tu escritorio.

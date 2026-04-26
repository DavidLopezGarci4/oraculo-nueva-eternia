# ðŸ“– El OrÃ¡culo de Nueva Eternia: DocumentaciÃ³n Maestra

**VersiÃ³n:** 2.1.0-RECOVERY (Basado en la Fase 62)
**Ãšltima RevisiÃ³n:** Abril 2026

Este documento es la **Fuente de Verdad Absoluta** del proyecto "El OrÃ¡culo de Nueva Eternia". Se ha redactado tras una auditorÃ­a profunda del cÃ³digo fuente (`src/`, `frontend/`, `docker-compose.yml`), asegurando que describe **exactamente cÃ³mo funciona la aplicaciÃ³n hoy en dÃ­a**, sin suposiciones ni elementos obsoletos.

Cualquier desarrollador, arquitecto o auditor que necesite entender el proyecto, debe empezar por aquÃ­.

---

## 1. VisiÃ³n General y PropÃ³sito

**El OrÃ¡culo de Nueva Eternia** es una plataforma integral de inteligencia de mercado y gestiÃ³n patrimonial para coleccionistas (especÃ­ficamente enfocada en la lÃ­nea de figuras *Masters of the Universe: Origins*).

### Â¿QuÃ© hace?

1. **Inteligencia de Mercado (Scraping):** Extrae automÃ¡ticamente precios y disponibilidad de 15 tiendas de Europa y plataformas P2P (Wallapop, Vinted, eBay).
2. **Filtrado y VinculaciÃ³n (El Purgatorio):** Procesa los datos crudos, detecta anomalÃ­as, y sugiere a quÃ© figura del catÃ¡logo pertenece cada oferta (SmartMatch), dejÃ¡ndolo en un estado de "espera" hasta su validaciÃ³n humana.
3. **AnÃ¡lisis Financiero (DealScorer):** Calcula el coste real de una figura (Landed Price = Precio + EnvÃ­o + Aduanas/IVA) y asigna una puntuaciÃ³n de "Oportunidad" (1-100) frente al mercado secundario y el MSRP (Precio de salida).
4. **GestiÃ³n de ColecciÃ³n (La Fortaleza):** Permite al usuario llevar un control estricto de su colecciÃ³n personal (inversiÃ³n, estado MOC/Loose, Shelf Wear) y calcular el retorno de inversiÃ³n (ROI) en tiempo real.

---

## 2. Arquitectura Global y TopologÃ­a

La aplicaciÃ³n sigue los principios de **Clean Architecture** (Arquitectura de Cebolla) y opera bajo el estÃ¡ndar interno de resiliencia **3OX (Tier 3)**.

### 2.1 Stack TecnolÃ³gico Definitivo

| Capa | TecnologÃ­a | JustificaciÃ³n |
| :--- | :--- | :--- |
| **Frontend UI** | **React 19** + Vite | Velocidad de recarga, estado reactivo concurrente. |
| **Estilos** | **Tailwind CSS 4.0** + Framer Motion | EstÃ©tica *Glassmorphism* sin configuraciones pesadas. |
| **Peticiones/Estado** | **TanStack Query** (React Query) | Cacheo, re-fetching inteligente y gestiÃ³n de carga de la API. |
| **Backend API (Broker)**| **FastAPI** (Python 3.12+) | AltÃ­simo rendimiento, tipado estricto (Pydantic V2) y asincronÃ­a. |
| **Persistencia (Local)**| **SQLite** (`oraculo.db`) | Buffer de alta velocidad para sincronizaciÃ³n *Out-of-Band* y offline. |
| **Persistencia (Cloud)**| **PostgreSQL** (Supabase) | Fuente de verdad global, respaldada por RLS (Row Level Security). |
| **Motor de ExtracciÃ³n** | **Playwright** + BeautifulSoup4 | Capacidad de saltar bloqueos (403, 503) mediante simulaciÃ³n humana. |
| **Infraestructura** | **Docker** + Docker Compose | Despliegue industrializado, consistente entre desarrollo y producciÃ³n. |

### 2.2 TopologÃ­a de Conexiones

1. **El Frontend** se comunica **exclusivamente** con el **API Broker (FastAPI)** a travÃ©s del puerto 8000 usando JWT para autenticaciÃ³n.
2. **El API Broker** valida reglas de negocio y delega las operaciones de guardado al **MÃ³dulo de Infraestructura (SQLAlchemy)**.
3. Las operaciones pesadas (ej. Incursiones masivas) se lanzan mediante `BackgroundTasks` en FastAPI, devolviendo inmediatamente un `200 OK` al Frontend para no bloquear la UI.

---

## 3. Flujo de Datos (El Ciclo de Vida de una Oferta)

Entender cÃ³mo viaja un dato desde una tienda hasta el "Dashboard" es vital para dominar la aplicaciÃ³n. El sistema emplea una polÃ­tica de **"Purgatory-First"** (RevisiÃ³n humana obligatoria para Ã­tems nuevos).

### FASE A: IncursiÃ³n (El Pipeline)

1. El usuario (o un *cron job*) dispara la "IncursiÃ³n Total" (`POST /api/scrapers/run`).
2. El `ScrapingPipeline` inicia la recolecciÃ³n de manera **secuencial**. (Se implementÃ³ en Fase 56 para permitir **cancelaciÃ³n cooperativa** y timeouts individuales precisos de 5 minutos).
3. Cada araÃ±a (*Scraper*) devuelve objetos en bruto que pasan por un **Adapter**, generando un `receipt_id` forense.

### FASE B: Bulk Pre-Filtering & Purgatorio

El orquestador realiza una consulta masiva para evitar el temido error "N+1" (consultar la base de datos por cada Ã­tem):

1. Si el Ã­tem estÃ¡ en **Lista Negra**, se descarta silenciosamente.
2. Si el Ã­tem **ya estÃ¡ vinculado** en el catÃ¡logo, se actualiza su precio y se recalcula su puntuaciÃ³n financiera al instante.
3. Si el Ã­tem es **nuevo**, pasa directamente al **Purgatorio** (`PendingMatchModel`), guardando todos sus datos (precio, nombre, URL, imagen).

### FASE C: SmartMatch (Identidad)

El `SmartMatcher` (`matching.py`) analiza los Ã­tems del Purgatorio intentando adivinar de quÃ© figura se trata. ActÃºa como un tribunal:

- **Prueba Irrefutable (EAN):** Si hay cÃ³digo de barras, el match es 100% automÃ¡tico.
- **Test de Velocidad (Rust Kernel):** Realiza bÃºsquedas hiper-rÃ¡pidas mediante lÃ³gica de cercanÃ­a de strings.
- **El Juez SemÃ¡ntico (Python Brain & VETO):** Un motor con "pesos" IDF. Sabe que la palabra "Origins" vale mÃ¡s que "Figura". Si detecta una contradicciÃ³n flagrante (ej. coinciden en "Skeletor" pero uno es "Masterverse" y otro "Origins"), **Python aplica VETO y bloquea el Match** por seguridad.

### FASE D: ConsolidaciÃ³n Financiera (DealScorer)

Una vez que una oferta es vÃ¡lida, entra al `DealScorer`:

1. El sistema de **LogÃ­stica** calcula el `Landed Price` (si la tienda es de USA, aÃ±ade aduanas; si es Europea, aÃ±ade envÃ­os locales).
2. Se asigna una nota (0 a 100) en base a 3 vectores:
   - CuÃ¡nto descuento tiene frente al Precio Oficial (MSRP) [Max 40pts].
   - QuÃ© tan barato es frente a la media de segunda mano (P25 Floor) [Max 40pts].
   - Â¿EstÃ¡ en tu lista de deseos? [Max 20pts].
3. Si la oferta supera los 90 puntos y tiene mÃ¡s de 20% de descuento real, se dispara un **"Mandatory Buy Alert"** (Compra Obligatoria) directamente a tu Telegram.

---

## 4. Estructura de Directorios (Mapeo FÃ­sico)

Una vista resumida del interior de la arquitectura Clean:

```text
/oraculo-nueva-eternia
â”‚
â”œâ”€â”€ .env                     # [CRÃ�TICO] Secretos y configuraciones
â”œâ”€â”€ docker-compose.yml       # Orquestador local de contenedores
â”œâ”€â”€ frontend/                # AplicaciÃ³n React 19 / Vite
â”‚   â””â”€â”€ src/
â”‚       â”œâ”€â”€ api/             # Clientes axios para FastAPI
â”‚       â”œâ”€â”€ components/      # UI, Layout, Loaders (PowerSwordLoader)
â”‚       â””â”€â”€ pages/           # Vistas (Dashboard, Catalog, Purgatory...)
â”‚
â””â”€â”€ src/                     # Backend Python / FastAPI
    â”œâ”€â”€ core/                # MÃ³dulo central: config.py, matching.py, logger.py
    â”œâ”€â”€ domain/              # LÃ³gica pura: schemas.py, models.py (SQLAlchemy)
    â”œâ”€â”€ application/         # Casos de uso: deal_scorer.py, logistics_service.py
    â”œâ”€â”€ infrastructure/      # Capa externa:
    â”‚   â”œâ”€â”€ database_cloud.py# ConexiÃ³n Supabase/SQLite
    â”‚   â””â”€â”€ scrapers/        # Motores web (amazon_scraper.py, wallapop_scraper.py)
    â””â”€â”€ interfaces/
        â””â”€â”€ api/             # Capa de entrada FastAPI
            â”œâ”€â”€ main.py      # App FastAPI, middlewares y manejadores de error
            â””â”€â”€ routers/     # 12 mÃ³dulos enrutados (products.py, admin.py...)
```

---

## 5. Diccionario de Variables de Entorno (`.env`)

El sistema sigue una polÃ­tica **Zero-Leak**. Ninguna credencial se escribe en el cÃ³digo. Para levantar la aplicaciÃ³n, necesitas configurar estas variables (presentes en `src/core/config.py`).

*(AclaraciÃ³n: No se incluyen valores reales, solo las definiciones).*

| Variable | DescripciÃ³n | Estado |
| :--- | :--- | :--- |
| `DATABASE_URL` | Ruta local para el buffer rÃ¡pido. Ej: `sqlite:///./oraculo.db`. | Requerida |
| `SUPABASE_DATABASE_URL` | Connection string a la base de datos maestra en la nube. | Requerida (Cloud) |
| `SUPABASE_URL` y `KEY` | (Legacy/Opcional) Si se utiliza la API REST de Supabase directamente. | Opcional |
| `ORACULO_API_KEY` | Clave de seguridad interna. Protege los endpoints de administraciÃ³n y comandos. | Requerida |
| `JWT_SECRET` | Semilla para firmar los tokens de sesiÃ³n de usuarios (React). **CrÃ­tico cambiarla en prod.** | Requerida |
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram para alertas de "Compra Obligatoria". | Opcional |
| `TELEGRAM_CHAT_ID` | Tu ID de usuario en Telegram para que el bot sepa a quiÃ©n escribirle. | Opcional |
| `SMTP_HOST`, `SMTP_USER`... | Credenciales para envÃ­o de emails (RecuperaciÃ³n de contraseÃ±as, reportes). | Opcional |
| `CLOUDINARY_API_KEY` | (Futuro/ImÃ¡genes) Servicio de hosteo de imÃ¡genes. Actualmente usando Supabase Storage. | Opcional |
| `SOVEREIGN_EMAIL` | Email de emergencia para bypassear la seguridad y obtener rol `admin` si falla la BD. | Opcional |

---

## 6. Procedimientos Administrativos Comunes

### 6.1 Bypasseando el Firewall (Sovereign Login)

Si la base de datos se corrompe o pierdes tu cuenta, el sistema incluye un mecanismo de emergencia (*MasterLogin / ShieldBypass* en React). Si introduces el `SOVEREIGN_EMAIL` validado por el backend, obtienes poderes administrativos instantÃ¡neos, seteando tu rol localmente.

### 6.2 Modificar / AÃ±adir un Scraper

Para aÃ±adir un nuevo motor de bÃºsqueda (por ejemplo, Triguetech):

1. Crea un archivo en `src/infrastructure/scrapers/nuevo_scraper.py`.
2. Hereda de `BaseScraper` y define `shop_name` y la URL.
3. Sobrescribe el mÃ©todo `search()`.
4. **Registro Manual:** A diferencia de sistemas antiguos, los scrapers NO se autodescubren. Debes registrarlos manualmente en dos lugares clave para que sean reconocidos por el ecosistema:
   - En `src/application/jobs/daily_scan.py` (dentro de la lista `all_scrapers` para las rondas nocturnas).
   - En `src/interfaces/api/routers/scrapers.py` (dentro del diccionario `spiders_map` para ejecuciones manuales desde el admin).

#### Troubleshootings Comunes de Scrapers

- **Scraper no aparece en el Panel Admin:** AsegÃºrate de haberlo aÃ±adido en `spiders_map` de `routers/scrapers.py`.
- **Scraper de WooCommerce (ej. Triguetech) no detecta precios/stock:** WooCommerce puede variar las clases de CSS (`ins` vs `del`, `.instock` vs `.outofstock`). Si hay errores en las lecturas, inspecciona la estructura devuelta (`_parse_listing`) con BeautifulSoup y ajusta los selectores.

### 6.3 Seguridad y Permisos

- El sistema utiliza `create_access_token` basado en PyJWT para generar tokens que expiran en 24h.
- Los endpoints crÃ­ticos (`/api/admin/`, `/api/scrapers/run`) requieren validaciÃ³n de JWT y, adicionalmente, verificaciÃ³n de rol `admin` inyectado mediante dependencias de FastAPI (`get_current_user`).

---

## 7. Notas para el Futuro

- **Escalabilidad de BÃºsqueda**: Las bÃºsquedas de FastAPI actualmente tiran contra SQLite y Postgres indistintamente gracias al ORM SQLAlchemy.
- **SincronizaciÃ³n de ImÃ¡genes**: Existe un proceso secundario en GitHub Actions que sincroniza las fotos locales y genera URLs pÃºblicas (`src/application/services/storage_service.py`), evitando colapsar la base de datos con BLOBs pesados.
- **CancelaciÃ³n Cooperativa**: En `main.py` hay un `scraper_cancel_event` de tipo `threading.Event()`. Cuando un usuario hace un `POST /api/scrapers/stop`, esta bandera se levanta. El pipeline lee esta bandera entre cada iteraciÃ³n de tienda y se detiene limpiamente. No se matan procesos bruscamente.
- **MÃ³dulo Radar P2P**: El mÃ³dulo Radar P2P ha sido desactivado del menÃº principal del frontend ya que actuaba como un visor independiente de oportunidades P2P (TeorÃ­a de Cuarentena P25) y no se le estaba dando uso continuo. El cÃ³digo subyacente (`RadarP2P.tsx` y endpoint `/api/radar/p2p-opportunities`) permanece en el proyecto por si se desea reactivar en el futuro, pero no interfiere con el flujo principal ni el enrutado de React.

---
*Este documento invalida cualquier anotaciÃ³n antigua que hable de Streamlit, ejecuciÃ³n en paralelo de araÃ±as (asyncio.gather), o matching automÃ¡tico a Ciegas. La realidad del sistema es la aquÃ­ plasmada.*

---

## 8. OrquestaciÃ³n DevOps, CI/CD y Despliegue en la Nube

Para entender verdaderamente Nueva Eternia, no basta con mirar el cÃ³digo local. El sistema es un ecosistema vivo que respira gracias a la interacciÃ³n coordinada entre **GitHub**, **Oracle Cloud (OCI)** y **Docker**.

### 8.1 El Motor AutÃ³nomo (GitHub Actions)

GitHub no es solo un repositorio de cÃ³digo, actÃºa como el "cerebro cronometrado" de la aplicaciÃ³n mediante sus *Workflows* (ej. `.github/workflows/scrapers.yml`).

1. **Daily Scan (El Cronjob):** Dos veces al dÃ­a (02:00 y 14:30 UTC), GitHub levanta una mÃ¡quina efÃ­mera (`ubuntu-latest`).
2. **Nexo Maestro:** Ejecuta la sincronizaciÃ³n del catÃ¡logo (`NexusService`), inyectando las imÃ¡genes locales en **Supabase Storage**.
3. **SincronizaciÃ³n Inversa (Reverse Sync):** GitHub hace una copia de seguridad de tu base de datos de Supabase y la convierte en un archivo Excel local (`lista_MOTU.xlsx`).
4. **El Bot GuardiÃ¡n (Git Commit AutomÃ¡tico):** Un bot automatizado (`Oracle Guardian Bot`) hace `git commit` y empuja ese Excel de vuelta a tu repositorio. De este modo, siempre tienes un backup fÃ­sico versionado de tu colecciÃ³n.
5. **IncursiÃ³n de Mercado:** Finalmente, dispara `daily_scan.py` para correr los scrapers (con un `random-delay` para evitar ser baneado).

### 8.2 La Fortaleza de Cristal (Oracle Cloud - OCI)

El cÃ³digo en producciÃ³n no vive en tu PC, vive en una instancia **ARM A1 (Always Free)** en Oracle Cloud.

- **TÃºnel SSH y Firewalls:** La mÃ¡quina estÃ¡ cerrada a cal y canto. Solo permite trÃ¡fico por los puertos `80` (HTTP), `443` (HTTPS) y `22` (SSH con tu llave privada). El firewall interno de Linux (firewalld) estÃ¡ configurado en concordancia.
- **DNS DinÃ¡mico (DuckDNS):** Un script cron (`duckdns_update.sh`) se ejecuta cada 5 minutos en el servidor de Oracle para mantener el dominio `oraculo-eternia.duckdns.org` siempre apuntando a la IP pÃºblica de la mÃ¡quina.

### 8.3 La Red Contenerizada (Docker Compose Prod)

El despliegue en Oracle Cloud se realiza mediante `docker-compose.prod.yml`, que encapsula toda la complejidad:

1. **Backend (FastAPI):** Se despliega bajo un contenedor con la instrucciÃ³n `uvicorn --workers 2`, optimizando el rendimiento para producciÃ³n en la arquitectura ARM. Consume el archivo `.env` que le inyectas en el servidor.
2. **Frontend (Nginx Proxy):** El contenedor de React no se sirve directamente. Se sirve a travÃ©s de **Nginx** (puertos 80/443), el cual intercepta el trÃ¡fico.
3. **Blindaje SSL (Certbot):** Nginx utiliza certificados SSL generados por *Certbot* (Let's Encrypt), los cuales estÃ¡n mapeados en volÃºmenes (`/etc/letsencrypt`) entre la mÃ¡quina host y el contenedor.

### 8.4 El Flujo de Vida Horizontal (End-to-End)

Si observamos el ecosistema desde arriba, la interacciÃ³n completa funciona asÃ­:

1. **Desarrollo**: Programas una mejora en local (Windows) y haces `git push` a `main`.
2. **ValidaciÃ³n**: GitHub Actions (`ci.yml`) corre los tests unitarios en Python 3.10/3.11 para asegurar que no has roto nada.
3. **Despliegue**: Entras a tu servidor Oracle por SSH, haces `git pull` y ejecutas `docker compose -f docker-compose.prod.yml up -d --build`. Docker reconstruye la imagen Nginx y FastAPI en minutos.
4. **AlimentaciÃ³n**: A las 02:00 AM, GitHub despierta por su cuenta, busca ofertas, actualiza Supabase, descarga el backup en Excel y lo sube de vuelta al cÃ³digo fuente.
5. **Consumo**: Al despertar, abres `oraculo-eternia.duckdns.org` en tu mÃ³vil. Nginx verifica el SSL, el Frontend carga la UI desde cachÃ© y pide datos a FastAPI. FastAPI conecta con Supabase (donde GitHub dejÃ³ los datos nuevos de la noche) y te muestra las nuevas gangas, listas para ser validadas en el Purgatorio.

---

## 9. Ecosistema de Actores y Dependencias Externas

Para que la aplicaciÃ³n viva, se requiere la colaboraciÃ³n de diferentes actores en dos entornos diferenciados: Local y ProducciÃ³n. A continuaciÃ³n, se detalla quÃ© "fichas" intervienen en cada tablero y de quÃ© aplicaciones web externas dependemos para no colapsar.

### 9.1 Actores en Entorno Local (Modo Arca / Desarrollo)

Cuando el arquitecto programa en su PC (Windows), este es el ecosistema activo:

- **TÃº (El Desarrollador/IA):** Edita cÃ³digo en VSCode o cursor.
- **SQLite Local (`oraculo.db`):** El motor de base de datos de escritorio. Permite trabajar ultrarrÃ¡pido y offline sin gastar cuota de la nube.
- **Docker Compose Local (`docker-compose.yml`):**
  - Contenedor *Frontend* (React con Vite exponiendo localhost:3001).
  - Contenedor *Backend* (FastAPI en modo `--reload`, escuchando cambios en el cÃ³digo para reiniciarse en tiempo real).

### 9.2 Actores y Servicios Activos en ProducciÃ³n (Dependencias CrÃ­ticas)

Para que el entorno en producciÃ³n funcione de forma autÃ³noma (mientras tÃº duermes o tu PC estÃ¡ apagado), **TODOS** estos servicios web/aplicaciones deben estar activos y sanos:

1. **Oracle Cloud (OCI):**
   - *Rol:* El mÃºsculo fÃ­sico. Es el servidor ARM A1 que ejecuta el Docker de producciÃ³n. Si tu tarjeta de crÃ©dito o cuenta de Oracle se suspende, la web se cae por completo.
2. **Supabase (PostgreSQL Cloud):**
   - *Rol:* La Fuente de Verdad. Almacena todos los usuarios, sesiones (RLS) y ofertas. Si el proyecto de Supabase se pausa (por inactividad o lÃ­mites del plan Free), FastAPI lanzarÃ¡ errores 500 y no se podrÃ¡ hacer login ni ver el catÃ¡logo.
3. **DuckDNS:**
   - *Rol:* Enrutamiento. Mantiene el nombre `oraculo-eternia.duckdns.org` apuntando a la IP pÃºblica de Oracle. Si la web de DuckDNS cae, el dominio no resolverÃ¡ y los navegadores dirÃ¡n "Sitio no encontrado".
4. **GitHub (Repositorio y Actions):**
   - *Rol:* AutomatizaciÃ³n e Historia. Alberga el cÃ³digo. Si los Runners gratuitos de GitHub se agotan, los "Daily Scans" nocturnos no se ejecutarÃ¡n.
5. **Telegram Bot API:**
   - *Rol:* Comunicador. Los servidores de Telegram reciben los mensajes HTTP de FastAPI para enviarte alertas al mÃ³vil de *Mandatory Buy*.
6. **Certbot (Let's Encrypt):**
   - *Rol:* Identidad Segura. Otorga los candados verdes HTTPS gratis. Debe poder validar el puerto 80 cada 3 meses para renovarse automÃ¡ticamente.

### 9.3 Flujos de ActualizaciÃ³n a ProducciÃ³n (Las 3 VÃ­as)

Â¿CÃ³mo hago que un cambio en local aparezca en el mÃ³vil cuando entro a la web? Depende del tipo de cambio:

#### VÃ­a 1: Cambios en el CÃ³digo (Nuevos Scrapers, Cambios Visuales en UI)

1. Modificas el cÃ³digo en tu PC (VSCode/Local).
2. Haces un `git commit` y `git push origin main` para enviarlo a GitHub.
3. Te conectas por SSH al servidor de Oracle (`ssh opc@...`).
4. Bajas el cÃ³digo nuevo: `git pull origin main`.
5. Obligas a Docker a tragarse los cambios y reiniciar:

   ```bash
   sudo docker compose -f docker-compose.prod.yml up -d --build
   ```

#### VÃ­a 2: Cambios en el CatÃ¡logo de Origen (Nuevas figuras anunciadas por Mattel)

1. Actualizas tus listados / el scraper base lee `actionfigure411`.
2. Desde la interfaz web en ProducciÃ³n, pulsas el botÃ³n **"Sincro Nexo Maestro"** en ConfiguraciÃ³n.
3. El backend actualiza la nube (Supabase) al instante. Todos los mÃ³viles/PCs conectados a la web en producciÃ³n verÃ¡n las nuevas figuras inmediatamente sin tocar cÃ³digo.

#### VÃ­a 3: Modificaciones AutomÃ¡ticas (Scraping de Ofertas Diarias)

1. No haces nada.
2. A las 02:00 AM, GitHub ejecuta el cÃ³digo.
3. Encuentra nuevos precios en Wallapop, y hace `INSERT` directamente a la base de datos de Supabase.
4. Cuando entras en producciÃ³n al dÃ­a siguiente, el Frontend pide los datos a FastAPI, y FastAPI lee Supabase, mostrando los Ã­tems en el Purgatorio. Â¡ProducciÃ³n se ha actualizado de forma invisible y autÃ³noma!

### 9.4 Troubleshootings CrÃ­ticos (Emergencias)

#### A) PÃ©rdida de Acceso SSH a Oracle Cloud (Firewall/Llaves rotas)

Si pierdes el acceso a tu servidor OCI a travÃ©s de tu terminal de Windows por problemas con las llaves SSH o el firewall, **no reinstales la mÃ¡quina**. Usa la consola de emergencia del navegador:

1. Entra en `cloud.oracle.com` y ve a la pÃ¡gina de tu instancia `nueva_eternia_produccion` (o `oraculo-eternia`).
2. Baja haciendo scroll hasta el apartado **"Recursos"** (en la columna inferior izquierda de la pÃ¡gina de la instancia, no en el menÃº global).
3. Haz clic en **"Conexiones de consola"**.
4. Haz clic en **"Iniciar conexiÃ³n de consola en Cloud Shell"**.
5. Se abrirÃ¡ una terminal negra en la parte inferior de tu navegador web conectada directamente al corazÃ³n del servidor, saltÃ¡ndose las reglas SSH. Desde ahÃ­ podrÃ¡s arreglar los permisos, hacer `git pull` o relanzar Docker.

#### B) Advertencia CrÃ­tica sobre el Despliegue Docker (Prod vs Local-Prod)

En la raÃ­z del proyecto existen dos archivos de orquestaciÃ³n de producciÃ³n. Es vital **no confundirlos** al ejecutar comandos en la terminal del servidor:

- â�Œ **`docker-compose.local-prod.yml`**: Esta versiÃ³n estÃ¡ mutilada a propÃ³sito. **NO TIENE SSL (HTTPS)**. EstÃ¡ diseÃ±ada Ãºnicamente para que puedas probar la compilaciÃ³n de la imagen de producciÃ³n en tu ordenador local de Windows sin que Nginx se queje por no encontrar los certificados de Let's Encrypt.
- âœ… **`docker-compose.prod.yml`**: Este es el **ÃšNICO** archivo que debe ejecutarse en Oracle Cloud. Incluye los volÃºmenes de *Certbot* para encriptar la web y garantizar su seguridad pÃºblica.
Si por error levantas el `local-prod.yml` en la nube, la web cargarÃ¡, pero los navegadores la bloquearÃ¡n por insegura al carecer de certificados SSL.

## 9.5 Protocolo de Actualización Rápida (PowerShell)

Para actualizar la web desde tu ordenador de forma efectiva, sigue estos pasos:

### 1. Acceso al Servidor

Ejecuta esto en tu PowerShell sustituyendo tu IP:

ssh -i "C:\Users\dace8\OneDrive\Documentos\Antigravity\oraculo-nueva-eternia\tu_llave.key" opc@TU_IP_PUBLICA
2. Actualización Estándar (Si no hay conflictos)
Una vez dentro del servidor:

cd ~/oraculo-nueva-eternia && git pull origin main && sudo docker compose -f docker-compose.prod.yml up -d --build
3. Actualización Forzada (Si hay errores de Git o archivos modificados)
Usa este comando si el git pull falla o quieres limpiar el servidor y forzar la versión de GitHub:

cd ~/oraculo-nueva-eternia && git reset --hard origin/main && git pull origin main && sudo docker compose -f docker-compose.prod.yml up -d --build

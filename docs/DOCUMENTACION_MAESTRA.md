# ðŸ“– El OrÃ¡culo de Nueva Eternia: DocumentaciÃ³n Maestra

**VersiÃ³n:** 2.1.0-RECOVERY (Basado en la Fase 62)
**Ãšltima RevisiÃ³n:** Abril 2026

Este documento es la **Fuente de Verdad Absoluta** del proyecto "El OrÃ¡culo de Nueva Eternia". Se ha redactado tras una auditorÃ­a profunda del código fuente (`src/`, `frontend/`, `docker-compose.yml`), asegurando que describe **exactamente cÃ³mo funciona la aplicaciÃ³n hoy en dÃ­a**, sin suposiciones ni elementos obsoletos.

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
2. **El API Broker** valida reglas de negocio y delega las operaciones de guardado al **Módulo de Infraestructura (SQLAlchemy)**.
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

- **Prueba Irrefutable (EAN):** Si hay código de barras, el match es 100% automÃ¡tico.
- **Test de Velocidad (Rust Kernel):** Realiza bÃºsquedas hiper-rÃ¡pidas mediante lÃ³gica de cercanÃ­a de strings.
- **El Juez SemÃ¡ntico (Python Brain & VETO):** Un motor con "pesos" IDF. Sabe que la palabra "Origins" vale mÃ¡s que "Figura". Si detecta una contradicciÃ³n flagrante (ej. coinciden en "Skeletor" pero uno es "Masterverse" y otro "Origins"), **Python aplica VETO y bloquea el Match** por seguridad.

### FASE D: ConsolidaciÃ³n Financiera (DealScorer)

Una vez que una oferta es vÃ¡lida, entra al `DealScorer`:

1. El sistema de **LogÃ­stica** calcula el `Landed Price` (si la tienda es de USA, aÃ±ade aduanas; si es Europea, aÃ±ade envÃ­os locales).
2. Se asigna una nota (0 a 100) en base a 3 vectores:
   - CuÃ¡nto descuento tiene frente al Precio Oficial (MSRP) [Max 40pts].
   - QuÃ© tan barato es frente a la media de segunda mano (P25 Floor) [Max 40pts].
   - Â¿EstÃ¡ en tu lista de deseos? [Max 20pts].
3. Si la oferta supera los 90 puntos y tiene mÃ¡s de 20% de descuento real, se dispara un */oraculo-nueva-eternia
â”‚
â”œâ”€â”€ .env                     # [CRÃTICO] Secretos y configuraciones
â”œâ”€â”€ docker-compose.yml       # Orquestador local de contenedores
â”œâ”€â”€ docs/                    # Documentación del proyecto
â”‚   â””â”€â”€ manual_usuario/      # Manual de usuario interactivo (8 guías detalladas)
â”œâ”€â”€ frontend/                # AplicaciÃ³n React 19 / Vite
â”‚   â””â”€â”€ src/
â”‚       â”œâ”€â”€ api/             # Clientes axios para FastAPI
â”‚       â”œâ”€â”€ components/      # UI, Layout, Loaders (PowerSwordLoader)
â”‚       â””â”€â”€ pages/           # Vistas (Dashboard, Catalog, Purgatory...)
â”‚
â””â”€â”€ src/                     # Backend Python / FastAPI
    â”œâ”€â”€ core/                # Módulo central: config.py, matching.py, logger.py
    â”œâ”€â”€ domain/              # LÃ³gica pura: schemas.py, models.py (SQLAlchemy)
    â”œâ”€â”€ application/         # Casos de uso: deal_scorer.py, logistics_service.py
    â”œâ”€â”€ infrastructure/      # Capa externa:
    â”‚   â”œâ”€â”€ database_cloud.py# ConexiÃ³n Supabase/SQLite
    â”‚   â””â”€â”€ scrapers/        # Motores web (amazon_scraper.py, wallapop_scraper.py)
    â””â”€â”€ interfaces/
        â””â”€â”€ api/             # Capa de entrada FastAPI
            â”œâ”€â”€ main.py      # App FastAPI, middlewares y manejadores de error
            â””â”€â”€ routers/     # 12 módulos enrutados (products.py, admin.py...)
��‚   â”œâ”€â”€ database_cloud.py# ConexiÃ³n Supabase/SQLite
    â”‚   â””â”€â”€ scrapers/        # Motores web (amazon_scraper.py, wallapop_scraper.py)
    â””â”€â”€ interfaces/
        â””â”€â”€ api/             # Capa de entrada FastAPI
            â”œâ”€â”€ main.py      # App FastAPI, middlewares y manejadores de error
            â””â”€â”€ routers/     # 12 módulos enrutados (products.py, admin.py...)
```

---

## 5. Diccionario de Variables de Entorno (`.env`)

El sistema sigue una polÃ­tica **Zero-Leak**. Ninguna credencial se escribe en el código. Para levantar la aplicaciÃ³n, necesitas configurar estas variables (presentes en `src/core/config.py`).

*(AclaraciÃ³n: No se incluyen valores reales, solo las definiciones).*

| Variable | DescripciÃ³n | Estado |
| :--- | :--- | :--- |
| `DATABASE_URL` | Ruta local para el buffer rÃ¡pido. Ej: `sqlite:///./oraculo.db`. | Requerida |
| `SUPABASE_DATABASE_URL` | Connection string a la base de datos maestra en la nube. | Requerida (Cloud) |
| `IMAGE_CACHE_DIR` | Directorio local donde se guardarán las imágenes de productos (caché local). Por defecto data/image_cache. | Opcional |
| `IMAGE_CACHE_DIR` | Directorio local donde se guardarán las imágenes de productos (caché local). Por defecto data/image_cache. | Opcional |
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
- **Módulo Radar P2P**: El módulo Radar P2P ha sido desactivado del menú principal del frontend ya que actuaba como un visor independiente de oportunidades P2P (Teoría de Cuarentena P25) y no se le estaba dando uso continuo. El código subyacente (`RadarP2P.tsx` y endpoint `/api/radar/p2p-opportunities`) permanece en el proyecto por si se desea reactivar en el futuro, pero no interfiere con el flujo principal ni el enrutado de React.
- **Caché Local de Imágenes**: Para mejorar el rendimiento, el sistema cuenta con un caché local de imágenes (Phase 68) que se sirve a través de FastAPI en `/api/static/images`. Si se activa `use_local_images` en el frontend, se cargan estas imágenes locales con fallback automático en error al hotlink de origen.

---
*Este documento invalida cualquier anotaciÃ³n antigua que hable de Streamlit, ejecuciÃ³n en paralelo de araÃ±as (asyncio.gather), o matching automÃ¡tico a Ciegas. La realidad del sistema es la aquÃ­ plasmada.*

---

## 8. OrquestaciÃ³n DevOps, CI/CD y Despliegue en la Nube

Para entender verdaderamente Nueva Eternia, no basta con mirar el código local. El sistema es un ecosistema vivo que respira gracias a la interacciÃ³n coordinada entre **GitHub**, **Oracle Cloud (OCI)** y **Docker**.

### 8.1 El Motor AutÃ³nomo (GitHub Actions)

GitHub no es solo un repositorio de código, actÃºa como el "cerebro cronometrado" de la aplicaciÃ³n mediante sus *Workflows* (ej. `.github/workflows/scrapers.yml`).

1. **Daily Scan (El Cronjob):** Dos veces al dÃ­a (02:00 y 14:30 UTC), GitHub levanta una mÃ¡quina efÃ­mera (`ubuntu-latest`).
2. **Nexo Maestro:** Ejecuta la sincronizaciÃ³n del catÃ¡logo (`NexusService`), inyectando las imÃ¡genes locales en **Supabase Storage**.
3. **SincronizaciÃ³n Inversa (Reverse Sync):** GitHub hace una copia de seguridad de tu base de datos de Supabase y la convierte en un archivo Excel local (`lista_MOTU.xlsx`).
4. **El Bot GuardiÃ¡n (Git Commit AutomÃ¡tico):** Un bot automatizado (`Oracle Guardian Bot`) hace `git commit` y empuja ese Excel de vuelta a tu repositorio. De este modo, siempre tienes un backup fÃ­sico versionado de tu colecciÃ³n.
5. **IncursiÃ³n de Mercado:** Finalmente, dispara `daily_scan.py` para correr los scrapers (con un `random-delay` para evitar ser baneado).

### 8.2 La Fortaleza de Cristal (Oracle Cloud - OCI)

El código en producciÃ³n no vive en tu PC, vive en una instancia **ARM A1 (Always Free)** en Oracle Cloud.

- **TÃºnel SSH y Firewalls:** La mÃ¡quina estÃ¡ cerrada a cal y canto. Solo permite trÃ¡fico por los puertos `80` (HTTP), `443` (HTTPS) y `22` (SSH con tu llave privada). El firewall interno de Linux (firewalld) estÃ¡ configurado en concordancia.
- **DNS DinÃ¡mico (DuckDNS):** Un script cron (`duckdns_update.sh`) se ejecuta cada 5 minutos en el servidor de Oracle para mantener el dominio `oraculo-eternia.duckdns.org` siempre apuntando a la IP pÃºblica de la mÃ¡quina.

### 8.3 La Red Contenerizada (Docker Compose Prod)

El despliegue en Oracle Cloud se realiza mediante `docker-compose.prod.yml`, que encapsula toda la complejidad:

1. **Backend (FastAPI):** Se despliega bajo un contenedor con la instrucciÃ³n `uvicorn --workers 1 (reducido a 1 para evitar conflictos de webhook 409 con el bot listener de Telegram)`, optimizando el rendimiento para producciÃ³n en la arquitectura ARM. Consume el archivo `.env` que le inyectas en el servidor.
2. **Frontend (Nginx Proxy):** El contenedor de React no se sirve directamente. Se sirve a travÃ©s de **Nginx** (puertos 80/443), el cual intercepta el trÃ¡fico.
3. **Blindaje SSL (Certbot):** Nginx utiliza certificados SSL generados por *Certbot* (Let's Encrypt), los cuales estÃ¡n mapeados en volÃºmenes (`/etc/letsencrypt`) entre la mÃ¡quina host y el contenedor.

### 8.4 El Flujo de Vida Horizontal (End-to-End)

Si observamos el ecosistema desde arriba, la interacciÃ³n completa funciona asÃ­:

1. **Desarrollo**: Programas una mejora en local (Windows) y haces `git push` a `main`.
2. **ValidaciÃ³n**: GitHub Actions (`ci.yml`) corre los tests unitarios en Python 3.10/3.11 para asegurar que no has roto nada.
3. **Despliegue**: Entras a tu servidor Oracle por SSH, haces `git pull` y ejecutas `docker compose -f docker-compose.prod.yml up -d --build`. Docker reconstruye la imagen Nginx y FastAPI en minutos.
4. **AlimentaciÃ³n**: A las 02:00 AM, GitHub despierta por su cuenta, busca ofertas, actualiza Supabase, descarga el backup en Excel y lo sube de vuelta al código fuente.
5. **Consumo**: Al despertar, abres `oraculo-eternia.duckdns.org` en tu mÃ³vil. Nginx verifica el SSL, el Frontend carga la UI desde cachÃ© y pide datos a FastAPI. FastAPI conecta con Supabase (donde GitHub dejÃ³ los datos nuevos de la noche) y te muestra las nuevas gangas, listas para ser validadas en el Purgatorio.

---

## 9. Ecosistema de Actores y Dependencias Externas

Para que la aplicaciÃ³n viva, se requiere la colaboraciÃ³n de diferentes actores en dos entornos diferenciados: Local y ProducciÃ³n. A continuaciÃ³n, se detalla quÃ© "fichas" intervienen en cada tablero y de quÃ© aplicaciones web externas dependemos para no colapsar.

### 9.1 Actores en Entorno Local (Modo Arca / Desarrollo)

Cuando el arquitecto programa en su PC (Windows), este es el ecosistema activo:

- **TÃº (El Desarrollador/IA):** Edita código en VSCode o cursor.
- **SQLite Local (`oraculo.db`):** El motor de base de datos de escritorio. Permite trabajar ultrarrÃ¡pido y offline sin gastar cuota de la nube.
- **Docker Compose Local (`docker-compose.yml`):**
  - Contenedor *Frontend* (React con Vite exponiendo localhost:3001).
  - Contenedor *Backend* (FastAPI en modo `--reload`, escuchando cambios en el código para reiniciarse en tiempo real).

### 9.2 Actores y Servicios Activos en ProducciÃ³n (Dependencias CrÃ­ticas)

Para que el entorno en producciÃ³n funcione de forma autÃ³noma (mientras tÃº duermes o tu PC estÃ¡ apagado), **TODOS** estos servicios web/aplicaciones deben estar activos y sanos:

1. **Oracle Cloud (OCI):**
   - *Rol:* El mÃºsculo fÃ­sico. Es el servidor ARM A1 que ejecuta el Docker de producciÃ³n. Si tu tarjeta de crÃ©dito o cuenta de Oracle se suspende, la web se cae por completo.
2. **Supabase (PostgreSQL Cloud):**
   - *Rol:* La Fuente de Verdad. Almacena todos los usuarios, sesiones (RLS) y ofertas. Si el proyecto de Supabase se pausa (por inactividad o lÃ­mites del plan Free), FastAPI lanzarÃ¡ errores 500 y no se podrÃ¡ hacer login ni ver el catÃ¡logo.
3. **DuckDNS:**
   - *Rol:* Enrutamiento. Mantiene el nombre `oraculo-eternia.duckdns.org` apuntando a la IP pÃºblica de Oracle. Si la web de DuckDNS cae, el dominio no resolverÃ¡ y los navegadores dirÃ¡n "Sitio no encontrado".
4. **GitHub (Repositorio y Actions):**
   - *Rol:* AutomatizaciÃ³n e Historia. Alberga el código. Si los Runners gratuitos de GitHub se agotan, los "Daily Scans" nocturnos no se ejecutarÃ¡n.
5. **Telegram Bot API:**
   - *Rol:* Comunicador. Los servidores de Telegram reciben los mensajes HTTP de FastAPI para enviarte alertas al mÃ³vil de *Mandatory Buy*.
6. **Certbot (Let's Encrypt):**
   - *Rol:* Identidad Segura. Otorga los candados verdes HTTPS gratis. Debe poder validar el puerto 80 cada 3 meses para renovarse automÃ¡ticamente.

### 9.3 Flujos de ActualizaciÃ³n a ProducciÃ³n (Las 3 VÃ­as)

Â¿CÃ³mo hago que un cambio en local aparezca en el mÃ³vil cuando entro a la web? Depende del tipo de cambio:

#### VÃ­a 1: Cambios en el CÃ³digo (Nuevos Scrapers, Cambios Visuales en UI)

1. Modificas el código en tu PC (VSCode/Local).
2. Haces un `git commit` y `git push origin main` para enviarlo a GitHub.
3. Te conectas por SSH al servidor de Oracle (`ssh opc@...`).
4. Bajas el código nuevo: `git pull origin main`.
5. Obligas a Docker a tragarse los cambios y reiniciar:

   ```bash
   sudo docker compose -f docker-compose.prod.yml up -d --build
   ```

#### VÃ­a 2: Cambios en el CatÃ¡logo de Origen (Nuevas figuras anunciadas por Mattel)

1. Actualizas tus listados / el scraper base lee `actionfigure411`.
2. Desde la interfaz web en ProducciÃ³n, pulsas el botÃ³n **"Sincro Nexo Maestro"** en ConfiguraciÃ³n.
3. El backend actualiza la nube (Supabase) al instante. Todos los mÃ³viles/PCs conectados a la web en producciÃ³n verÃ¡n las nuevas figuras inmediatamente sin tocar código.

#### VÃ­a 3: Modificaciones AutomÃ¡ticas (Scraping de Ofertas Diarias)

1. No haces nada.
2. A las 02:00 AM, GitHub ejecuta el código.
3. Encuentra nuevos precios en Wallapop, y hace `INSERT` directamente a la base de datos de Supabase.
4. Cuando entras en producciÃ³n al dÃ­a siguiente, el Frontend pide los datos a FastAPI, y FastAPI lee Supabase, mostrando los Ã­tems en el Purgatorio. Â¡ProducciÃ³n se ha actualizado de forma invisible y autÃ³noma!

### 9.4 Troubleshootings CrÃ­ticos (Emergencias)

#### A) PÃ©rdida de Acceso SSH a Oracle Cloud (Firewall/Llaves rotas)

Si pierdes el acceso a tu servidor OCI a travÃ©s de tu terminal de Windows por problemas con las llaves SSH o el firewall, **no reinstales la mÃ¡quina**. Usa la consola de emergencia del navegador:

1. Entra en `cloud.oracle.com` y ve a la pÃ¡gina de tu instancia `nueva_eternia_produccion` (o `oraculo-eternia`).
2. Baja haciendo scroll hasta el apartado **"Recursos"** (en la columna inferior izquierda de la pÃ¡gina de la instancia, no en el menú global).
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

---

## 10. Segregación de Catálogos e Inteligencia Retro (Eternia Vintage)

El Oráculo ahora cuenta con una arquitectura de catálogos e inventario estrictamente segregados mediante la bandera lógica `is_vintage` a nivel de base de datos y API:

### 10.1 Estructura Relacional y Aislamiento de Datos
* **Segregación Física/Lógica:** Las figuras y ofertas de **Eternia Vintage (Clásicos de los 80)** se diferencian estrictamente de **Nueva Eternia (Origins/Moderna)** mediante la bandera `is_vintage` en la tabla `products` y `offers`.
* **Aislamiento en Posesiones:** Las posesiones de colección del usuario se dividen entre "Mi Fortaleza" (Nueva Eternia) y "Mi Fortaleza Vintage" (Eternia). Cualquier cambio en la catalogación de una figura (por ejemplo, correcciones de catalogaciones erróneas) migra de forma atómica e instantánea las posesiones de los usuarios al santuario correcto.

### 10.2 Flujos del Purgatorio Blindados (Anti-Regresión)
* **Match Estándar (Moderna):** Se eliminó la auto-promoción a vintage basada en análisis de texto sobre productos existentes. Al vincular ofertas en el drawer moderno de Nueva Eternia, el backend respeta de forma inmutable el estado `is_vintage` pre-definido en el catálogo por el Arquitecto, erradicando falsos positivos en figuras con palabras descriptivas como `"Skeletor (Vintage Sculpt)"`.
* **Segregación de Buscadores en Caliente:**
  * *Vincular de Nueva Eternia:* Tanto el buscador manual como el motor de coincidencia del Oráculo filtran estrictamente por `!is_vintage`.
  * *Vincular de Eternia:* Se implementó un algoritmo inteligente de sugerencias vintage (`vintageOracleSuggestions`) que filtra sugerencias por `is_vintage === true`, con un fallback reactivo al catálogo general vintage consultado desde `/api/products?is_vintage=true`.

### 10.3 Algoritmo de Ordenación Híbrida Retro (Eternia)
El catálogo de **Eternia Vintage** utiliza un ordenamiento diferencial jerarquizado en dos reglas que prevalecen secuencialmente:
1. **Regla Prevalente (Ofertas Activas Primero):** Se prioriza y coloca delante de todo cualquier muñeco que disponga de al menos una oferta activa en el catálogo (`best_p2p_price > 0` o detectadas por `hasMarketIntel(product.id)`). Esto garantiza que las figuras con oportunidades inmediatas de compra lideren la interfaz.
2. **Regla Secundaria (Acumulación en Purgatorio y ID Fallback):** El resto de ítems sin ofertas activas se muestran a continuación, ordenados de **mayor a menor** según el conteo de coincidencias pendientes esperando en el Purgatorio (`purgatory_match_count`). Si persisten empates (por ejemplo, muñecos con 0 ofertas y 0 coincidencias), se ordenan de **menor a mayor por su número de ID interno de la base de datos (`a.id - b.id`)** dentro de la colección.

---

## 11. Bazar del Oráculo (Lotes y Varios Retro)

Para gestionar adecuadamente ofertas que no corresponden a una única figura (como lotes de juguetes clásicos, packs variados o accesorios sueltos de Masters of the Universe), el sistema incorpora un circuito especializado:

### 11.1 Modelo y Base de Datos
* **Tabla `vintage_miscellaneous`**: Almacena ofertas de lotes con título, precio, procedencia, URL del anuncio original, imagen y notas.
* **Migración Automática**: El motor migrador de base de datos detecta y crea la tabla en el próximo arranque.

### 11.2 Flujo Operativo en el Purgatorio
1. **Desvío**: El administrador Master puede presionar "Enviar a Miscelánea (Lote / Varios)" desde el modal de emparejamiento.
2. **Registro**: El backend extrae la oferta de la cola del Purgatorio, la inyecta en la tabla de miscelánea y registra la acción `LINKED_MISCELLANEOUS` en `OfferHistoryModel`.
3. **Bazar del Oráculo**: Los lotes se presentan en una galería glassmorphic exclusiva en la pestaña **Miscelánea** de Eternia Vintage.
4. **Reversión**: Los administradores Master disponen de un botón para devolver el lote a la cola del Purgatorio (`revert_miscellaneous_item`), registrando el evento `REVERTED_MISCELLANEOUS`.


---

## 12. Normalización de URLs, Filtros de Relevancia MOTU y Calibración de Haces de Luz

La versión 2.2.0 del Oráculo implementa un blindaje de calidad de datos en el Purgatorio y una experiencia visual altamente calibrable en el Frontend:

### 12.1 Normalización Universal de URLs (Deduplicaci�n)
Para evitar la duplicaci�n de ofertas en el Purgatorio debido a parámetros de tracking o barras diagonales finales, se ha implementado la normalizaci�n universal mediante la función 
ormalize_url(url: str):
* **Remoci�n de parámetros**: Elimina todos los query parameters de tracking (ej. ?utm_source=..., ?utm_medium=...).
* **Sanaci�n de barras**: Asegura que las URLs terminen sin barras diagonales / redundantes.
* **Integridad de Datos**: Tanto los scrapers en segundo plano (pipeline.py) como la extensi�n de navegador para importaciones manuales normalizan la URL antes de intentar la inserci�n en base de datos.
* **Manejo de Colisiones**: El backend intercepta colisiones de clave �nica en base de datos (IntegrityError) y actualiza o de-duplica los registros correspondientes sin perturbar el flujo de usuario.

### 12.2 Filtro de Relevancia MOTU (Inteligencia del Purgatorio)
El pipeline incorpora un filtro autom�tico de relevancia (alidate_motu_relevance) que analiza t�tulos y descripciones de las ofertas extra�das:
* **Lista de Exclusi�n (Blacklist)**: Se descartan autom�ticamente ofertas de marcas ajenas al foco de la aplicaci�n como unko, pop (palabra completa), ig jim, masterverse, gi joe, star wars, ction man, madelman, geyperman, max steel y arbie.
* **Excepciones para Crossovers Oficiales**: Marcas que tienen crossovers oficiales con la línea Origins (ej. 	ransformers, 	hundercats, stranger things, 	mnt, 	urtles) no son excluidas de forma fulminante si vienen acompa�adas de t�rminos de He-Man/MOTU (ej. motu, origins, grayskull, he-man). Si no los contienen, se descartan de forma est�ndar.
* **Soporte Multiling�e**: Incluye soporte para traducciones europeas como la francesa maitres de l\'univers (y variantes sin ap�strofe).
* **Descarte Autom�tico a Lista Negra**: Los �tems descartados se guardan directamente en la lista negra (lackcluded_items) con el motivo correspondiente, impidiendo que vuelvan a saturar la cola del Purgatorio.

### 12.3 Limpieza Proactiva Global del Purgatorio
Al iniciar y finalizar las incursiones de scraping o las importaciones manuales, el worker ejecuta la rutina clean_purgatory_globally(). Esta rutina elimina del buffer de pendientes (PendingMatchModel) cualquier oferta cuya URL ya figure en el cat�logo principal (offers), en la lista negra (lackcluded_items) o en la secci�n del Bazar del Oráculo (intage_miscellaneous), manteniendo la base de datos libre de residuos.

### 12.4 Calibración Din�mica de Haces de Luz Vintage
El componente de carga interactiva PowerSwordLoader.tsx se ha redise�ado para admitir coordenadas din�micas para la animaci�n de haces de luz vectoriales:
* **Proyecci�n Vectorial**: A partir de la posici�n de la empu�adura (GuardX, GuardY) y la punta de la espada (TipX, TipY), el cargador calcula vectorialmente la inclinaci�n y longitud de los haces en tiempo real.
* **Calibrador Interactivo**: Se ha a�adido un calibrador en la secci�n de Ajustes (Config.tsx) con deslizadores para ajustar los ejes X e Y de guard y tip de forma visual con gu�as de depuraci�n superpuestas. Los valores calibrados se persisten en el localStorage del cliente.
* **Carga de Secci�n Vintage**: Se pre-configuraron las coordenadas �ptimas para el asset de He-Man ddg-heman.png utilizado en las pantallas de carga de las páginas Vintage: empu�adura en (79.5, 66.5) y punta en (73.0, 20.5).

### 12.5 Compactaci�n Visual de la Interfaz Core
Para optimizar el espacio en pantallas de ordenadores y dispositivos móviles y reducir el desplazamiento vertical, se ha redise�ado la rejilla de tarjetas en **Cat�logo**, **Mi Fortaleza** y **Mercader de Eternos**:
* **Tarjetas y Dock**: Compactaci�n general de m�rgenes, rellenos y tipograf�as. El dock de botones inferiores se unific� a un tama�o de h-7 w-7 con iconos de h-3.5 w-3.5.
* **Bot�n A�adir (+)**: Se increment� el contraste del bot�n de agregar en figuras no deseadas/poseídas usando el color temático de la secci�n (celeste/azul en moderno, �mbar/dorado en vintage) al 60% de opacidad en reposo y 100% al pasar el cursor (hover).
* **Cabeceras de Ordenaci�n y Contadores**: Unificaci�n de las cabeceras del panel con selector de tipo de ordenamiento, indicador de direcci�n de ordenación reactivo (ArrowUp / ArrowDown), y contador del total de �tems con iconograf�a tem�tica de color.
* **Limpieza**: Remoci�n del icono de la campana de notificaciones de la barra superior (Navbar.tsx) y eliminaci�n de su código muerto.

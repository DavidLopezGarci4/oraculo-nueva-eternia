# 📖 El Oráculo de Nueva Eternia: Documentación Maestra

**Versión:** 2.1.0-RECOVERY (Basado en la Fase 62)
**Última Revisión:** Abril 2026

Este documento es la **Fuente de Verdad Absoluta** del proyecto "El Oráculo de Nueva Eternia". Se ha redactado tras una auditoría profunda del código fuente (`src/`, `frontend/`, `docker-compose.yml`), asegurando que describe **exactamente cómo funciona la aplicación hoy en día**, sin suposiciones ni elementos obsoletos.

Cualquier desarrollador, arquitecto o auditor que necesite entender el proyecto, debe empezar por aquí.

---

## 1. Visión General y Propósito

**El Oráculo de Nueva Eternia** es una plataforma integral de inteligencia de mercado y gestión patrimonial para coleccionistas (específicamente enfocada en la línea de figuras *Masters of the Universe: Origins*).

### ¿Qué hace?
1. **Inteligencia de Mercado (Scraping):** Extrae automáticamente precios y disponibilidad de 15 tiendas de Europa y plataformas P2P (Wallapop, Vinted, eBay).
2. **Filtrado y Vinculación (El Purgatorio):** Procesa los datos crudos, detecta anomalías, y sugiere a qué figura del catálogo pertenece cada oferta (SmartMatch), dejándolo en un estado de "espera" hasta su validación humana.
3. **Análisis Financiero (DealScorer):** Calcula el coste real de una figura (Landed Price = Precio + Envío + Aduanas/IVA) y asigna una puntuación de "Oportunidad" (1-100) frente al mercado secundario y el MSRP (Precio de salida).
4. **Gestión de Colección (La Fortaleza):** Permite al usuario llevar un control estricto de su colección personal (inversión, estado MOC/Loose, Shelf Wear) y calcular el retorno de inversión (ROI) en tiempo real.

---

## 2. Arquitectura Global y Topología

La aplicación sigue los principios de **Clean Architecture** (Arquitectura de Cebolla) y opera bajo el estándar interno de resiliencia **3OX (Tier 3)**.

### 2.1 Stack Tecnológico Definitivo

| Capa | Tecnología | Justificación |
| :--- | :--- | :--- |
| **Frontend UI** | **React 19** + Vite | Velocidad de recarga, estado reactivo concurrente. |
| **Estilos** | **Tailwind CSS 4.0** + Framer Motion | Estética *Glassmorphism* sin configuraciones pesadas. |
| **Peticiones/Estado** | **TanStack Query** (React Query) | Cacheo, re-fetching inteligente y gestión de carga de la API. |
| **Backend API (Broker)**| **FastAPI** (Python 3.12+) | Altísimo rendimiento, tipado estricto (Pydantic V2) y asincronía. |
| **Persistencia (Local)**| **SQLite** (`oraculo.db`) | Buffer de alta velocidad para sincronización *Out-of-Band* y offline. |
| **Persistencia (Cloud)**| **PostgreSQL** (Supabase) | Fuente de verdad global, respaldada por RLS (Row Level Security). |
| **Motor de Extracción** | **Playwright** + BeautifulSoup4 | Capacidad de saltar bloqueos (403, 503) mediante simulación humana. |
| **Infraestructura** | **Docker** + Docker Compose | Despliegue industrializado, consistente entre desarrollo y producción. |

### 2.2 Topología de Conexiones
1. **El Frontend** se comunica **exclusivamente** con el **API Broker (FastAPI)** a través del puerto 8000 usando JWT para autenticación.
2. **El API Broker** valida reglas de negocio y delega las operaciones de guardado al **Módulo de Infraestructura (SQLAlchemy)**.
3. Las operaciones pesadas (ej. Incursiones masivas) se lanzan mediante `BackgroundTasks` en FastAPI, devolviendo inmediatamente un `200 OK` al Frontend para no bloquear la UI.

---

## 3. Flujo de Datos (El Ciclo de Vida de una Oferta)

Entender cómo viaja un dato desde una tienda hasta el "Dashboard" es vital para dominar la aplicación. El sistema emplea una política de **"Purgatory-First"** (Revisión humana obligatoria para ítems nuevos).

### FASE A: Incursión (El Pipeline)
1. El usuario (o un *cron job*) dispara la "Incursión Total" (`POST /api/scrapers/run`).
2. El `ScrapingPipeline` inicia la recolección de manera **secuencial**. (Se implementó en Fase 56 para permitir **cancelación cooperativa** y timeouts individuales precisos de 5 minutos).
3. Cada araña (*Scraper*) devuelve objetos en bruto que pasan por un **Adapter**, generando un `receipt_id` forense.

### FASE B: Bulk Pre-Filtering & Purgatorio
El orquestador realiza una consulta masiva para evitar el temido error "N+1" (consultar la base de datos por cada ítem):
1. Si el ítem está en **Lista Negra**, se descarta silenciosamente.
2. Si el ítem **ya está vinculado** en el catálogo, se actualiza su precio y se recalcula su puntuación financiera al instante.
3. Si el ítem es **nuevo**, pasa directamente al **Purgatorio** (`PendingMatchModel`), guardando todos sus datos (precio, nombre, URL, imagen). 

### FASE C: SmartMatch (Identidad)
El `SmartMatcher` (`matching.py`) analiza los ítems del Purgatorio intentando adivinar de qué figura se trata. Actúa como un tribunal:
- **Prueba Irrefutable (EAN):** Si hay código de barras, el match es 100% automático.
- **Test de Velocidad (Rust Kernel):** Realiza búsquedas hiper-rápidas mediante lógica de cercanía de strings.
- **El Juez Semántico (Python Brain & VETO):** Un motor con "pesos" IDF. Sabe que la palabra "Origins" vale más que "Figura". Si detecta una contradicción flagrante (ej. coinciden en "Skeletor" pero uno es "Masterverse" y otro "Origins"), **Python aplica VETO y bloquea el Match** por seguridad.

### FASE D: Consolidación Financiera (DealScorer)
Una vez que una oferta es válida, entra al `DealScorer`:
1. El sistema de **Logística** calcula el `Landed Price` (si la tienda es de USA, añade aduanas; si es Europea, añade envíos locales).
2. Se asigna una nota (0 a 100) en base a 3 vectores:
   - Cuánto descuento tiene frente al Precio Oficial (MSRP) [Max 40pts].
   - Qué tan barato es frente a la media de segunda mano (P25 Floor) [Max 40pts].
   - ¿Está en tu lista de deseos? [Max 20pts].
3. Si la oferta supera los 90 puntos y tiene más de 20% de descuento real, se dispara un **"Mandatory Buy Alert"** (Compra Obligatoria) directamente a tu Telegram.

---

## 4. Estructura de Directorios (Mapeo Físico)

Una vista resumida del interior de la arquitectura Clean:

```text
/oraculo-nueva-eternia
│
├── .env                     # [CRÍTICO] Secretos y configuraciones
├── docker-compose.yml       # Orquestador local de contenedores
├── frontend/                # Aplicación React 19 / Vite
│   └── src/
│       ├── api/             # Clientes axios para FastAPI
│       ├── components/      # UI, Layout, Loaders (PowerSwordLoader)
│       └── pages/           # Vistas (Dashboard, Catalog, Purgatory...)
│
└── src/                     # Backend Python / FastAPI
    ├── core/                # Módulo central: config.py, matching.py, logger.py
    ├── domain/              # Lógica pura: schemas.py, models.py (SQLAlchemy)
    ├── application/         # Casos de uso: deal_scorer.py, logistics_service.py
    ├── infrastructure/      # Capa externa:
    │   ├── database_cloud.py# Conexión Supabase/SQLite
    │   └── scrapers/        # Motores web (amazon_scraper.py, wallapop_scraper.py)
    └── interfaces/
        └── api/             # Capa de entrada FastAPI
            ├── main.py      # App FastAPI, middlewares y manejadores de error
            └── routers/     # 12 módulos enrutados (products.py, admin.py...)
```

---

## 5. Diccionario de Variables de Entorno (`.env`)

El sistema sigue una política **Zero-Leak**. Ninguna credencial se escribe en el código. Para levantar la aplicación, necesitas configurar estas variables (presentes en `src/core/config.py`).

*(Aclaración: No se incluyen valores reales, solo las definiciones).*

| Variable | Descripción | Estado |
| :--- | :--- | :--- |
| `DATABASE_URL` | Ruta local para el buffer rápido. Ej: `sqlite:///./oraculo.db`. | Requerida |
| `SUPABASE_DATABASE_URL` | Connection string a la base de datos maestra en la nube. | Requerida (Cloud) |
| `SUPABASE_URL` y `KEY` | (Legacy/Opcional) Si se utiliza la API REST de Supabase directamente. | Opcional |
| `ORACULO_API_KEY` | Clave de seguridad interna. Protege los endpoints de administración y comandos. | Requerida |
| `JWT_SECRET` | Semilla para firmar los tokens de sesión de usuarios (React). **Crítico cambiarla en prod.** | Requerida |
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram para alertas de "Compra Obligatoria". | Opcional |
| `TELEGRAM_CHAT_ID` | Tu ID de usuario en Telegram para que el bot sepa a quién escribirle. | Opcional |
| `SMTP_HOST`, `SMTP_USER`... | Credenciales para envío de emails (Recuperación de contraseñas, reportes). | Opcional |
| `CLOUDINARY_API_KEY` | (Futuro/Imágenes) Servicio de hosteo de imágenes. Actualmente usando Supabase Storage. | Opcional |
| `SOVEREIGN_EMAIL` | Email de emergencia para bypassear la seguridad y obtener rol `admin` si falla la BD. | Opcional |

---

## 6. Procedimientos Administrativos Comunes

### 6.1 Bypasseando el Firewall (Sovereign Login)
Si la base de datos se corrompe o pierdes tu cuenta, el sistema incluye un mecanismo de emergencia (*MasterLogin / ShieldBypass* en React). Si introduces el `SOVEREIGN_EMAIL` validado por el backend, obtienes poderes administrativos instantáneos, seteando tu rol localmente.

### 6.2 Modificar / Añadir un Scraper
Para añadir un nuevo motor de búsqueda:
1. Crea un archivo en `src/infrastructure/scrapers/nuevo_scraper.py`.
2. Hereda de `BaseScraper` y define `shop_name`.
3. Sobrescribe el método `search()`.
4. El backend registrará automáticamente el scraper al iniciar gracias al autodiscovery de FastAPI, sin necesidad de modificar el orquestador principal.

### 6.3 Seguridad y Permisos
- El sistema utiliza `create_access_token` basado en PyJWT para generar tokens que expiran en 24h.
- Los endpoints críticos (`/api/admin/`, `/api/scrapers/run`) requieren validación de JWT y, adicionalmente, verificación de rol `admin` inyectado mediante dependencias de FastAPI (`get_current_user`).

---

## 7. Notas para el Futuro
- **Escalabilidad de Búsqueda**: Las búsquedas de FastAPI actualmente tiran contra SQLite y Postgres indistintamente gracias al ORM SQLAlchemy.
- **Sincronización de Imágenes**: Existe un proceso secundario en GitHub Actions que sincroniza las fotos locales y genera URLs públicas (`src/application/services/storage_service.py`), evitando colapsar la base de datos con BLOBs pesados.
- **Cancelación Cooperativa**: En `main.py` hay un `scraper_cancel_event` de tipo `threading.Event()`. Cuando un usuario hace un `POST /api/scrapers/stop`, esta bandera se levanta. El pipeline lee esta bandera entre cada iteración de tienda y se detiene limpiamente. No se matan procesos bruscamente.

---
*Este documento invalida cualquier anotación antigua que hable de Streamlit, ejecución en paralelo de arañas (asyncio.gather), o matching automático a Ciegas. La realidad del sistema es la aquí plasmada.*

---

## 8. Orquestación DevOps, CI/CD y Despliegue en la Nube

Para entender verdaderamente Nueva Eternia, no basta con mirar el código local. El sistema es un ecosistema vivo que respira gracias a la interacción coordinada entre **GitHub**, **Oracle Cloud (OCI)** y **Docker**.

### 8.1 El Motor Autónomo (GitHub Actions)
GitHub no es solo un repositorio de código, actúa como el "cerebro cronometrado" de la aplicación mediante sus *Workflows* (ej. `.github/workflows/scrapers.yml`).

1. **Daily Scan (El Cronjob):** Dos veces al día (02:00 y 14:30 UTC), GitHub levanta una máquina efímera (`ubuntu-latest`).
2. **Nexo Maestro:** Ejecuta la sincronización del catálogo (`NexusService`), inyectando las imágenes locales en **Supabase Storage**.
3. **Sincronización Inversa (Reverse Sync):** GitHub hace una copia de seguridad de tu base de datos de Supabase y la convierte en un archivo Excel local (`lista_MOTU.xlsx`).
4. **El Bot Guardián (Git Commit Automático):** Un bot automatizado (`Oracle Guardian Bot`) hace `git commit` y empuja ese Excel de vuelta a tu repositorio. De este modo, siempre tienes un backup físico versionado de tu colección.
5. **Incursión de Mercado:** Finalmente, dispara `daily_scan.py` para correr los scrapers (con un `random-delay` para evitar ser baneado).

### 8.2 La Fortaleza de Cristal (Oracle Cloud - OCI)
El código en producción no vive en tu PC, vive en una instancia **ARM A1 (Always Free)** en Oracle Cloud.

- **Túnel SSH y Firewalls:** La máquina está cerrada a cal y canto. Solo permite tráfico por los puertos `80` (HTTP), `443` (HTTPS) y `22` (SSH con tu llave privada). El firewall interno de Linux (firewalld) está configurado en concordancia.
- **DNS Dinámico (DuckDNS):** Un script cron (`duckdns_update.sh`) se ejecuta cada 5 minutos en el servidor de Oracle para mantener el dominio `oraculo-eternia.duckdns.org` siempre apuntando a la IP pública de la máquina.

### 8.3 La Red Contenerizada (Docker Compose Prod)
El despliegue en Oracle Cloud se realiza mediante `docker-compose.prod.yml`, que encapsula toda la complejidad:

1. **Backend (FastAPI):** Se despliega bajo un contenedor con la instrucción `uvicorn --workers 2`, optimizando el rendimiento para producción en la arquitectura ARM. Consume el archivo `.env` que le inyectas en el servidor.
2. **Frontend (Nginx Proxy):** El contenedor de React no se sirve directamente. Se sirve a través de **Nginx** (puertos 80/443), el cual intercepta el tráfico.
3. **Blindaje SSL (Certbot):** Nginx utiliza certificados SSL generados por *Certbot* (Let's Encrypt), los cuales están mapeados en volúmenes (`/etc/letsencrypt`) entre la máquina host y el contenedor.

### 8.4 El Flujo de Vida Horizontal (End-to-End)
Si observamos el ecosistema desde arriba, la interacción completa funciona así:

1. **Desarrollo**: Programas una mejora en local (Windows) y haces `git push` a `main`.
2. **Validación**: GitHub Actions (`ci.yml`) corre los tests unitarios en Python 3.10/3.11 para asegurar que no has roto nada.
3. **Despliegue**: Entras a tu servidor Oracle por SSH, haces `git pull` y ejecutas `docker compose -f docker-compose.prod.yml up -d --build`. Docker reconstruye la imagen Nginx y FastAPI en minutos.
4. **Alimentación**: A las 02:00 AM, GitHub despierta por su cuenta, busca ofertas, actualiza Supabase, descarga el backup en Excel y lo sube de vuelta al código fuente.
5. **Consumo**: Al despertar, abres `oraculo-eternia.duckdns.org` en tu móvil. Nginx verifica el SSL, el Frontend carga la UI desde caché y pide datos a FastAPI. FastAPI conecta con Supabase (donde GitHub dejó los datos nuevos de la noche) y te muestra las nuevas gangas, listas para ser validadas en el Purgatorio.

---

## 9. Ecosistema de Actores y Dependencias Externas

Para que la aplicación viva, se requiere la colaboración de diferentes actores en dos entornos diferenciados: Local y Producción. A continuación, se detalla qué "fichas" intervienen en cada tablero y de qué aplicaciones web externas dependemos para no colapsar.

### 9.1 Actores en Entorno Local (Modo Arca / Desarrollo)
Cuando el arquitecto programa en su PC (Windows), este es el ecosistema activo:
- **Tú (El Desarrollador/IA):** Edita código en VSCode o cursor.
- **SQLite Local (`oraculo.db`):** El motor de base de datos de escritorio. Permite trabajar ultrarrápido y offline sin gastar cuota de la nube.
- **Docker Compose Local (`docker-compose.yml`):**
  - Contenedor *Frontend* (React con Vite exponiendo localhost:3001).
  - Contenedor *Backend* (FastAPI en modo `--reload`, escuchando cambios en el código para reiniciarse en tiempo real).

### 9.2 Actores y Servicios Activos en Producción (Dependencias Críticas)
Para que el entorno en producción funcione de forma autónoma (mientras tú duermes o tu PC está apagado), **TODOS** estos servicios web/aplicaciones deben estar activos y sanos:

1. **Oracle Cloud (OCI):** 
   - *Rol:* El músculo físico. Es el servidor ARM A1 que ejecuta el Docker de producción. Si tu tarjeta de crédito o cuenta de Oracle se suspende, la web se cae por completo.
2. **Supabase (PostgreSQL Cloud):** 
   - *Rol:* La Fuente de Verdad. Almacena todos los usuarios, sesiones (RLS) y ofertas. Si el proyecto de Supabase se pausa (por inactividad o límites del plan Free), FastAPI lanzará errores 500 y no se podrá hacer login ni ver el catálogo.
3. **DuckDNS:** 
   - *Rol:* Enrutamiento. Mantiene el nombre `oraculo-eternia.duckdns.org` apuntando a la IP pública de Oracle. Si la web de DuckDNS cae, el dominio no resolverá y los navegadores dirán "Sitio no encontrado".
4. **GitHub (Repositorio y Actions):** 
   - *Rol:* Automatización e Historia. Alberga el código. Si los Runners gratuitos de GitHub se agotan, los "Daily Scans" nocturnos no se ejecutarán.
5. **Telegram Bot API:** 
   - *Rol:* Comunicador. Los servidores de Telegram reciben los mensajes HTTP de FastAPI para enviarte alertas al móvil de *Mandatory Buy*.
6. **Certbot (Let's Encrypt):** 
   - *Rol:* Identidad Segura. Otorga los candados verdes HTTPS gratis. Debe poder validar el puerto 80 cada 3 meses para renovarse automáticamente.

### 9.3 Flujos de Actualización a Producción (Las 3 Vías)
¿Cómo hago que un cambio en local aparezca en el móvil cuando entro a la web? Depende del tipo de cambio:

#### Vía 1: Cambios en el Código (Nuevos Scrapers, Cambios Visuales en UI)
1. Modificas el código en tu PC (VSCode/Local).
2. Haces un `git commit` y `git push origin main` para enviarlo a GitHub.
3. Te conectas por SSH al servidor de Oracle (`ssh opc@...`).
4. Bajas el código nuevo: `git pull origin main`.
5. Obligas a Docker a tragarse los cambios y reiniciar: 
   ```bash
   sudo docker compose -f docker-compose.prod.yml up -d --build
   ```

#### Vía 2: Cambios en el Catálogo de Origen (Nuevas figuras anunciadas por Mattel)
1. Actualizas tus listados / el scraper base lee `actionfigure411`.
2. Desde la interfaz web en Producción, pulsas el botón **"Sincro Nexo Maestro"** en Configuración.
3. El backend actualiza la nube (Supabase) al instante. Todos los móviles/PCs conectados a la web en producción verán las nuevas figuras inmediatamente sin tocar código.

#### Vía 3: Modificaciones Automáticas (Scraping de Ofertas Diarias)
1. No haces nada.
2. A las 02:00 AM, GitHub ejecuta el código.
3. Encuentra nuevos precios en Wallapop, y hace `INSERT` directamente a la base de datos de Supabase.
4. Cuando entras en producción al día siguiente, el Frontend pide los datos a FastAPI, y FastAPI lee Supabase, mostrando los ítems en el Purgatorio. ¡Producción se ha actualizado de forma invisible y autónoma!

# ⚔️ El Oráculo de Nueva Eternia

> Plataforma integral de inteligencia de mercado, valoración financiera y gestión patrimonial para coleccionistas de *Masters of the Universe* (Origins y Vintage).

El Oráculo monitoriza en tiempo real más de 15 tiendas especializadas y plataformas P2P (Wallapop, Vinted, eBay), calculando el coste real puesto en casa (*Landed Price*), detectando chollos automáticos mediante el algoritmo *DealScore* y protegiendo el valor de tu colección bajo una arquitectura híbrida de alta resiliencia.

---

## ⚡ Quick Path (Puesta en Marcha en 3 Pasos)

### 1. Entorno Backend (FastAPI + SQLite WAL)
```powershell
# Activar entorno virtual e instalar dependencias
.\.venv\Scripts\activate
pip install -r requirements.txt

# Iniciar servidor API (puerto 8000)
uvicorn src.interfaces.api.main:app --reload --port 8000
```

### 2. Entorno Frontend (React 19 + Vite 7)
```powershell
cd frontend
npm install
npm run dev
# Acceder a http://localhost:5173
```

### 3. Verificación de Salud del Sistema
```powershell
# Ejecutar suite de pruebas unitarias e integración (67 tests)
python -m pytest tests/

# Comprobar estado de migraciones Alembic
python -m alembic heads
```

---

## 🏛️ Arquitectura del Sistema

| Capa | Componente | Función Principal |
| :--- | :--- | :--- |
| **Frontend UI** | **React 19 + TypeScript + Vite 7** | SPA moderna, animaciones a 60 FPS (`FoilTiltCard`), Modo Incógnito universal y *lazy loading* de cromos TCG. |
| **Backend Broker** | **FastAPI (Python 3.11+)** | API modular, tipado estricto Pydantic V2 y ejecución síncrona en threadpool para no bloquear el Event Loop. |
| **Persistencia Local** | **SQLite (`oraculo.db`)** | Buffer de alta velocidad con modo WAL (`PRAGMA journal_mode = WAL;`, `busy_timeout = 30000`) e índices de rendimiento. |
| **Persistencia Cloud** | **PostgreSQL (Supabase)** | Fuente de verdad multi-dispositivo protegida con Row Level Security (RLS) y sincronización con `SessionCloud`. |
| **Inteligencia P2P** | **Playwright + Nexus Local** | Cosecha automatizada de ofertas con evasión de WAFs, API v3 firmada y bot centinela en Telegram. |

---

## 🧭 Mapa de Documentación

Toda la documentación detallada del proyecto se organiza en el directorio [`docs/`](docs/README.md):

- 📖 **[Manual de Usuario](docs/manual_usuario/01_introduccion.md)**: Guías paso a paso para el Dashboard, la Fortaleza, los Catálogos, el Purgatorio y la Configuración.
- 📜 **[Documentación Maestra](docs/DOCUMENTACION_MAESTRA.md)**: Explicación exhaustiva del pipeline de datos, algoritmos de scoring y seguridad.
- 🔮 **[Master Roadmap](docs/MASTER_ROADMAP.md)**: Evolución SMART por fases y visión técnica.
- 📋 **[Log Maestro de Operaciones](docs/technical/LOG_MAESTRO_NUEVA_ETERNIA.md)**: Bitácora cronológica con las 100 fases operativas completadas.
- ❓ **[Preguntas Frecuentes (FAQ)](docs/FAQ.md)**: Respuestas rápidas sobre Modo Incógnito, cromos TCG, alertas de Telegram y exportaciones.

---

## ✅ Checklist de Verificación de Salud

- [ ] Backend responde `{"status": "healthy"}` en `http://localhost:8000/api/health`.
- [ ] Base de datos SQLite opera en modo WAL (`PRAGMA journal_mode;` devuelve `wal`).
- [ ] La compilación del frontend completa con 0 errores (`npm run build` en `frontend/`).
- [ ] Las 67 pruebas automatizadas pasan al 100% (`pytest tests/`).
- [ ] Modo Incógnito difumina correctamente métricas de inversión y oculta inputs manuales sin fuga por hover.

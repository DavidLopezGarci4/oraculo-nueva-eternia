# Auditoría de carpetas de la raíz — qué se usa y qué no (2026-07-21)

> **Propósito.** El usuario alterna entre máquinas y herramientas de IA distintas (Claude Code,
> posiblemente 3OX.Ai, Gemini/Antigravity, y el framework detrás de `.agent`/`.agents`/`.pi`).
> Este documento deja constancia de qué carpetas de la raíz confirmé en uso real por **esta
> aplicación** (backend FastAPI + frontend React, tests, CI, Docker) y cuáles NO — para que
> cualquier sesión futura, en cualquier máquina, decida qué hacer con las segundas sin tener que
> repetir la investigación. **No se ha borrado ni movido nada** — es solo un mapa de evidencia.
>
> Metodología: cada carpeta/archivo se contrastó contra `src/`, `frontend/src/`, `tests/`,
> `scripts/`, `Dockerfile`, `docker-compose*.yml`, `.dockerignore`, `pyproject.toml`,
> `requirements.txt` y los dos workflows de `.github/workflows/` (`ci.yml`, `scrapers.yml`) —
> búsqueda de referencias reales (imports, rutas leídas en runtime, comandos ejecutados), no solo
> presencia del nombre.

## Leyenda

- ✅ **Usado directamente** — referenciado de verdad por la app, los tests, CI o Docker. Evidencia citada.
- 🔧 **Operación manual del usuario** — no lo toca la app en automático, pero es tooling real que tú ejecutas a mano (launchers, backups, scrapers asistidos).
- ❓ **No usado por esta app — posible otra herramienta** — cero referencias en el código/CI/Docker, pero coincide con la convención de otra herramienta de IA que puede que sigas usando. **No tocar sin decidirlo explícitamente.**
- 🗑️ **Sin ninguna referencia detectada** — ni en la app, ni en otra herramienta identificable. Candidato a basura, pero sigue sin tocarse hasta que lo confirmes.
- ⚠️ **Contradicción detectada** — un documento existente en el propio repo dice una cosa y mi auditoría dice otra (detalle en la nota).

---

## Árbol

```
oraculo-nueva-eternia/
├── src/                          ✅ Backend FastAPI. CMD del Dockerfile, target de pytest, todo el negocio.
├── frontend/                     ✅ SPA React/Vite. job "frontend" de ci.yml, servido por nginx en docker-compose.
├── tests/                        ✅ Suite pytest real (pyproject.toml: testpaths=["tests"]). Job "backend" de ci.yml.
├── migrations/                   ✅ Alembic — alembic.ini apunta aquí (script_location).
├── scripts/                      ✅ scrapers.yml ejecuta scripts/sync_excel_from_db.py. Resto son herramientas de mantenimiento reales (ver docs/technical/architecture_map.md §5).
│   └── (subcarpetas diagnostics/audits/maintenance/experimental/smoke) ✅ Documentadas y en uso, ver architecture_map.md.
├── data/                         ✅ scrapers.yml lee/escribe data/MOTU/lista_MOTU.xlsx. Resto son perfiles/evals de scrapers (data/profile_*.json, data/*_eval.json).
├── chrome-extension/             ✅ Extensión real (popup/content.js → POST /api/wallapop/import), documentada y arreglada en Fase AAA-3d.
├── deploy/                       ✅ Guía de despliegue OCI + scripts de servidor (duckdns_update.sh, setup_server.sh) — uso manual real del usuario en la máquina con Docker.
├── vec3/                         ✅ `vec3/var/receipts/` es donde escribe de verdad `AuditorService` (src/application/services/auditor.py). Vacío en disco pero activo — no es basura aunque git no lo trackee.
├── .venv/                        ✅ Entorno virtual Python del proyecto (gitignored, obviamente necesario localmente).
├── .git/, .claude/               ✅ Control de versiones y config de Claude Code (esta herramienta).
│
├── .devcontainer/                🗑️ Apunta a `original_app.py` (ya NO EXISTE en el repo) y lanza `streamlit run` — Streamlit no es dependencia del proyecto desde hace fases. Resto de un devcontainer de la era Streamlit, previa a la reescritura a FastAPI+React.
├── dev_tools/                    🗑️ 39 archivos de scraping exploratorio (analyze_*, test_tradeinn_*, logs .txt). El propio ci.yml lo cita en un comentario explicando que ANTES se colaba por error en CI y que ya está corregido — confirma que hoy no se ejecuta desde ningún sitio.
├── brain.rs                      🗑️⚠️ Un solo `println!`, no se compila (no hay Cargo.toml en la raíz). architecture_map.md lo lista como "Activo" — contradicción, ver nota abajo.
├── run.rb                        🗑️ Un solo `puts`, sin runtime Ruby en el proyecto, cero referencias.
├── routes.json                   🗑️ Texto declarativo (rutas a scripts .py), no lo lee ningún código — las rutas reales se invocan directo desde ci.yml/scrapers.yml, no desde aquí.
├── limits.json                   🗑️ Cero referencias.
├── tools.yml                     🗑️ Registro decorativo de "herramientas", cero referencias.
├── sparkfile.md                  🗑️⚠️ Spec de "agente" en prosa. architecture_map.md lo lista como "Activo" — contradicción, ver nota abajo.
├── dependency_audit.txt          🗑️ 23 KB, salida de una auditoría de dependencias ya volcada a fichero. Cero referencias.
├── packages.txt                  🗑️ Paquetes apt (libnss3, etc.) — solo los usa `.devcontainer/devcontainer.json`, que es él mismo 🗑️.
├── Oraculo.lnk                   🗑️ Acceso directo de Windows (binario, específico de una máquina) comiteado a git. No debería versionarse en absoluto, sea cual sea su destino.
│
├── .3ox/                         ❓ Cargo.toml/.rs (Rust) + routes.json/limits.toml/run.rb/sparkfile.md/tools.yml — mismos nombres que los archivos 🗑️ de la raíz, pero como workspace de una herramienta ("3OX.Ai" según el comentario en .gitignore). Sin Rust en el resto del proyecto (app es Python+TS).
├── .agent/                       ❓ Skills "3ox-project-manager", "3ox-windows-search", "project-roadmap" — de la misma familia que .3ox/.
├── .agents/ + skills-lock.json   ❓ Skills de seguridad genéricas (OWASP, Trivy, secrets-scanning) bajo convención AGENTS.md — framework de agente distinto a .agent/.3ox por la convención de nombres.
├── .gemini/                      ❓ `.gemini/antigravity/brain/<uuid>/walkthrough.md` — carpeta de trabajo de Gemini/Antigravity IDE.
├── .pi/settings.json             ❓ Config de una herramienta no identificada ("Pi").
│
├── logs/, backups/, scratch/     🔧 Gitignored, runtime local (backups de BD, logs, scratch de debug). No son "código del proyecto", son salida generada — no hay nada que decidir, se regeneran solos.
├── oraculo.db*, *.db-wal/-shm    🔧 Base de datos SQLite local de desarrollo — gitignored, esperado.
├── *.ps1 / *.bat (raíz)          🔧 Launchers y scrapers asistidos reales que ejecutas tú a mano (launch_ark.ps1, run_wallapop_attached.ps1, run_nexus_bridge.ps1, backup_db.ps1, etc.) — confirmados legítimos, no son residuos.
├── Apuntes a llevar a cabo.txt   🔧 Tus notas personales, gitignored por diseño.
└── CREDENCIALES_LOCAL.md         🔧 Notas de credenciales locales, gitignored por diseño ("NUNCA subir a git").
```

---

## ⚠️ Contradicción con `architecture_map.md`

`docs/technical/architecture_map.md` (documento ya existente en el repo, de una sesión/herramienta
anterior) tiene una sección **"1. Núcleo de Control (Core 3OX)"** que lista `brain.rs`,
`sparkfile.md` y `Dockerfile`/`docker-compose.yml`/`launch_ark.ps1` juntos como **"Activo"**,
tratando los archivos de temática 3OX como parte real de la arquitectura de control del agente.

Mi auditoría (grep de referencias reales en `src/`, `frontend/src/`, Docker, CI) **no encuentra
ninguna llamada, import ni lectura en runtime** de `brain.rs`, `sparkfile.md`, `routes.json`,
`limits.json` ni `tools.yml` desde el código que realmente se ejecuta. Las dos cosas pueden ser
ciertas a la vez sin contradicción real: puede que esos archivos SÍ sean "activos" para la
herramienta de IA que los generó (ej. 3OX.Ai los lee como su propio contexto/spec), simplemente
**no para esta aplicación (el backend/frontend que corre en Docker)**. Por eso estos archivos
están marcados 🗑️ (sin uso por la app) y no ❓ (herramienta externa) — a diferencia de `.3ox/`,
`.agent/`, etc., que SÍ son carpetas de configuración reconocibles de una herramienta, estos son
archivos sueltos en la raíz sin extensión de "carpeta de config" clara. Aun así, decídelo tú: si
sigues usando la herramienta que los generó y los lee desde la raíz (no desde `.3ox/`), trátalos
como ❓, no 🗑️.

---

## Resumen accionable

| Categoría | Carpetas/archivos | Acción sugerida |
|---|---|---|
| 🗑️ Sin ninguna referencia | `.devcontainer/`, `dev_tools/`, `brain.rs`, `run.rb`, `routes.json`, `limits.json`, `tools.yml`, `sparkfile.md`, `dependency_audit.txt`, `packages.txt`, `Oraculo.lnk` | Candidatos a cuarentena/borrado — pendiente de tu confirmación explícita (ver conversación 2026-07-21). |
| ❓ Otra herramienta, en uso confirmado | `.3ox/`, `.agent/`, `.agents/`, `.gemini/`, `.pi/`, `skills-lock.json` | **No tocar** — confirmaste el 2026-07-21 que sigues usando alguna de estas herramientas en tu otra máquina. |
| ⚠️ Doc desactualizado | `docs/technical/architecture_map.md` §1 | Revisar y corregir en una sesión futura si se decide limpiar la raíz — hoy describe como "Activo" archivos sin uso real por la app. |

*Generado por Claude Code (Sonnet 5) el 2026-07-21, a petición explícita del usuario, sin borrar
ni mover ningún archivo.*

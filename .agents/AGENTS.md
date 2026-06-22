# Reglas del Proyecto: Oráculo de Nueva Eternia

Este archivo contiene las directrices de arquitectura y comportamiento para cualquier agente de IA que trabaje en este espacio de trabajo.

---

## 1. Metodología de Desarrollo (SDD)
*   **Obligatorio:** Todo desarrollo complejo, refactorización o cambio arquitectónico debe seguir la skill `specification-driven-development`.
*   No se debe programar "al vuelo" (*vibe coding*). Se debe consensuar primero un glosario/contexto y un plan técnico antes de modificar ficheros.

---

## 2. Restricciones Técnicas y Reglas de Negocio
*   **Búsquedas Vintage Inhabilitadas (Temporal):** Está estrictamente prohibido activar o re-habilitar las búsquedas de artículos vintage o de la década de los 80 en los scrapers de eBay, Wallapop y Amazon. Mantener estas consultas desactivadas hasta orden explícita del usuario.
*   **Base de Datos y Sincronización:** El backend expone datos locales en SQLite (`oraculo.db`) y realiza sincronizaciones en Supabase (PostgreSQL). Mantener la coherencia de esquemas entre ambas bases de datos al añadir tablas o campos.
*   **Precios Manuales:** Asegurarse de que las casillas de precios insertados manualmente en Nueva Eternia y Eternia oculten correctamente los valores (difuminado/opacidad) y no muestren el valor real al posar el cursor, a menos que el usuario lo tenga configurado o permitido.

---

## 3. Guías de Código
*   **Backend:** Python 3.11+, FastAPI, SQLAlchemy (v2.0), Alembic para migraciones.
*   **Frontend:** React + Vite + TypeScript en `/frontend`. Utilizar CSS Vanilla con tokens de diseño limpios y modernos.
*   **Scrapers:** Usar `playwright` o `curl_cffi` para peticiones resilientes. Controlar siempre los tiempos de espera y la evasión de bloqueos.

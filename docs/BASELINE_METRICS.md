# Línea Base de Métricas — antes del uplift AAA

> Capturado en Fase 0 sobre la rama `refactor/aaa-uplift`. Fecha: 2026-07-21.
> Sirve para medir la mejora al final (Fase 8). **No editar los valores de partida.**

## Build de producción (`npm run build`, Vite 7)

El code-splitting por página **ya funciona** (lazy-loading en `App.tsx`). Chunks relevantes:

| Chunk | Raw | Gzip | Nota |
|-------|-----|------|------|
| `index` (entry) | 431.12 KB | **140.86 KB** | react + react-dom + framer-motion + react-query core. Objetivo: separar vendors para cache. |
| `CategoricalChart` (recharts) | 315.12 KB | 97.59 KB | Lazy (solo en vistas con gráficas). Candidato a aligerar. |
| `Config` | 123.86 KB | 27.47 KB | Monolito de 3072 líneas. |
| `Purgatory` | 80.76 KB | 18.45 KB | Monolito de 2253 líneas. |
| `products` (capa API/query compartida) | 61.73 KB | 16.50 KB | |
| `Catalog` | 61.72 KB | 15.08 KB | Monolito de 1965 líneas. |
| `Collection` | 47.85 KB | 11.75 KB | |
| `Dashboard` | 42.02 KB | 8.54 KB | |
| `Auctions` | 27.11 KB | 7.34 KB | |

**Carga inicial estimada (login/dashboard):** `index` (140.86 KB gz) + chunk de la primera ruta. Recharts NO entra en la carga inicial (bien).

## Activos pesados (problema principal de rendimiento)

- **`frontend/src/assets`: 17.1 MB de PNG.** Con duplicados: existen `.webp` junto a `.png` y versiones `old.*`/`olld*`. Fondos a resolución completa (`bg-heman.png`, `Entrance_prod.png`).
- `dist` total ≈ 18 MB (dominado por imágenes copiadas).

## Backend / API

- 89 endpoints en 15 routers. Cobertura de auth dispar: `admin` 14/14 con `Depends`, pero `collection` 0/6, `vault` 0/4, `logistics` 0/1.
- Sin `.env` local presente → la app corre hoy con defaults inseguros (`JWT_SECRET` de ejemplo, `ORACULO_API_KEY = eternia-shield-2026`).

## Pendiente de capturar (requiere entorno corriendo)

- [ ] Lighthouse (Performance / Accessibility / Best-Practices / SEO) en `dashboard`, `catalog`, `collection`.
- [ ] LCP, TBT, CLS reales.
- [ ] `npm audit` y `pip-audit`.

## Objetivos AAA (criterios de aceptación, Fase 8)

- Entry inicial < 250 KB gz (hoy 140.86 — ya cumple; mantener tras cambios y mejorar cache-hit con vendor split).
- Imágenes iniciales reducidas > 80%.
- Lighthouse Performance ≥ 90, Accessibility ≥ 95.
- LCP < 2.5 s; transición entre secciones < 200 ms percibidos.
- 0 hallazgos críticos/altos en `/security-review`.

---

## Métricas finales (tras Fases 0–2, 3.1 y parte de la 4) — 2026-07-21

> Pendiente aún de capturar con entorno corriendo: Lighthouse/LCP/TBT/CLS reales (fuera de alcance sin un despliegue accesible). Lo demás, medido directamente.

### Build de producción

| Chunk | Antes (raw / gzip) | Ahora (raw / gzip) |
|-------|---------------------|----------------------|
| `index` (entry) | 431.12 KB / 140.86 KB | **274.84 KB / 88.70 KB** |
| Vendors | (mezclados en `index`) | separados: `vendor-react` 14.56 KB, `vendor-query` 13.79 KB, `vendor-motion` 38.65 KB, `vendor-icons` 8.63 KB gz (cacheables independientemente) |
| `vendor-charts` (recharts) | 315.12 KB / 97.59 KB (dentro de `CategoricalChart`) | 361.25 KB / 107.56 KB (lazy, fuera de la carga inicial) |

Entry inicial: **140.86 KB → 88.70 KB gzip** (-37%). Objetivo de <250 KB gz ya se cumplía antes; ahora con más margen y mejor cache-hit entre despliegues (los vendors no cambian de hash si no cambia la librería).

### Activos

- `frontend/src/assets`: **17.1 MB → 412 KB** (-97.6%). 16 archivos sin usar eliminados (duplicados PNG/webp, copias `old.*`, `react.svg` de plantilla). Verificado en navegador real que ninguna imagen quedó rota.
- `dist` total: 18 MB → 11 MB (el resto lo domina `public/theme.mp3`, 8.2 MB, fuera de alcance de esta limpieza — es audio, no imagen).
- Cerrado el hueco de conversión a WebP: las imágenes de producto nuevas (descubiertas por los scrapers de tienda) ahora se descargan, convierten y cachean automáticamente en su primera petición (`main.py::_fetch_and_cache_product_image`), no solo las del importador antiguo de Excel.

### Backend / API

- Cobertura de auth: de "dispar" (varios routers con 0 endpoints protegidos) a **auditados los 89 endpoints**, con los vacíos reales cerrados (el más grave: activación no autenticada del escaparate público de cualquier usuario).
- `ORACULO_API_KEY` ya no viaja al navegador; el modelo de auth del frontend es JWT real via login.
- `pip-audit`: no ejecutado formalmente esta sesión (dependencias fijadas en 2.6, sin CVEs conocidos evaluados manualmente). `npm audit`: 5 vulnerabilidades → **0** (`npm audit fix`, sin `--force`).
- 46+ tests de integración nuevos/actualizados cubriendo IDOR, scoping de identidad, response_model y la cache de imágenes; suite completa en verde en cada commit de esta sesión.

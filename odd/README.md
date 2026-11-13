# Organic Driven Development (ODD — Gentle AI v4)

Este directorio aloja los contratos ligeros de ejecución ODD para iniciativas grandes o multifase en **Oráculo de Nueva Eternia**, regido por las skills globales `gentle-ai` y `work-unit-commits`.

## Enrutamiento Elástico por Tamaño de Tarea

| Tamaño | Criterio | Flujo Obligatorio |
| :--- | :--- | :--- |
| **Pequeña / Mediana** | Bugfix acotado, mejora puntual o `< 400` líneas estimadas | Ciclo directo `RED -> GREEN -> REFACTOR` en tests + código, sin documento previo en `odd/tasks/`. |
| **Grande / Multifase** | Auditoría amplia, refactorización transversal o múltiples slices | Archivo de contrato ligero en `odd/tasks/<slug>.md` con criterios de aceptación, límites `<= 400` líneas por unidad de trabajo, evidencia de tests y límites de rollback. |

## Reglas de Oro
1. **Unidades Atómicas (`work-unit-commits`):** Cada unidad entrega comportamiento + tests + docs juntos y mantiene los slices revisables (`<= 400` líneas por commit/PR cuando aplique).
2. **Evidence-First:** Nunca marcar una unidad como completada sin registrar el comando ejecutado y el resultado exacto observado.
3. **Glosario Vivo:** Los invariantes estructurales, RLS y fronteras de dominio viven en `docs/CONTEXT.md`.

---
name: specification-driven-development
description: Metodología estructurada de desarrollo guiado por especificaciones (SDD) inspirada en Spec-Kit y Grill-with-Docs. Evita la improvisación (vibe coding) mediante entrevistas previas y planificación técnica paso a paso.
---

# Desarrollo Guiado por Especificaciones (Specification-Driven Development - SDD)

Este Skill define el flujo de trabajo obligatorio cuando se solicitan nuevas funcionalidades complejas, cambios de arquitectura o refactorizaciones mayores en el proyecto.

## Flujo de Trabajo

### Fase 1: Alineación del Dominio y Vocabulario (Grill-with-Docs)
Antes de escribir cualquier especificación técnica, el agente debe "interrogar" al desarrollador mediante una breve entrevista interactiva para definir el contexto del dominio.
*   **Objetivo:** Crear o actualizar un archivo `CONTEXT.md` en el directorio de documentación del proyecto.
*   **Preguntas clave:**
    1.  ¿Qué términos de negocio clave definen esta feature? (ej. ¿Qué diferencia hay entre un "item" y un "catálogo"?).
    2.  ¿Qué restricciones o reglas técnicas innegociables existen? (ej. versiones de librerías, uso de APIs de terceros).
    3.  ¿Cómo se mapea esto al stack del proyecto (FastAPI, React, SQLite/Supabase)?

### Fase 2: Plan de Implementación Técnico (Spec-Kit Plan)
Una vez definido el dominio, el agente debe generar un archivo de propuesta `implementation_plan.md` en el directorio de la conversación o de documentación del proyecto.
*   **Contenido obligatorio:**
    *   **Propósito:** Descripción breve y clara del cambio.
    *   **Efectos Secundarios:** Impacto en bases de datos, integraciones de red o rendimiento.
    *   **Archivos Modificados:** Lista de archivos con marcas `[MODIFY]`, `[NEW]` o `[DELETE]`.
    *   **Verificación:** Plan de pruebas automatizadas y manuales.
*   **Aprobación:** El desarrollador debe dar luz verde al plan antes de proceder a la ejecución.

### Fase 3: Desglose de Tareas (Spec-Kit Tasks)
Una vez aprobado el plan técnico, se debe crear un archivo `task.md` con un listado de tareas pendientes (ToDo List).
*   **Formato de Tareas:**
    *   `[ ]` Tarea pendiente
    *   `[/]` Tarea en progreso
    *   `[x]` Tarea completada

### Fase 4: Implementación y Verificación
*   Realizar cambios de forma incremental, marcando las tareas completadas en `task.md`.
*   Ejecutar pruebas y validar que se cumplen los requisitos.
*   Generar un informe final `walkthrough.md` resumiendo las modificaciones realizadas y los resultados de las pruebas.

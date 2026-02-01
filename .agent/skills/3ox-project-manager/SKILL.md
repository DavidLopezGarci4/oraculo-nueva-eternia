---
name: 3ox-project-manager
description: Gestiona la documentación de avances, roadmap de valor y actualización de arquitectura. Úsalo al finalizar cada fase o cambio importante.
---

# 3OX Project Management: Log, Roadmap, README & Codex

Este skill asegura que la estructura y el progreso del proyecto sean siempre visibles y precisos.

## 1. Tetralogía de Documentación Obligatoria
Tras cada cambio importante o fase completada, debes actualizar:

- **3ox.log / LOG_MAESTRO:** Registrar la acción realizada usando Sirius Time y el ciclo 3OX.
- **MASTER_ROADMAP.md:** Proponer activamente futuras incorporaciones de valor. Las propuestas deben ser **SMART** y alineadas con la lógica de negocio del programa.
- **PROJECT_CODEX.md:** Mantener una guía incremental de la sinergia técnica, combinando herramientas, procesos y arquitectura.
- **README.md:** Actualizar tecnologías, lenguajes y versiones. 
    - **Mapeo de Conexiones:** Describir la relación entre tecnologías y la jerarquía de carpetas (ej. cómo `dev/` interactúa con el kernel).

## 2. Auditoría de Estructura
- Mantener actualizado el `architecture_map.md` (Árbol de Correlación).
- Marcar archivos obsoletos como `[DEPRECATED]`.
- Verificar que las conexiones entre archivos sigan la lógica de superficies protegidas de 3OX.

## 3. Entrega de Commit
Al finalizar, proporcionar siempre un Título y Descripción para el commit de GitHub que refleje los cambios realizados.
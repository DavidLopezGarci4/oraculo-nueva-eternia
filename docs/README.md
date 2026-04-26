# 🔮 El Oráculo de Nueva Eternia

**Centro de Inteligencia de Mercado y Gestión de Colecciones MOTU Origins**

![Oráculo Dashboard](https://img.shields.io/badge/Version-2.1.0-gold?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Operating-green?style=for-the-badge)
![Tech](https://img.shields.io/badge/Stack-React_19_|_FastAPI_|_Docker-blue?style=for-the-badge)

---

## 📖 Resumen Ejecutivo

**El Oráculo de Nueva Eternia** es una plataforma integral diseñada para coleccionistas de alto nivel (específicamente de la línea *Masters of the Universe: Origins*). Su propósito es doble:

1. **Vigilancia de Mercado**: Escanea automáticamente 15 tiendas en Europa y plataformas P2P (Wallapop, Vinted, eBay) para encontrar las mejores ofertas y calcular puntuaciones de oportunidad financiera (DealScorer).
2. **Gestión Patrimonial**: Permite llevar un control exhaustivo de la colección personal, calculando el valor real de mercado frente a la inversión realizada (Landed Price & ROI).

> [!IMPORTANT]
> **Toda la documentación profunda, flujos de datos, variables de entorno y arquitectura ha sido consolidada en un único documento maestro.**
> 👉 **[VER LA DOCUMENTACIÓN MAESTRA DE NUEVA ETERNIA](DOCUMENTACION_MAESTRA.md)** 👈

---

## 🏛️ Índices de Documentación Adicional

Si buscas detalles específicos, puedes consultar los siguientes archivos históricos y técnicos:

- **[La Documentación Maestra (El Santo Grial)](DOCUMENTACION_MAESTRA.md)**: El punto de entrada obligatorio para entender CÓMO funciona la aplicación (React, FastAPI, Supabase, Playwright, Variables de Entorno, etc.).
- **[PROJECT_CODEX.md](narrative/PROJECT_CODEX.md)**: Manifiesto técnico sobre la sinergia de los sistemas, política Zero-Leak y principios de diseño 3OX.
- **[SISTEMA_DE_INCURSION_TECNICO.md](technical/SISTEMA_DE_INCURSION_TECNICO.md)**: Documento legacy sobre el funcionamiento específico del orquestador y los Scrapers.
- **[MASTER_ROADMAP.md](MASTER_ROADMAP.md)**: El histórico de desarrollo y registro de todas las fases completadas (Fase 0 a Fase 62+).
- **[architecture_map.md](technical/architecture_map.md)**: Mapa físico exacto de todas las carpetas, routers y responsabilidades del código fuente.

---

## 🚀 Despliegue Rápido (Modo Arca)

Para levantar todo el sistema (Backend + Frontend + DB) usando contenedores:

```powershell
.\launch_ark.ps1
```

*(Consulta la **[Documentación Maestra](DOCUMENTACION_MAESTRA.md)** para la configuración de las variables `.env` requeridas).*

---
> **Nota del Oráculo**: "Lo que no es seguro, al Purgatorio. Lo que es verdad, a la Fortaleza."

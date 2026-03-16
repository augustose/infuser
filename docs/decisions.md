# Decision Log (ADR)

Este documento registra todas las decisiones arquitectónicas e implementaciones clave del proyecto Infuser.

## Decisiones Tomadas

| ID | Fecha | Decisión | Contexto / Justificación | Estado |
|---|---|---|---|---|
| ADR-001 | 2026-03-16 | **No hacer fork de Goliac; construir motor nativo en Python** | Goliac está profundamente acoplado a la API de GitHub y conceptos exclusivos de dicha plataforma. Hacer un refactor requeriría remover gran parte de su núcleo. Es más rápido y mantenible construir un motor desde cero usando Python interactuando directamente con la API REST de Gitea. | Aprobada |
| ADR-002 | 2026-03-16 | **Uso de `uv` como gestor de dependencias** | El usuario ha indicado que se utilizará `uv` (de Astral) para la gestión del entorno y las dependencias de Python, garantizando una mayor velocidad de ejecución e instalación. | Aprobada |
| ADR-003 | 2026-03-16 | **Gestor de estado y memoria local** | Para llevar un control sobre lo que ya se ha procesado (y lo que requerirá enviar notificaciones u otros cambios de estado), se agregará una "memoria local". Se ha decidido utilizar un archivo JSON o una base de datos embebida ligera como SQLite para rastrear el estado previo de los directorios YAML contra la API de Gitea. | Aprobada |
| ADR-004 | 2026-03-16 | **Generación de Reportes Visuales (Markdown/CSV)** | Para suplir las carencias visuales de Gitea en cuanto a auditorías centralizadas, se crearon scripts separados (`generate_report.py`, `generate_matrix_report.py`) que traducen el Estado Deseado (YAML) en reportes de lectura amigable para usuarios de negocio, sin sobrecargar la UI web core. | Aprobada |
| ADR-005 | 2026-03-16 | **Exportación de Shadow IT & Protecciones** | El motor de exportación debe ir más allá de los "Equipos" estándar. Se decidió intencionalmente mapear Branch Protections, Repositorios del espacio Personal (User Workspace) y Collaborators Directos para neutralizar riesgos de Shadow IT o bypass del modelo organizativo jerárquico. | Aprobada |

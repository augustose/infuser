# Decision Log (ADR)

Este documento registra todas las decisiones arquitectónicas e implementaciones clave del proyecto GiteAdmin.

## Decisiones Tomadas

| ID | Fecha | Decisión | Contexto / Justificación | Estado |
|---|---|---|---|---|
| ADR-001 | 2026-03-16 | **No hacer fork de Goliac; construir motor nativo en Python** | Goliac está profundamente acoplado a la API de GitHub y conceptos exclusivos de dicha plataforma. Hacer un refactor requeriría remover gran parte de su núcleo. Es más rápido y mantenible construir un motor desde cero usando Python interactuando directamente con la API REST de Gitea. | Aprobada |
| ADR-002 | 2026-03-16 | **Uso de `uv` como gestor de dependencias** | El usuario ha indicado que se utilizará `uv` (de Astral) para la gestión del entorno y las dependencias de Python, garantizando una mayor velocidad de ejecución e instalación. | Aprobada |
| ADR-003 | 2026-03-16 | **Gestor de estado y memoria local** | Para llevar un control sobre lo que ya se ha procesado (y lo que requerirá enviar notificaciones u otros cambios de estado), se agregará una "memoria local". Se ha decidido utilizar un archivo JSON o una base de datos embebida ligera como SQLite para rastrear el estado previo de los directorios YAML contra la API de Gitea. | Aprobada |

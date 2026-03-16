# User Journeys & User Stories

Este documento guía el desarrollo desde la perspectiva del flujo del usuario y las funcionalidades requeridas en GiteAdmin.

## User Journeys

### 1. El Desarrollador solicita un nuevo repositorio
El **Desarrollador** necesita un nuevo repositorio para su equipo.
1. Clona el repositorio `giteadmin-config`.
2. Crea una nueva rama (ej. `feat/nuevo-repo-frontend`).
3. Crea un archivo YAML (ej. `teams/frontend/nuevo-repo.yaml`) definiendo las características del repositorio.
4. Hace push y abre un Pull Request (PR).
5. El **Team Owner** o **Admin** revisa el PR.
6. Una vez aprobado y fusionado a la rama principal (main), **GiteAdmin** detecta el cambio, lee el YAML, y automáticamente crea el repositorio en Gitea usando los permisos solicitados.

### 2. El Administrador audita los accesos
El **Administrador** (o auditor de seguridad) necesita saber quién tiene acceso a qué.
1. Accede al repositorio `giteadmin-config`.
2. Lee los archivos YAML en las carpetas `teams/` y `users/`, consiguiendo inmediatamente la fuente única de verdad (Single Source of Truth) sobre todos los privilegios otorgados.

## User Stories

* **US-01:** Como **Desarrollador**, quiero definir mi nuevo repositorio usando un archivo YAML para no depender de la creación manual mediante tickets de IT.
* **US-02:** Como **Dueño de Equipo**, quiero aprobar PRs de configuración en `giteadmin-config` para tener un control transparente de lo que mi equipo está creando.
* **US-03:** Como **Sistema Automatizado**, quiero comparar el estado esperado (archivos YAML) contra el estado real (Gitea API), utilizando una **memoria local**, para determinar qué cambios (creaciones, modificaciones, archivados) deben aplicarse y notificar las discrepancias.
* **US-04:** Como **Software de Auditoría**, quiero notificar cuando un cambio es detectado y reconciliado para que haya visibilidad en canales (ej. Teams, Slack o email).

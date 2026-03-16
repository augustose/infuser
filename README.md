# Infuser

> **Inspirado en [Goliac](https://github.com/goliac-project/goliac)**: Infuser toma inspiración directa de los principios arquitectónicos y filosóficos de Goliac para ofrecer una solución nativa y liviana para la administración de servidores Gitea.

Infuser es un motor de **Infraestructura como Código (IaC)** diseñado específicamente para gestionar servidores Gitea y Forgejo (`gitea.alithya.com`).

En lugar de crear usuarios, equipos y repositorios manualmente a través de la interfaz web, Infuser permite gestionar la plataforma definiendo el estado deseado en archivos YAML alojados en un repositorio Git central (`infuser-config`).

## Características Principales

1. **Gestión Declarativa (IaC)**
   Define usuarios, organizaciones, equipos, miembros y repositorios usando archivos `.yaml` simples y legibles.

2. **Autoservicio y Auditoría Transparente**
   Cualquier desarrollador puede solicitar la creación de un repositorio o acceso a un equipo creando un *Pull Request* (PR) en el repositorio de configuración. Todos los cambios quedan registrados por control de versiones, creando un log de auditoría inmutable sobre "quién tiene acceso a qué". Las aprobaciones se gestionan naturalmente con revisiones de código.

3. **Automatización del Motor**
   El corazón de este proyecto es el motor Reconciliador, escrito en Python moderno utilizando `uv`. Compara periódicamente la configuración YAML contra el servidor Gitea y ejecuta los cambios necesarios (crear, modificar o archivar).

4. **Memoria Local y Notificaciones**
   Posee un sistema de estado local que permite notificar ágilmente a los equipos cuando sus solicitudes han sido aplicadas en el servidor, sin necesidad de consultar el 100% de la API constantemente.

5. **Auditoría Visual Anti Shadow IT 🛡️**
   Incluye generadores de reportes integrados (`status_report.md` interactivo y matrices CSV/Markdown) que documentan gráficamente qué equipos, usuarios directos y colaboradores externos tienen acceso a proyectos de organización y repositorios personales, visualizando también Protecciones de Ramas sin necesidad de navegar manual en Gitea.

## Comenzando (Quick Start)

### Requisitos Previos
- Python >= 3.12 (Recomendado)
- `uv` (Package Manager ultrarrápido)

### Instalación

1. Clona este proyecto.
2. Sincroniza las dependencias con `uv`:
   ```bash
   uv sync
   ```
3. Copia el archivo de entorno de ejemplo:
   ```bash
   cp .env.example .env
   ```
4. Edita el archivo `.env` e inserta tu `GITEA_TOKEN` personal de administración y ajusta la `GITEA_URL`.

## Documentación del Proyecto

Toda la documentación técnica y de arquitectura reside en la carpeta `docs/`. Recomendamos revisar los siguientes documentos fundamentales:

- [Manual de Operaciones](docs/manual_operaciones.md)
- [Arquitectura (Engine Specs)](docs/architecture.md)
- [User Journeys y Stories](docs/user_journeys_stories.md)
- [Registro de Decisiones (ADRs)](docs/decisions.md)

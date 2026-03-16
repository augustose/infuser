# Manual de Operaciones - GiteAdmin

Este documento actúa como guía principal (Runbook) para la interacción de ingenieros, desarrolladores y administradores con GiteAdmin.

## 1. Operativas del Día a Día para Desarrolladores

### Solicitar un Nuevo Repositorio
Para crear un nuevo repositorio en un equipo en Gitea, deberás:
1. Clonar localmente el repositorio central (`giteadmin-config`).
2. Crear un archivo YAML bajo el path `teams/[nombre_equipo]/[nombre_repo].yaml`.
3. El archivo debe contener la especificación mínima de repositorio (ver sección Plantillas).
4. Hacer push y mandar un PR al equipo propietario (Reviewers obligatorios asignados al equipo).
5. Una vez aprobado, el sistema de CI (u operación manual del Reconciliador) detectará y creará el repositorio en la organización adecuada en Gitea.

### Añadir o Remover Miembros
1. Localiza el archivo `team.yaml` dentro de la carpeta del equipo (ej. `teams/backend/team.yaml`).
2. Agrega o elimina el nombre del usuario de las claves `owners:` o `members:`.
3. Generar un PR, y al fusionarse a main, los permisos de Gitea se sincronizarán y se perderá/conseguirá el acceso instantáneamente.

## 2. Operativas para el Administrador del Motor

### Ejecutar el Reconciliador Manualmente
Para forzar o probar un sincronismo desde tu terminal (`uv` es necesario):

```bash
uv run scripts/core_diff_engine.py --dry-run
```
> **Nota**: El flag `--dry-run` es vital. Nunca ejecutes la sincronización manual sin ver primero el plan generado, o el motor puede borrar entidades no mapeadas.

### Monitoreo del Estado Local
El estado actual que ha reconocido el motor respecto al último "apply" exitoso se guarda localmente en `.giteadmin_state.db`. Si algo se corrompe por errores de red con la API de Gitea:
1. Ejecuta el comando de reconstrucción de estado:
   ```bash
   uv run scripts/rebuild_state.py
   ```
   Esto forzará a descargar todo el árbol de Gitea desde 0.

## 3. Resolución de Problemas (Troubleshooting)

### Error 40X en Gitea: Authentication Failed
*   **Síntoma**: Los scripts de Python (o el Runner) caen con HTTP 401/403.
*   **Razón**: El `GITEA_TOKEN` de Administrador presente en `.env` (o en GitHub Actions secrets) expiró o fue revocado.
*   **Arreglo**: Entra a Gitea, ve a Perfil > Applications y revoca el viejo. Genera uno nuevo y reemplázalo en las configuraciones correspondientes.

### Un YAML no está siendo detectado
*   **Síntoma**: El script de Python dice "Nothing to do", a pesar de haber integrado tu PR hace minutos.
*   **Arreglo**: Verifica la sintaxis del YAML usando herramientas online o un IDE plugin; el engine descarta YAMLs malformados. Revisa los logs de error del motor en la salida estándar.

# Manual de Operaciones - GiteAdmin

Este documento actúa como guía principal (Runbook) para la interacción de ingenieros, desarrolladores y administradores con GiteAdmin.

## 1. Operativas del Día a Día para Desarrolladores

### Solicitar un Nuevo Repositorio o Modificar Permisos
Toda alteración a la infraestructura de Gitea (crear repositorios, modificar equipos, invitar usuarios) se realiza mediante GitOps:
1. Clonar localmente este repositorio.
2. Navegar a la carpeta `giteadmin-config/` y crear o modificar el archivo YAML correspondiente (ej. `organizations/mi-org/repositories/app.yaml`).
3. Hacer push y mandar un Pull Request (PR).
4. Una vez aprobado y fusionado a `main`, el Reconciliador aplicará los cambios automáticamente.

## 2. Operativas para el Administrador del Motor

### Ejecutar el Reconciliador Manualmente
Para forzar o probar una sincronización desde tu terminal local (`uv` es necesario):

**1. Ver el Plan de Ejecución (Dry Run):**
```bash
uv run scripts/core_engine.py --dry-run
```
> **Nota:** Nunca ejecutes la sincronización manual sin ver primero el plan generado en modo "dry-run".

**2. Aplicar los Cambios (Apply):**
```bash
uv run scripts/core_engine.py --apply
```
Esto empujará permanentemente los cambios a través de la API de Gitea y actualizará la Memoria Local (`.giteadmin_state.json`).

### Exportar el Estado Actual de Gitea
Si la memoria local se corrompe o necesitas una fotografía fresca desde cero directo del servidor, corre:
```bash
uv run scripts/export_state.py
```
Esto descargará todos los usuarios, organizaciones, repositorios personales, protecciones de ramas y colaboradores directos en archivos YAML estructurados bajo la carpeta `giteadmin-config/`.

## 3. Auditoría y Seguridad (Generación de Reportes) 📊

GiteAdmin incluye potentes herramientas de generación de reportes visuales ideados para auditorías de seguridad y *compliance*.

**Reporte de Estado General y Visual (Markdown):**
```bash
uv run scripts/generate_report.py
```
Genera un documento interactivo (colapsable) detallando qué equipos y administradores acceden a qué proyecto, incluyendo espacios de trabajo personales de los usuarios. Queda en `output/reports/status_report.md`.

**Matriz de Accesos y Permisos (CSV/Markdown over time):**
```bash
uv run scripts/generate_matrix_report.py
```
Crea una "Access Matrix" cruzando Proyectos (filas) y Usuarios (columnas), extrayendo el permiso máximo agregado por cada usuario. Ideal para comparar la evolución de permisos a lo largo del tiempo. Queda en `output/reports/matrix/`.

## 4. Resolución de Problemas (Troubleshooting)

### Error HTTP 401/403 en la API de Gitea
*   **Síntoma**: Los scripts caen o muestran errores de autenticación.
*   **Razón**: El `GITEA_TOKEN` de Administrador presente en `.env` expiró o fue revocado.
*   **Arreglo**: Entra a Gitea, ve a Perfil > Applications y genera un nuevo token con permisos en todo el stack. Reemplázalo en el archivo local `.env`.

### Un YAML no está siendo detectado por el Reconciliador
*   **Arreglo**: Verifica la sintaxis del YAML. El motor `parser.py` está diseñado para fallar silenciosa pero positivamente si un archivo no tiene el formato esperado (`apiVersion` y `kind` requeridos).

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

**1. Ver el Plan de Ejecución:**
```bash
uv run scripts/core_engine.py
```
> **Nota:** Por seguridad, el modo Plan (Dry-Run) es el default. El motor analizará todos los YAML y los cruzará contra su memoria, y te dirá qué entidades considera que tiene que crear, modificar o borrar, sin tocar nada en producción.

**2. Aplicar los Cambios (Modo Interactivo):**
```bash
uv run scripts/core_engine.py --apply
```
Al correr este comando, verás la lista propuesta y el sistema pausará solicitándote confirmación obligatoria (`yes/no`). Si aceptas, persistirá las transacciones sobre Gitea.

**3. Aplicar Cambios sin Intervención (CI/CD):**
```bash
uv run scripts/core_engine.py --apply --auto-approve
```
Este flag bypassa el prompt interactivo y ejecuta las transacciones de inmediato. Recomendado primordialmente para GitHub Actions / Gitea Actions instanciadas por PR Merges.

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
Genera un documento interactivo (colapsable) detallando qué equipos y administradores acceden a qué proyecto. Queda en `output/reports/status_report.md`.

**Reporte Centrado en el Usuario (Offboarding / Access Checks):**
```bash
uv run scripts/generate_user_report.py
```
Genera un documento vital para revisiones de acceso. Por cada usuario, enumera colapsablemente las Organizaciones, Equipos, Repositorios (directos e indirectos) y Espacios Personales que controla. Útil para verificar que, si alguien es desvinculado de la empresa, ya no conste su acceso en ninguna arista de Gitea de forma independiente o residual. Queda en `output/reports/user_access_report.md`.

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

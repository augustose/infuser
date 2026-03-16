# Arquitectura: GiteAdmin Engine

Este documento define la especificación de la arquitectura técnica del motor GiteAdmin.

## 1. Visión General
GiteAdmin es un motor de Infraestructura como Código (IaC) diseñado para interactuar bidireccionalmente entre un repositorio Git central de configuración (`giteadmin-config`) y la instancia objetivo de Gitea (`gitea.alithya.com`).

Se basa en el principio de que los archivos YAML alojados en el repositorio conforman el **Estado Deseado**, y Gitea tiene el **Estado Actual**. 

## 2. Componentes Principales

1. **Gestor de Estado / YAML Parser (Lector)**
   - Se encarga de recorrer la carpeta `giteadmin-config` y transformar todos los archivos YAML (`users/`, `teams/`, `repos/`) en estructuras de datos de Python.

2. **Gitea API Client (Ejecutor)**
   - Un cliente HTTP ligero estructurado en múltiples scripts/clases.
   - Interactúa a través de `requests` con Gitea (`/api/v1/`) usando tokens de autenticación de administrador.

3. **Reconciliador (Differ Engine)**
   - El corazón de la aplicación.
   - Compara el **Estado Deseado** (Memoria local + Configuración YAML) contra el **Estado Actual** de la API.
   - Genera un Plan de Acción (Crear Equipo, Eliminar Acceso, Archivar Repo).

4. **Memoria Local (State / Cache)**
   - Archivo JSON local (`.giteadmin_state.json`) o base de datos ligera SQLite (`state.db`).
   - Propósito: Guardar la firma y estado físico del último "apply" exitoso.
   - Se usará en un futuro inminente para dirigir **Notificaciones** al detectar cuándo un usuario/repo fue específicamente mutado, sin necesidad de consultar el 100% de la API de Gitea en cada corrida.

5. **Módulo de Notificaciones**
   - Una capa reactiva que despacha eventos cuando el Reconciliador detecta o ejecuta cambios (Ej. "Repositorio Creado").

## 3. Flujo de Reconciliación

1. **Trigger Base**: Se ejecuta vía cron, CLI de forma manual o se empaqueta como servicio (Webhook trigger desde GitHub/Gitea Actions).
2. **Read Config**: Parsea YAMLs.
3. **Read Memory**: Parsea `state.db`.
4. **Diffing**: Calcula qué comandos le tiene que enviar a Gitea.
5. **Apply API**: Llama los endpoints (`POST /orgs`, `POST /repos`, etc).
6. **Update Memory & Notify**: Actualiza la memoria local e invoca el módulo que lanza avisos.

## 4. Stack Tecnológico
- **Lenguaje:** Python
- **Package Manager:** `uv`
- **Librerías Core:** `requests`, `pyyaml`
- **Memoria:** JSON file / SQLite embed.

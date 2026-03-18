# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Infuser** is a Python-based IaC (Infrastructure as Code) reconciliation engine for Gitea/Forgejo servers, inspired by Goliac. It manages users, organizations, teams, and repositories declaratively via YAML files.

## Commands

```bash
# Install dependencies
uv sync

# Interactive launcher (recommended — shows all scripts with descriptions)
uv run main.py

# Dry-run reconciliation (default safe mode, shows execution plan)
uv run scripts/core_engine.py

# Apply changes (interactive confirmation)
uv run scripts/core_engine.py --apply

# Apply without confirmation (CI/CD)
uv run scripts/core_engine.py --apply --auto-approve

# Export current Gitea state to YAML
uv run scripts/export_state.py

# Generate reports
uv run scripts/generate_report.py
uv run scripts/generate_user_report.py
uv run scripts/generate_matrix_report.py
uv run scripts/generate_repo_grid.py
```

No test framework or linter is currently configured.

## Architecture

### Reconciliation Flow

1. **Parse** — `scripts/parser.py` reads YAML from `infuser-config/` (users/, organizations/) into a desired state dict
2. **Memory** — `scripts/memory.py` loads `.infuser_state.json` (the last-known state from previous reconciliation)
3. **Diff** — `scripts/core_engine.py` computes set differences between desired and previous state to build an action plan (create/delete/update for users, orgs, teams, members, repos)
4. **Execute** — `scripts/api_actions.py` calls the Gitea API to apply the plan (only when `--apply` flag and `GITEA_ALLOW_WRITES=true`)
5. **Save** — Updated desired state is persisted to `.infuser_state.json`

### Key Modules

| Module | Role |
|--------|------|
| `scripts/core_engine.py` | Main entry point — orchestrates parse → diff → execute |
| `scripts/parser.py` | YAML parser for `infuser-config/` directory tree |
| `scripts/api_actions.py` | Gitea REST API client (CRUD for users, orgs, teams, repos) |
| `scripts/memory.py` | Local JSON state management (`.infuser_state.json`) |
| `scripts/config.py` | Loads `.env` configuration (URL, tokens, write permission) |
| `scripts/export_state.py` | Exports live Gitea state back to YAML files |

### Safety Model

- Dry-run is the default — no mutations without `--apply`
- Write operations require `GITEA_ALLOW_WRITES=true` in `.env`
- Interactive confirmation prompt before applying (bypass with `--auto-approve`)

## Configuration

Environment variables are loaded from `.env` (see `.env.example`):
- `GITEA_URL` — Gitea server URL
- `GITEA_READ_TOKEN` / `GITEA_WRITE_TOKEN` — API tokens with appropriate scopes
- `GITEA_ALLOW_WRITES` — Must be `"true"` to enable any mutations

## YAML Config Structure

The `infuser-config/` directory (gitignored, populated by export or manually) contains:
- `users/` — User definitions with personal repositories
- `organizations/` — Org definitions containing teams and repositories

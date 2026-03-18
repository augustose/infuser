# Operations Manual - Infuser

This document acts as the main guide (Runbook) for interaction by engineers, developers, and administrators with Infuser.

## 1. Day-to-Day Operations for Developers

### Requesting a New Repository or Modifying Permissions
Any alteration to the Gitea infrastructure (creating repositories, modifying teams, inviting users) is done via GitOps:
1. Clone this repository locally.
2. Navigate to the `infuser-config/` folder and create or modify the corresponding YAML file (e.g., `organizations/my-org/repositories/app.yaml`).
3. Commit, push and send a Pull Request (PR).
4. Once approved and merged into `main`, the Reconciler will apply the changes automatically.

## 2. Operations for the Engine Administrator

### Interactive Launcher
Instead of remembering individual script commands, you can use the interactive launcher:
```bash
uv run main.py
```
It presents a numbered menu with all available scripts and a short description of each one. Select an option by number to run it. This is the recommended way to interact with Infuser from the terminal.

### Running the Reconciler Manually
To force or test a synchronization from your local terminal (`uv` is required):

**1. View the Execution Plan:**
```bash
uv run scripts/core_engine.py
```
> **Note:** For security, Plan mode (Dry-Run) is the default. The engine will analyze all YAMLs and cross-check them against its memory, telling you which entities it considers needing creation, modification, or deletion, without touching production.

**2. Apply Changes (Interactive Mode):**
```bash
uv run scripts/core_engine.py --apply
```
By running this command, you will see the proposed list and the system will pause, requesting mandatory confirmation (`yes/no`). If you accept, it will persist the transactions on Gitea.

**3. Apply Changes without Intervention (CI/CD):**
```bash
uv run scripts/core_engine.py --apply --auto-approve
```
This flag bypasses the interactive prompt and executes transactions immediately. Primarily recommended for GitHub Actions / Gitea Actions instantiated by PR Merges.

### Exporting the Current Gitea State
If local memory becomes corrupted or you need a fresh snapshot from scratch directly from the server, run:
```bash
uv run scripts/export_state.py
```
This will download all users, organizations, personal repositories, branch protections, and direct collaborators into structured YAML files under the `infuser-config/` folder.

## 3. Auditing and Security (Report Generation) 📊

Infuser includes powerful visual reporting tools designed for security audits and compliance.

**General Visual Status Report (Markdown):**
```bash
uv run scripts/generate_report.py
```
Generates an interactive (collapsible) document detailing which teams and administrators access which projects. Saved in `output/reports/status_report.md`.

**User-Centric Report (Offboarding / Access Checks):**
```bash
uv run scripts/generate_user_report.py
```
Generates a vital document for access reviews. For each user, it collapsibly lists the Organizations, Teams, Repositories (direct and indirect), and Personal Spaces they control. Useful for verifying that, if someone is terminated from the company, their access is no longer present independently or residually in any Gitea configuration. Saved in `output/reports/user_access_report.md`.

**Access and Permissions Matrix (CSV/Markdown over time):**
```bash
uv run scripts/generate_matrix_report.py
```
Creates an "Access Matrix" crossing Projects (rows) and Users (columns), extracting the maximum aggregated permission for each user. Ideal for comparing the evolution of permissions over time. Saved in `output/reports/matrix/`.

## 4. Scripts Reference

| Script | Purpose | Command |
|--------|---------|---------|
| `main.py` | Interactive launcher — presents a menu with all scripts and their descriptions | `uv run main.py` |
| `scripts/core_engine.py` | Reconciliation engine — compares desired state (YAML) against local memory and applies changes to Gitea | `uv run scripts/core_engine.py [--apply] [--auto-approve]` |
| `scripts/export_state.py` | Exports the current live Gitea state (users, orgs, repos, protections) into YAML files under `infuser-config/` | `uv run scripts/export_state.py` |
| `scripts/generate_report.py` | General visual status report with collapsible sections per org/repo showing teams, permissions and branch protections | `uv run scripts/generate_report.py` |
| `scripts/generate_user_report.py` | User-centric access report — lists every org, team and repo each user can reach (useful for offboarding audits) | `uv run scripts/generate_user_report.py` |
| `scripts/generate_matrix_report.py` | Access matrix crossing repos (rows) vs users (columns) with highest aggregated permission level (CSV + Markdown) | `uv run scripts/generate_matrix_report.py` |
| `scripts/generate_repo_grid.py` | Repository grid — flat table with repository, description, organization, owner and list of users with access (CSV + Markdown) | `uv run scripts/generate_repo_grid.py` |

All reports are saved under `output/reports/`.

## 5. Troubleshooting

### HTTP Error 401/403 in the Gitea API
*   **Symptom**: Scripts crash or throw authentication errors.
*   **Reason**: The Administrator's `GITEA_READ_TOKEN` or `GITEA_WRITE_TOKEN` in `.env` expired or was revoked.
*   **Fix**: Enter Gitea, go to Profile > Applications and generate a new token with stack-wide permissions. Replace it in the local `.env` file.

### A YAML is not being detected by the Reconciler
*   **Fix**: Check the YAML syntax. The `parser.py` engine is designed to fail silently but positively if a file does not have the expected format (`apiVersion` and `kind` are required).

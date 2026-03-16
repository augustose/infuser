# User Journeys & User Stories

This document guides development from the perspective of user flow and the functionalities required in Infuser.

## User Journeys

### 1. Developer requests a new repository
The **Developer** needs a new repository for their team.
1. Clones the `infuser-config` repository.
2. Creates a new branch (e.g., `feat/new-repo-frontend`).
3. Creates a YAML file (e.g., `teams/frontend/new-repo.yaml`) defining the repository's characteristics.
4. Pushes the branch and opens a Pull Request (PR).
5. The **Team Owner** or **Admin** reviews the PR.
6. Once approved and merged into the main branch (`main`), **Infuser** detects the change, reads the YAML, and automatically creates the repository in Gitea using the requested permissions.

### 2. Administrator audits access
The **Administrator** (or security auditor) needs to know who has access to what.
1. Accesses the `infuser-config` repository.
2. Reads the YAML files in the `teams/` and `users/` folders, instantly obtaining the Single Source of Truth regarding all granted privileges.

## User Stories

* **US-01:** As a **Developer**, I want to define my new repository using a YAML file so I don't rely on manual IT ticket creation.
* **US-02:** As a **Team Owner**, I want to approve configuration PRs in `infuser-config` to have transparent control over what my team is creating.
* **US-03:** As an **Automated System**, I want to compare the expected state (YAML files) against the actual state (Gitea API), using a **local memory**, to determine what changes (creations, modifications, archiving) must be applied and notify discrepancies.
* **US-04:** As an **Auditing Software**, I want to notify when a change is detected and reconciled so that there is visibility in channels (e.g., Teams, Slack, or email).

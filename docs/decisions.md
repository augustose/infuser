# Decision Log (ADR)

This document records all architectural decisions and key implementations of the Infuser project.

## Decisions Made

| ID | Date | Decision | Context / Justification | Status |
|---|---|---|---|---|
| ADR-001 | 2026-03-16 | **Do not fork Goliac; build native Python engine** | Goliac is deeply coupled with the GitHub API and platform-exclusive concepts. Refactoring would require gutting most of its core. It is faster and more maintainable to build an engine from scratch using Python, interacting directly with the Gitea REST API. | Approved |
| ADR-002 | 2026-03-16 | **Use `uv` as the dependency manager** | The user indicated the use of `uv` (by Astral) for Python environment and dependency management, ensuring greater execution and installation speed. | Approved |
| ADR-003 | 2026-03-16 | **State manager and local memory** | To keep track of what has already been processed (and what will require sending notifications or other state changes), a "local memory" will be added. It was decided to use a JSON file or a lightweight embedded database like SQLite to track the previous state of the YAML directories against the Gitea API. | Approved |
| ADR-004 | 2026-03-16 | **Visual Report Generation (Markdown/CSV)** | To compensate for Gitea's lack of centralized auditing visuals, separate scripts (`generate_report.py`, `generate_matrix_report.py`) were created to translate the Desired State (YAML) into business-friendly read-only reports, without overloading the core web UI. | Approved |
| ADR-005 | 2026-03-16 | **Exporting Shadow IT & Protections** | The export engine must go beyond standard "Teams". It was intentionally decided to map Branch Protections, Personal Workspace Repositories, and Direct Collaborators to neutralize Shadow IT risks or bypasses of the hierarchical organizational model. | Approved |

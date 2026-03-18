# Infuser (Inspired by Goliac)

## Objective
To create an **Infrastructure as Code (IaC)** tool for managing Gitea and Forgejo servers. 

Inspired by the [Goliac](https://github.com/goliac-project/goliac) project, this system will shift organization management (users, teams, permissions, and repositories) from manual UI configurations to declarative YAML manifests stored in a central Git repository. This provides full visibility into projects, users, organizations, and activity out of the box.

## Core Concepts & Capabilities

1. **Declarative Management (IaC)**
   - Define organizations, teams, members, and repositories using simple YAML files.
   - Example: A single YAML file defines a team's owners/members and configures the repositories they have access to.

2. **Self-Service & Transparent Auditing**
   - Regular users can request new teams, new repositories, or access changes by opening a Pull Request against the central configuration repository.
   - All changes are version-controlled, providing a transparent and immutable audit log of "who has access to what" at any given time.
   - Approvals are handled naturally via PR reviews by team owners or administrators.

3. **Automation & Enforcement**
   - The Infuser engine runs in the background or via CI/CD.
   - When a PR is merged, the tool automatically reconciles the changes using the Gitea/Forgejo REST API (e.g., creating the repository, setting permissions, or archiving old projects).

## Proposed Configuration Structure

```text
infuser-config/
├── users/
│   ├── alice.yaml
│   └── bob.yaml
├── teams/
│   ├── frontend/
│   │   ├── team.yaml             # Defines owners and members of the frontend team
│   │   └── awesome-website.yaml  # Defines a Gitea repository owned by the frontend team
│   └── backend/
│       ├── team.yaml
│       └── main-api.yaml
└── archived/                     # Moving a repository YAML here archives it on Gitea
    └── old-project.yaml
```

## Implementation Path: Forking Goliac vs. Custom Build

We have two main paths to realize this vision for Gitea/Forgejo:

### Option A: Fork and Adapt Goliac
- **Pros:** Goliac (written in Go) already has parsing logic, reconciliation engines, and a web UI built out.
- **Cons:** Goliac is deeply integrated with GitHub concepts (e.g., GitHub Apps, specific GitHub REST/GraphQL APIs). Ripping out the GitHub API layer and replacing it with Gitea's API could be a massive refactoring effort.

### Option B: Build a Native Gitea/Forgejo IaC Engine
- **Pros:** We can tailor it perfectly to Gitea/Forgejo's specific API capabilities without carrying GitHub legacy code. We could build a lightweight, highly maintainable engine in Go or Python.
- **Cons:** Requires building the parser, differ, and API executor from scratch.

*(For now, we can structure this project to act as the engine that reads these YAMLs and applies them using Gitea/Forgejo API)*

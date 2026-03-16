# Gitea Administration & Analytics Tools (GiteAdmin)

## Objective
To create a structured system (scripts, tools, and documentation) to comprehensively manage, audit, and understand the state of the Gitea server (`gitea.alithya.com`). This project aims to provide clear visibility into projects, users, organizations, access permissions, and overall activity.

## Core Features & Requirements

1. **Inventory & Discovery**
   - Retrieve all projects (repositories) hosted on the server.
   - List all registered users and their profile details.
   - Enumerate all organizations and their associated teams/members.

2. **Access & Permissions Auditing**
   - Determine exactly "who has access to what" across all repositories and organizations.
   - Map user permissions (Read, Write, Admin) for enhanced security and compliance.

3. **Activity Monitoring**
   - Track and report on user and repository activity.
   - Monitor recent commits, pull requests, issues, and overall server usage.

## Proposed File Structure

```text
giteadmin/
├── README.md               # Project overview, setup, and usage instructions
├── .env                    # Environment variables (Gitea API URL, Tokens)
├── scripts/                # Core logic and API integration
│   ├── 01_get_projects.py  # Fetch and list all repositories
│   ├── 02_get_users.py     # Fetch and list all users
│   ├── 03_get_orgs.py      # Fetch organizations and teams
│   ├── 04_audit_access.py  # Map users to their access levels
│   └── 05_get_activity.py  # Fetch recent platform activities
├── docs/                   # Internal documentation
│   └── gitea_api_notes.md  # Reference for Gitea API endpoints used
└── output/                 # Generated reports (gitignored by default)
    ├── inventory/          # JSON/CSV exports of users, orgs, and projects
    └── reports/            # Access audits and activity summaries
```

## Technical Approach
The system will leverage the **Gitea REST API** to extract data securely. Scripts (preferably written in **Python** for strong data manipulation capabilities) will authenticate via API tokens, paginate through endpoints, and generate easily digestible reports (CSV, JSON, or Markdown).

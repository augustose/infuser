import os
import csv
from parser import parse_all_config
from datetime import datetime

REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "reports", "grid")

def generate_repo_grid():
    os.makedirs(REPORT_DIR, exist_ok=True)
    state = parse_all_config()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    global_admins = [u for u, d in state.get("users", {}).items() if d.get("spec", {}).get("is_admin")]

    rows = []

    # Organization repositories
    for org_name, org_data in state.get("organizations", {}).items():
        teams = org_data.get("teams", {})
        repos = org_data.get("repositories", {})

        for repo_name, r_data in repos.items():
            r_spec = r_data.get("spec", {})
            description = r_spec.get("description", "")

            # Collect users with access
            users_with_access = set()

            # Via teams
            for t_name, t_data in teams.items():
                t_spec = t_data.get("spec", {})
                if t_spec.get("includes_all_repositories", False):
                    for m in t_spec.get("members", []):
                        users_with_access.add(m)

            # Via direct collaborators
            for collab in r_spec.get("collaborators", {}).keys():
                users_with_access.add(collab)

            # Global admins always have access
            for admin in global_admins:
                users_with_access.add(admin)

            rows.append({
                "repository": repo_name,
                "description": description,
                "organization": org_name,
                "owner": org_name,
                "users": sorted(users_with_access),
            })

    # Personal repositories
    for u_name, u_data in state.get("users", {}).items():
        for repo_name, r_data in u_data.get("repositories", {}).items():
            r_spec = r_data.get("spec", {})
            description = r_spec.get("description", "")

            users_with_access = {u_name}

            for collab in r_spec.get("collaborators", {}).keys():
                users_with_access.add(collab)

            for admin in global_admins:
                users_with_access.add(admin)

            rows.append({
                "repository": repo_name,
                "description": description,
                "organization": "-",
                "owner": u_name,
                "users": sorted(users_with_access),
            })

    rows.sort(key=lambda r: (r["organization"], r["repository"]))

    # CSV
    csv_filename = os.path.join(REPORT_DIR, f"repo_grid_{timestamp}.csv")
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Repository", "Description", "Organization", "Owner", "Users with Access"])
        for row in rows:
            writer.writerow([row["repository"], row["description"], row["organization"], row["owner"], ", ".join(row["users"])])

    # Markdown
    md_filename = os.path.join(REPORT_DIR, f"repo_grid_{timestamp}.md")
    with open(md_filename, "w", encoding="utf-8") as f:
        f.write(f"# Repository Access Grid\n\n")
        f.write(f"> **Generated on:** `{timestamp}`\n\n")

        f.write("| Repository | Description | Organization | Owner | Users with Access |\n")
        f.write("|---|---|---|---|---|\n")

        for row in rows:
            users_str = ", ".join(row["users"]) if row["users"] else "-"
            desc = row["description"].replace("|", "\\|")
            f.write(f"| {row['repository']} | {desc} | {row['organization']} | {row['owner']} | {users_str} |\n")

    print(f"✅ Repository grid report generated:")
    print(f"   📄 CSV: {csv_filename}")
    print(f"   📊 MD:  {md_filename}")


if __name__ == "__main__":
    generate_repo_grid()

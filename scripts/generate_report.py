import os
from parser import parse_all_config
from datetime import datetime

REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "reports")
REPORT_FILE = os.path.join(REPORT_DIR, "status_report.md")

def generate_markdown_report():
    os.makedirs(REPORT_DIR, exist_ok=True)
    state = parse_all_config()
    
    num_users = len(state.get("users", {}))
    num_orgs = len(state.get("organizations", {}))
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        # Header
        f.write("# 🛡️ GiteAdmin Security & Access Report\n\n")
        f.write(f"> **Generated on:** `{datetime.now().strftime('%B %d, %Y - %H:%M')}` | **Users:** `{num_users}` | **Organizations:** `{num_orgs}`\n\n")
        f.write("---\n\n")
        
        # Organizations
        for org_name, org_data in state.get("organizations", {}).items():
            f.write(f"## 🏢 Organization: **{org_name}**\n\n")
            
            teams = org_data.get("teams", {})
            repos = org_data.get("repositories", {})
            
            # Sub-header: Projects (Repositories)
            f.write("### 🗂️ Projects (Repositories)\n")
            f.write("<br>\n\n")
            
            if not repos:
                f.write("*No projects found in this organization.*\n\n")
                continue
                
            for repo_name, repo_details in repos.items():
                spec = repo_details.get("spec", {})
                is_private = "🔒 Private" if spec.get("private") else "🌍 Public"
                desc = spec.get("description", "")
                desc_text = f" - *{desc}*" if desc else ""
                
                # Identify which teams have access to this specific repository
                repo_teams = []
                for t_name, t_data in teams.items():
                    t_spec = t_data.get("spec", {})
                    # A team has access if it includes all repos
                    # (In a full implementation, we would also check if the team explicitly lists this repo)
                    if t_spec.get("includes_all_repositories", False):
                        repo_teams.append((t_name, t_spec))
                
                # Identify direct collaborators bypassing teams
                direct_collabs = spec.get("collaborators", {})
                
                # Start Collapsible Section for the Repository
                f.write(f"<details>\n")
                f.write(f"  <summary><b>📦 {repo_name}</b> <kbd>{is_private}</kbd>{desc_text}</summary>\n\n")
                
                f.write("  <blockquote>\n")
                f.write("  <b>👥 Who has access?</b><br>\n")
                
                f.write("  <ul>\n")
                if not repo_teams and not direct_collabs:
                    f.write("    <li><i>No specific teams assigned. Only Organization Admins.</i></li>\n")
                
                if repo_teams:
                    for t_name, t_spec in repo_teams:
                        perm = t_spec.get("permission", "custom")
                        if perm == "none" and t_spec.get("units_map"):
                            perm = "Custom Granular"
                        members = t_spec.get("members", [])
                        members_str = ", ".join(members) if members else "<i>No members</i>"
                        f.write(f"    <li><b>Team {t_name}</b> (<code>Access: {perm.upper()}</code>)<br>\n")
                        f.write(f"    <i>Members:</i> {members_str}</li>\n")
                        
                if direct_collabs:
                    for usr, lvl in direct_collabs.items():
                        f.write(f"    <li>👤 <b>Direct: <code>@{usr}</code></b> (<code>Access: {lvl.upper()}</code>)</li>\n")
                        
                f.write("  </ul>\n")
                
                # Identify branch protections
                protections = spec.get("branch_protections", [])
                if protections:
                    f.write("  <br><b>🛡️ Branch Protections:</b><br>\n")
                    f.write("  <ul>\n")
                    for bp in protections:
                        br_name = bp.get("branch_name")
                        req_apprv = bp.get("required_approvals", 0)
                        push_en = "Yes" if bp.get("enable_push") else "No"
                        f.write(f"    <li>🌿 <code>{br_name}</code> — <b>Push allowed:</b> {push_en} | <b>Required Approvals:</b> {req_apprv}</li>\n")
                    f.write("  </ul>\n")

                f.write("  </blockquote>\n")
                f.write("</details>\n\n")
            
            f.write("---\n")
            
        # Global Admins Section
        f.write("\n<details>\n")
        f.write("  <summary><b>🚨 Global System Administrators</b></summary>\n\n")
        f.write("  <blockquote>\n")
        f.write("  <i>These users have full unrestricted access to all organizations and projects:</i><br>\n")
        admins = [u_name for u_name, u_details in state.get("users", {}).items() if u_details.get("spec", {}).get("is_admin")]
        if admins:
            f.write("  <ul>\n")
            for admin in admins:
                f.write(f"    <li>🛡️ <b>{admin}</b></li>\n")
            f.write("  </ul>\n")
        else:
            f.write("  <i>No global administrators found.</i>\n")
        f.write("  </blockquote>\n")
        f.write("</details>\n\n")
            
        # Personal Workspaces Section
        f.write("\n## 🧑‍💻 Personal Workspaces\n\n")
        f.write("> *Personal repositories belonging to individual users instead of organizations.*<br><br>\n\n")
        
        users_with_repos = {u_name: u_data for u_name, u_data in state.get("users", {}).items() if u_data.get("repositories")}
        if not users_with_repos:
            f.write("*No personal repositories found in the system.*\n\n")
        else:
            for u_name, u_data in users_with_repos.items():
                repos = u_data.get("repositories", {})
                
                f.write(f"<details>\n")
                f.write(f"  <summary><b>👤 {u_name}</b> <i>({len(repos)} repositories)</i></summary>\n\n")
                f.write("  <blockquote>\n")
                f.write("  <ul>\n")
                
                for r_name, r_data in repos.items():
                    spec = r_data.get("spec", {})
                    is_private = "🔒 Private" if spec.get("private") else "🌍 Public"
                    desc = spec.get("description", "")
                    desc_text = f" - *{desc}*" if desc else ""
                    
                    collaborators = spec.get("collaborators", {})
                    collab_text = ""
                    if collaborators:
                        collab_items = [f"`@{usr}` ({lvl})" for usr, lvl in collaborators.items()]
                        collab_text = f"<br>&nbsp;&nbsp;&nbsp;&nbsp;↳ 🤝 **Shared with:** " + ", ".join(collab_items)
                    
                    protections = spec.get("branch_protections", [])
                    prot_text = ""
                    if protections:
                        prot_text = "<br>&nbsp;&nbsp;&nbsp;&nbsp;↳ 🛡️ **Branch Protections:**<br>"
                        for bp in protections:
                            br_name = bp.get("branch_name")
                            req_apprv = bp.get("required_approvals", 0)
                            push_en = "Yes" if bp.get("enable_push") else "No"
                            prot_text += f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🌿 <code>{br_name}</code> — <b>Push allowed:</b> {push_en} | <b>Required Approvals:</b> {req_apprv}<br>"

                    f.write(f"    <li><b>📦 {r_name}</b> <kbd>{is_private}</kbd>{desc_text}{collab_text}{prot_text}</li><br>\n")
                    
                f.write("  </ul>\n")
                f.write("  </blockquote>\n")
                f.write("</details>\n\n")
            
    print(f"\n✨ Beautiful Report Generated! 👉 {REPORT_FILE}")

if __name__ == "__main__":
    generate_markdown_report()

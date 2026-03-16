import os
import yaml
import requests
import urllib3
from config import GITEA_URL, HEADERS

# Disable SSL Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "infuser-config")

def get_paginated(url):
    """Auxiliar function to handle Gitea pagination."""
    results = []
    page = 1
    limit = 50
    while True:
        sep = "&" if "?" in url else "?"
        paged_url = f"{url}{sep}page={page}&limit={limit}"
        response = requests.get(paged_url, headers=HEADERS, verify=False)
        if response.status_code != 200:
            print(f"Error HTTP {response.status_code} on {paged_url}")
            break
        data = response.json()
        if not data:
            break
        results.extend(data)
        if len(data) < limit:
            break
        page += 1
    return results

def export_users():
    """Download all users and save as YAML."""
    print("Exporting users...")
    users_dir = os.path.join(EXPORT_DIR, "users")
    os.makedirs(users_dir, exist_ok=True)
    
    users = get_paginated(f"{GITEA_URL}/api/v1/admin/users")
    
    for u in users:
        username = u.get("login")
        user_dir = os.path.join(users_dir, username)
        os.makedirs(user_dir, exist_ok=True)
        
        user_data = {
            "apiVersion": "v1",
            "kind": "User",
            "metadata": {
                "name": username
            },
            "spec": {
                "email": u.get("email"),
                "full_name": u.get("full_name"),
                "is_admin": u.get("is_admin", False),
                "active": u.get("active", True)
            }
        }
        
        filepath = os.path.join(user_dir, "user.yaml")
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(user_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
        # 1.1 Export User's Personal Repositories
        repos_dir = os.path.join(user_dir, "repositories")
        os.makedirs(repos_dir, exist_ok=True)
        
        user_repos = get_paginated(f"{GITEA_URL}/api/v1/users/{username}/repos")
        for repo in user_repos:
            repo_name = repo.get("name")
            
            # Fetch collaborators (direct access assigned to this personal repository)
            collaborators_map = {}
            collabs = get_paginated(f"{GITEA_URL}/api/v1/repos/{username}/{repo_name}/collaborators")
            for collab in collabs:
                login = collab.get("login")
                
                # Check permissions
                role_name = collab.get("role_name", "")
                if not role_name:
                    perms = collab.get("permissions", {})
                    if perms.get("admin"): role_name = "admin"
                    elif perms.get("push"): role_name = "write"
                    else: role_name = "read"
                
                # Skip the owner 
                if login != username:
                    collaborators_map[login] = role_name
                    
            # Fetch branch protections
            protections = []
            bp_data = get_paginated(f"{GITEA_URL}/api/v1/repos/{username}/{repo_name}/branch_protections")
            for bp in bp_data:
                protections.append({
                    "branch_name": bp.get("branch_name"),
                    "enable_push": bp.get("enable_push", False),
                    "required_approvals": bp.get("required_approvals", 0)
                })

            repo_data = {
                "apiVersion": "v1",
                "kind": "Repository",
                "metadata": {"name": repo_name, "owner": username},
                "spec": {
                    "private": repo.get("private"),
                    "description": repo.get("description", ""),
                    "default_branch": repo.get("default_branch", "main"),
                    "collaborators": collaborators_map,
                    "branch_protections": protections
                }
            }
            with open(os.path.join(repos_dir, f"{repo_name}.yaml"), "w", encoding="utf-8") as f:
                yaml.dump(repo_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

def export_organizations():
    """Download all organizations, their teams, and repositories as YAML."""
    print("Exporting organizations, teams, and repositories...")
    orgs = get_paginated(f"{GITEA_URL}/api/v1/admin/orgs")
    
    for org in orgs:
        org_name = org.get("username")
        org_dir = os.path.join(EXPORT_DIR, "organizations", org_name)
        teams_dir = os.path.join(org_dir, "teams")
        repos_dir = os.path.join(org_dir, "repositories")
        
        os.makedirs(teams_dir, exist_ok=True)
        os.makedirs(repos_dir, exist_ok=True)
        
        # 1. Export Org basic info
        org_data = {
            "apiVersion": "v1",
            "kind": "Organization",
            "metadata": {"name": org_name},
            "spec": {
                "description": org.get("description", ""),
                "full_name": org.get("full_name", "")
            }
        }
        with open(os.path.join(org_dir, "org.yaml"), "w", encoding="utf-8") as f:
            yaml.dump(org_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
        # 2. Export Teams in this Org
        teams = get_paginated(f"{GITEA_URL}/api/v1/orgs/{org_name}/teams")
        for team in teams:
            team_name = team.get("name").lower().replace(" ", "-")
            
            # Get members of the team
            members = get_paginated(f"{GITEA_URL}/api/v1/teams/{team.get('id')}/members")
            member_logins = [m.get("login") for m in members]
            
            team_data = {
                "apiVersion": "v1",
                "kind": "Team",
                "metadata": {"name": team_name},
                "spec": {
                    "permission": team.get("permission"), # read, write, admin, owner, none (custom)
                    "includes_all_repositories": team.get("includes_all_repositories", False),
                    "can_create_org_repo": team.get("can_create_org_repo", False),
                    "units_map": team.get("units_map", {}),
                    "members": member_logins
                }
            }
            with open(os.path.join(teams_dir, f"{team_name}.yaml"), "w", encoding="utf-8") as f:
                yaml.dump(team_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        # 3. Export Repositories in this Org
        repos = get_paginated(f"{GITEA_URL}/api/v1/orgs/{org_name}/repos")
        for repo in repos:
            repo_name = repo.get("name")
            
            # Fetch direct collaborators for Org Repos (users added manually bypassing teams)
            collaborators_map = {}
            collabs = get_paginated(f"{GITEA_URL}/api/v1/repos/{org_name}/{repo_name}/collaborators")
            for collab in collabs:
                login = collab.get("login")
                
                # Check permissions
                role_name = collab.get("role_name", "")
                if not role_name:
                    perms = collab.get("permissions", {})
                    if perms.get("admin"): role_name = "admin"
                    elif perms.get("push"): role_name = "write"
                    else: role_name = "read"
                
                collaborators_map[login] = role_name
                
            # Fetch branch protections
            protections = []
            bp_data = get_paginated(f"{GITEA_URL}/api/v1/repos/{org_name}/{repo_name}/branch_protections")
            for bp in bp_data:
                protections.append({
                    "branch_name": bp.get("branch_name"),
                    "enable_push": bp.get("enable_push", False),
                    "required_approvals": bp.get("required_approvals", 0)
                })

            repo_data = {
                "apiVersion": "v1",
                "kind": "Repository",
                "metadata": {"name": repo_name, "owner": org_name},
                "spec": {
                    "private": repo.get("private"),
                    "description": repo.get("description", ""),
                    "default_branch": repo.get("default_branch", "main"),
                    "collaborators": collaborators_map,
                    "branch_protections": protections
                }
            }
            with open(os.path.join(repos_dir, f"{repo_name}.yaml"), "w", encoding="utf-8") as f:
                yaml.dump(repo_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

if __name__ == "__main__":
    export_users()
    export_organizations()
    print(f"\nExport completed! Check folder: {EXPORT_DIR}")

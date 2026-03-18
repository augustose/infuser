import requests
import urllib3
from config import GITEA_URL, HEADERS, WRITE_HEADERS, GITEA_ALLOW_WRITES
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_write_allowance():
    if not GITEA_ALLOW_WRITES:
        print("  [API: BLOCKED] 🔒 Write prevented. 'GITEA_ALLOW_WRITES' is configured to false.")
        return False
    return True

def create_user(username, spec):
    """Creates a user in Gitea."""
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/admin/users"
    payload = {
        "login_name": username,
        "username": username,
        "email": spec.get("email"),
        "full_name": spec.get("full_name", ""),
        "password": "Password123!", # Dummy password for initial creation
        "must_change_password": True,
        "send_notify": True
    }
    resp = requests.post(url, headers=WRITE_HEADERS, json=payload, verify=False)
    if resp.status_code == 201:
        print(f"  [API] ✅ Usuario {username} created successfully.")
        return True
    else:
        print(f"  [API] ❌ Error creating user {username}: {resp.text}")
        return False

def delete_user(username):
    """Deletes a user."""
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/admin/users/{username}"
    resp = requests.delete(url, headers=WRITE_HEADERS, verify=False)
    if resp.status_code in [200, 204]:
        print(f"  [API] 🗑️ User {username} deleted.")
        return True
    else:
        print(f"  [API] ❌ Error deleting user {username}: {resp.text}")
        return False

def create_organization(org_name, spec):
    """Creates an organization."""
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/orgs"
    payload = {
        "username": org_name,
        "full_name": spec.get("full_name", ""),
        "description": spec.get("description", "")
    }
    resp = requests.post(url, headers=WRITE_HEADERS, json=payload, verify=False)
    if resp.status_code == 201:
        print(f"  [API] ✅ Organization {org_name} created.")
        return True
    else:
        print(f"  [API] ❌ Error creating org {org_name}: {resp.text}")
        return False

def create_team(org_name, team_name, spec):
    """Creates a team inside an Organization."""
    if not check_write_allowance(): return None
    url = f"{GITEA_URL}/api/v1/orgs/{org_name}/teams"
    payload = {
        "name": team_name,
        "permission": spec.get("permission", "read"),
        "includes_all_repositories": spec.get("includes_all_repositories", False),
        "can_create_org_repo": spec.get("can_create_org_repo", False)
    }
    
    if "units_map" in spec:
        payload["units_map"] = spec["units_map"]

    resp = requests.post(url, headers=WRITE_HEADERS, json=payload, verify=False)
    if resp.status_code == 201:
        print(f"  [API] ✅ Team {team_name} ({org_name}) creado.")
        return resp.json().get("id")
    else:
        print(f"  [API] ❌ Error creating team {team_name}: {resp.text}")
        return None

def add_team_member(team_id, username):
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/teams/{team_id}/members/{username}"
    resp = requests.put(url, headers=WRITE_HEADERS, verify=False)
    if resp.status_code in [200, 204]:
        print(f"  [API] 👤 User {username} added to team.")
        return True
    else:
        print(f"  [API] ❌ Error adding {username}: {resp.text}")
        return False

def remove_team_member(team_id, username):
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/teams/{team_id}/members/{username}"
    resp = requests.delete(url, headers=WRITE_HEADERS, verify=False)
    if resp.status_code in [200, 204]:
        print(f"  [API] 👤 User {username} removed from team.")
        return True
    else:
        print(f"  [API] ❌ Error removing {username}: {resp.text}")
        return False

def create_org_repo(org_name, repo_name, spec):
    """Creates a repository inside an Organization."""
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/orgs/{org_name}/repos"
    payload = {
        "name": repo_name,
        "private": spec.get("private", True),
        "description": spec.get("description", ""),
        "default_branch": spec.get("default_branch", "main")
    }
    resp = requests.post(url, headers=WRITE_HEADERS, json=payload, verify=False)
    if resp.status_code == 201:
        print(f"  [API] ✅ Repository {repo_name} creado.")
        return True
    else:
        print(f"  [API] ❌ Error creating repo {repo_name}: {resp.text}")
        return False

def find_team_id(org_name, team_name):
    url = f"{GITEA_URL}/api/v1/orgs/{org_name}/teams"
    resp = requests.get(url, headers=HEADERS, verify=False) # GET is a READ operation, keep HEADERS
    if resp.status_code == 200:
        for t in resp.json():
            if t["name"].lower().replace(' ', '-') == team_name.lower().replace(' ', '-'):
                return t["id"]
    return None

def delete_team(org_name, team_name):
    team_id = find_team_id(org_name, team_name)
    if team_id:
        if not check_write_allowance(): return False
        url = f"{GITEA_URL}/api/v1/teams/{team_id}"
        resp = requests.delete(url, headers=WRITE_HEADERS, verify=False)
        if resp.status_code in [200, 204]:
            print(f"  [API] 🗑️ Team {team_name} deleted.")
            return True
        else:
            print(f"  [API] ❌ Error deleting team {team_name}: {resp.text}")
            return False
    return False

def delete_org_repo(org_name, repo_name):
    """Deletes a repository from an Organization."""
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/repos/{org_name}/{repo_name}"
    resp = requests.delete(url, headers=WRITE_HEADERS, verify=False)
    if resp.status_code in [200, 204]:
        print(f"  [API] 🗑️ Repository {repo_name} deleted.")
        return True
    else:
        print(f"  [API] ❌ Error deleting repo {repo_name}: {resp.text}")
        return False

def update_user(username, changed_spec):
    """Updates user properties via PATCH /admin/users/{username}."""
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/admin/users/{username}"
    payload = {"login_name": username, "source_id": 0}
    for key in ["email", "full_name", "active"]:
        if key in changed_spec:
            payload[key] = changed_spec[key]
    resp = requests.patch(url, headers=WRITE_HEADERS, json=payload, verify=False)
    if resp.status_code == 200:
        print(f"  [API] ✅ User {username} updated.")
        return True
    else:
        print(f"  [API] ❌ Error updating user {username}: {resp.text}")
        return False

def update_repo(owner, repo_name, changed_spec):
    """Updates repository properties via PATCH /repos/{owner}/{repo}."""
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/repos/{owner}/{repo_name}"
    payload = {}
    for key in ["description", "private", "default_branch"]:
        if key in changed_spec:
            payload[key] = changed_spec[key]
    if not payload:
        return True
    resp = requests.patch(url, headers=WRITE_HEADERS, json=payload, verify=False)
    if resp.status_code == 200:
        print(f"  [API] ✅ Repository {owner}/{repo_name} updated.")
        return True
    else:
        print(f"  [API] ❌ Error updating repo {owner}/{repo_name}: {resp.text}")
        return False

def update_organization(org_name, changed_spec):
    """Updates organization properties via PATCH /orgs/{org}."""
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/orgs/{org_name}"
    payload = {}
    for key in ["description", "full_name"]:
        if key in changed_spec:
            payload[key] = changed_spec[key]
    if not payload:
        return True
    resp = requests.patch(url, headers=WRITE_HEADERS, json=payload, verify=False)
    if resp.status_code == 200:
        print(f"  [API] ✅ Organization {org_name} updated.")
        return True
    else:
        print(f"  [API] ❌ Error updating org {org_name}: {resp.text}")
        return False

def update_team(org_name, team_name, changed_spec):
    """Updates team properties via PATCH /teams/{id}."""
    if not check_write_allowance(): return False
    team_id = find_team_id(org_name, team_name)
    if not team_id:
        print(f"  [API] ❌ Team {team_name} not found in {org_name}.")
        return False
    url = f"{GITEA_URL}/api/v1/teams/{team_id}"
    payload = {}
    for key in ["permission", "includes_all_repositories", "can_create_org_repo"]:
        if key in changed_spec:
            payload[key] = changed_spec[key]
    if "units_map" in changed_spec:
        payload["units_map"] = changed_spec["units_map"]
    if not payload:
        return True
    resp = requests.patch(url, headers=WRITE_HEADERS, json=payload, verify=False)
    if resp.status_code == 200:
        print(f"  [API] ✅ Team {team_name} ({org_name}) updated.")
        return True
    else:
        print(f"  [API] ❌ Error updating team {team_name}: {resp.text}")
        return False

def create_user_repo(username, repo_name, spec):
    """Creates a personal repository for a user via POST /admin/users/{username}/repos."""
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/admin/users/{username}/repos"
    payload = {
        "name": repo_name,
        "private": spec.get("private", True),
        "description": spec.get("description", ""),
        "default_branch": spec.get("default_branch", "main")
    }
    resp = requests.post(url, headers=WRITE_HEADERS, json=payload, verify=False)
    if resp.status_code == 201:
        print(f"  [API] ✅ Repository {username}/{repo_name} created.")
        return True
    else:
        print(f"  [API] ❌ Error creating repo {username}/{repo_name}: {resp.text}")
        return False

def delete_user_repo(username, repo_name):
    """Deletes a personal repository."""
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/repos/{username}/{repo_name}"
    resp = requests.delete(url, headers=WRITE_HEADERS, verify=False)
    if resp.status_code in [200, 204]:
        print(f"  [API] 🗑️ Repository {username}/{repo_name} deleted.")
        return True
    else:
        print(f"  [API] ❌ Error deleting repo {username}/{repo_name}: {resp.text}")
        return False

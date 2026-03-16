import requests
import urllib3
from config import GITEA_URL, HEADERS
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_user(username, spec):
    """Creates a user in Gitea."""
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
    resp = requests.post(url, headers=HEADERS, json=payload, verify=False)
    if resp.status_code == 201:
        print(f"  [API] ✅ Usuario {username} creado con éxito.")
    else:
        print(f"  [API] ❌ Error creando usuario {username}: {resp.text}")

def delete_user(username):
    """Deletes a user."""
    url = f"{GITEA_URL}/api/v1/admin/users/{username}"
    resp = requests.delete(url, headers=HEADERS, verify=False)
    if resp.status_code in [200, 204]:
        print(f"  [API] 🗑️ Usuario {username} eliminado.")
    else:
        print(f"  [API] ❌ Error eliminando usuario {username}: {resp.text}")

def create_organization(org_name, spec):
    """Creates an organization."""
    url = f"{GITEA_URL}/api/v1/orgs"
    payload = {
        "username": org_name,
        "full_name": spec.get("full_name", ""),
        "description": spec.get("description", "")
    }
    resp = requests.post(url, headers=HEADERS, json=payload, verify=False)
    if resp.status_code == 201:
        print(f"  [API] ✅ Organización {org_name} creada.")
    else:
        print(f"  [API] ❌ Error creando org {org_name}: {resp.text}")

def create_team(org_name, team_name, spec):
    """Creates a team inside an Organization."""
    url = f"{GITEA_URL}/api/v1/orgs/{org_name}/teams"
    payload = {
        "name": team_name,
        "permission": spec.get("permission", "read"),
        "includes_all_repositories": spec.get("includes_all_repositories", False),
        "can_create_org_repo": spec.get("can_create_org_repo", False)
    }
    # units map handle later
    resp = requests.post(url, headers=HEADERS, json=payload, verify=False)
    if resp.status_code == 201:
        print(f"  [API] ✅ Equipo {team_name} ({org_name}) creado.")
        return resp.json().get("id")
    else:
        print(f"  [API] ❌ Error creando equipo {team_name}: {resp.text}")
        return None

def add_team_member(team_id, username):
    url = f"{GITEA_URL}/api/v1/teams/{team_id}/members/{username}"
    resp = requests.put(url, headers=HEADERS, verify=False)
    if resp.status_code in [200, 204]:
        print(f"  [API] 👤 Usuario {username} añadido al equipo.")
    else:
        print(f"  [API] ❌ Error añadiendo {username}: {resp.text}")

def remove_team_member(team_id, username):
    url = f"{GITEA_URL}/api/v1/teams/{team_id}/members/{username}"
    resp = requests.delete(url, headers=HEADERS, verify=False)
    if resp.status_code in [200, 204]:
        print(f"  [API] 👤 Usuario {username} removido del equipo.")
    else:
        print(f"  [API] ❌ Error removiendo {username}: {resp.text}")

def create_org_repo(org_name, repo_name, spec):
    """Creates a repository inside an Organization."""
    url = f"{GITEA_URL}/api/v1/orgs/{org_name}/repos"
    payload = {
        "name": repo_name,
        "private": spec.get("private", True),
        "description": spec.get("description", ""),
        "default_branch": spec.get("default_branch", "main")
    }
    resp = requests.post(url, headers=HEADERS, json=payload, verify=False)
    if resp.status_code == 201:
        print(f"  [API] ✅ Repositorio {repo_name} creado.")
    else:
        print(f"  [API] ❌ Error creando repo {repo_name}: {resp.text}")

def find_team_id(org_name, team_name):
    url = f"{GITEA_URL}/api/v1/orgs/{org_name}/teams"
    resp = requests.get(url, headers=HEADERS, verify=False)
    if resp.status_code == 200:
        for t in resp.json():
            if t["name"].lower().replace(' ', '-') == team_name.lower().replace(' ', '-'):
                return t["id"]
    return None

def delete_team(org_name, team_name):
    team_id = find_team_id(org_name, team_name)
    if team_id:
        url = f"{GITEA_URL}/api/v1/teams/{team_id}"
        resp = requests.delete(url, headers=HEADERS, verify=False)
        if resp.status_code in [200, 204]:
            print(f"  [API] 🗑️ Equipo {team_name} eliminado.")
        else:
            print(f"  [API] ❌ Error eliminando equipo {team_name}: {resp.text}")

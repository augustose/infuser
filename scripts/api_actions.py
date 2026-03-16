import requests
import urllib3
from config import GITEA_URL, HEADERS, WRITE_HEADERS, GITEA_ALLOW_WRITES
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_write_allowance():
    if not GITEA_ALLOW_WRITES:
        print("  [API: BLOQUEO] 🔒 Escritura prevenida. 'GITEA_ALLOW_WRITES' está apagado.")
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
        print(f"  [API] ✅ Usuario {username} creado con éxito.")
        return True
    else:
        print(f"  [API] ❌ Error creando usuario {username}: {resp.text}")
        return False

def delete_user(username):
    """Deletes a user."""
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/admin/users/{username}"
    resp = requests.delete(url, headers=WRITE_HEADERS, verify=False)
    if resp.status_code in [200, 204]:
        print(f"  [API] 🗑️ Usuario {username} eliminado.")
        return True
    else:
        print(f"  [API] ❌ Error eliminando usuario {username}: {resp.text}")
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
        print(f"  [API] ✅ Organización {org_name} creada.")
        return True
    else:
        print(f"  [API] ❌ Error creando org {org_name}: {resp.text}")
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
    # units map handle later
    resp = requests.post(url, headers=WRITE_HEADERS, json=payload, verify=False)
    if resp.status_code == 201:
        print(f"  [API] ✅ Equipo {team_name} ({org_name}) creado.")
        return resp.json().get("id")
    else:
        print(f"  [API] ❌ Error creando equipo {team_name}: {resp.text}")
        return None

def add_team_member(team_id, username):
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/teams/{team_id}/members/{username}"
    resp = requests.put(url, headers=WRITE_HEADERS, verify=False)
    if resp.status_code in [200, 204]:
        print(f"  [API] 👤 Usuario {username} añadido al equipo.")
        return True
    else:
        print(f"  [API] ❌ Error añadiendo {username}: {resp.text}")
        return False

def remove_team_member(team_id, username):
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/teams/{team_id}/members/{username}"
    resp = requests.delete(url, headers=WRITE_HEADERS, verify=False)
    if resp.status_code in [200, 204]:
        print(f"  [API] 👤 Usuario {username} removido del equipo.")
        return True
    else:
        print(f"  [API] ❌ Error removiendo {username}: {resp.text}")
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
        print(f"  [API] ✅ Repositorio {repo_name} creado.")
        return True
    else:
        print(f"  [API] ❌ Error creando repo {repo_name}: {resp.text}")
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
            print(f"  [API] 🗑️ Equipo {team_name} eliminado.")
            return True
        else:
            print(f"  [API] ❌ Error eliminando equipo {team_name}: {resp.text}")
            return False
    return False

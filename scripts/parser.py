import os
import yaml

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "infuser-config")

def read_yaml(filepath):
    """Returns YAML content or None if the file is ignored."""
    if not filepath.endswith(".yaml") and not filepath.endswith(".yml"):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading YAML {filepath}: {e}")
        return None

def parse_all_config():
    """
    Reads infuser-config/ and compiles a 'desired state' in memory.
    """
    desired_state = {
        "users": {},
        "organizations": {}
    }

    if not os.path.exists(CONFIG_DIR):
        print(f"Directory not found: {CONFIG_DIR}")
        return desired_state

    # Parsear users
    users_dir = os.path.join(CONFIG_DIR, "users")
    if os.path.exists(users_dir):
        for user_name in os.listdir(users_dir):
            user_path = os.path.join(users_dir, user_name)
            if not os.path.isdir(user_path):
                continue
                
            # User definition
            data = read_yaml(os.path.join(user_path, "user.yaml"))
            if data and data.get("kind") == "User":
                name = data["metadata"]["name"]
                # Create a structure for user that also holds their personal repos
                desired_state["users"][name] = data
                desired_state["users"][name]["repositories"] = {}
                
                # Parse personal repositories
                repos_dir = os.path.join(user_path, "repositories")
                if os.path.exists(repos_dir):
                    for filename in os.listdir(repos_dir):
                        repo_data = read_yaml(os.path.join(repos_dir, filename))
                        if repo_data and repo_data.get("kind") == "Repository":
                            repo_name = repo_data["metadata"]["name"]
                            desired_state["users"][name]["repositories"][repo_name] = repo_data

    # Parsear orgs
    orgs_dir = os.path.join(CONFIG_DIR, "organizations")
    if os.path.exists(orgs_dir):
        for org_name in os.listdir(orgs_dir):
            org_path = os.path.join(orgs_dir, org_name)
            if not os.path.isdir(org_path):
                continue

            org_state = {"teams": {}, "repositories": {}}

            # Org definition
            org_def = read_yaml(os.path.join(org_path, "org.yaml"))
            if org_def:
                org_state["metadata"] = org_def.get("metadata", {})
                org_state["spec"] = org_def.get("spec", {})

            # Teams
            teams_dir = os.path.join(org_path, "teams")
            if os.path.exists(teams_dir):
                for filename in os.listdir(teams_dir):
                    data = read_yaml(os.path.join(teams_dir, filename))
                    if data and data.get("kind") == "Team":
                        name = data["metadata"]["name"]
                        org_state["teams"][name] = data

            # Repositories
            repos_dir = os.path.join(org_path, "repositories")
            if os.path.exists(repos_dir):
                for filename in os.listdir(repos_dir):
                    data = read_yaml(os.path.join(repos_dir, filename))
                    if data and data.get("kind") == "Repository":
                        name = data["metadata"]["name"]
                        org_state["repositories"][name] = data

            desired_state["organizations"][org_name] = org_state

    return desired_state

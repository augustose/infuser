import os
import json

STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".infuser_state.json")

class LocalMemory:
    """
    Handles the local state (memory) of Infuser reconciliations.
    """
    def __init__(self):
        self.state = self.load()

    def load(self):
        if not os.path.exists(STATE_FILE):
            # Si no existe, retornamos un estado vacío.
            return {
                "users": {},
                "organizations": {}
            }
        
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("WARNING: Corrupted state file. Returning empty state.")
                return {"users": {}, "organizations": {}}

    def save(self):
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)
        print("Local state successfully saved.")

    def get_user(self, username):
        return self.state["users"].get(username)

    def set_user(self, username, user_data):
        self.state["users"][username] = user_data

    def set_org(self, org_name, org_data):
        if org_name not in self.state["organizations"]:
            self.state["organizations"][org_name] = {"teams": {}, "repositories": {}}
            
        self.state["organizations"][org_name]["metadata"] = org_data.get("metadata", {})
        self.state["organizations"][org_name]["spec"] = org_data.get("spec", {})

    def set_team(self, org_name, team_name, team_data):
        if org_name not in self.state["organizations"]:
            self.state["organizations"][org_name] = {"teams": {}, "repositories": {}}
        self.state["organizations"][org_name]["teams"][team_name] = team_data

    def set_repo(self, org_name, repo_name, repo_data):
        if org_name not in self.state["organizations"]:
            self.state["organizations"][org_name] = {"teams": {}, "repositories": {}}
        self.state["organizations"][org_name]["repositories"][repo_name] = repo_data

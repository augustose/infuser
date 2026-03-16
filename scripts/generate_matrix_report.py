import os
import csv
from parser import parse_all_config
from datetime import datetime

REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "reports", "matrix")

def generate_matrix_reports():
    os.makedirs(REPORT_DIR, exist_ok=True)
    state = parse_all_config()
    
    # We use a timestamp to allow historical comparisons
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    
    # We will generate one matrix report per organization
    for org_name, org_data in state.get("organizations", {}).items():
        teams = org_data.get("teams", {})
        repos = org_data.get("repositories", {})
        
        if not repos:
            continue
            
        repo_names = sorted(list(repos.keys()))
        
        # 1. Collect all users in this org from all teams
        users_in_org = set()
        user_team_map = {} # map user -> list of teams they belong to
        for t_name, t_data in teams.items():
            members = t_data.get("spec", {}).get("members", [])
            for m in members:
                users_in_org.add(m)
                if m not in user_team_map:
                    user_team_map[m] = []
                user_team_map[m].append(t_name)
                
        # Include global admins since they theoretically have access to everything
        global_admins = [u for u, d in state.get("users", {}).items() if d.get("spec", {}).get("is_admin")]
        users_list = sorted(list(users_in_org.union(set(global_admins))))
        
        # 2. Build the Matrix (Transposed: Projects as Rows, Users as Columns)
        matrix = []
        header = ["Project / Repository"] + users_list
        matrix.append(header)
        
        for repo_name in repo_names:
            row = [repo_name]
            for user in users_list:
                if user in global_admins:
                    row.append("Admin (Glo)")
                    continue
                
                # Calculate the accumulated highest permission for this user on this specific repo
                highest_perm = "None"
                # Simple weight to determine what "beats" what
                perm_weight = {"None": 0, "Read": 1, "Write": 2, "Admin": 3, "Owner": 4}
                
                user_teams = user_team_map.get(user, [])
                for t_name in user_teams:
                    t_spec = teams[t_name].get("spec", {})
                    
                    # Logic: Does the team have access?
                    if t_spec.get("includes_all_repositories", False): 
                        raw_perm = t_spec.get("permission", "none")
                        perm = "None"
                        
                        if raw_perm == "read": perm = "Read"
                        elif raw_perm == "write": perm = "Write"
                        elif raw_perm in ["admin", "owner"]: perm = "Admin"
                        elif raw_perm == "none" and t_spec.get("units_map"):
                            # Parse granular units
                            units = t_spec.get("units_map", {})
                            if "owner" in units.values() or "admin" in units.values():
                                perm = "Admin"
                            elif units.get("repo.code") == "write" or "write" in units.values():
                                perm = "Write"
                            elif "read" in units.values():
                                perm = "Read"
                                
                        if perm_weight[perm] > perm_weight[highest_perm]:
                            highest_perm = perm
                
                row.append(highest_perm if highest_perm != "None" else "-")
            matrix.append(row)
            
        # 3. Write CSV Output (Ideal for Over Time Comparison in Excel)
        csv_filename = os.path.join(REPORT_DIR, f"{org_name}_matrix_{timestamp}.csv")
        with open(csv_filename, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(matrix)
            
        # 4. Write Markdown Output (Grilla anidada / Tabla visual)
        md_filename = os.path.join(REPORT_DIR, f"{org_name}_matrix_{timestamp}.md")
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(f"# 🛡️ Access Matrix: **{org_name}**\n\n")
            f.write(f"> **Generated on:** `{timestamp}`\n")
            f.write("> *Displays the highest accumulated access level per user across all projects.*\n\n")
            
            # Markdown Table Header
            f.write("| " + " | ".join(header) + " |\n")
            f.write("|" + "|".join(["---" for _ in header]) + "|\n")
            
            # Markdown Table Rows
            for r in matrix[1:]:
                f.write("| " + " | ".join(r) + " |\n")
                
        print(f"✅ Matriz generada para la organización '{org_name}':")
        print(f"   📄 CSV: {csv_filename}")
        print(f"   📊 MD:  {md_filename}\n")

if __name__ == "__main__":
    generate_matrix_reports()

import argparse
from parser import parse_all_config
from memory import LocalMemory

class EngineOptions:
    def __init__(self, dry_run=True, auto_approve=False):
        self.dry_run = dry_run
        self.auto_approve = auto_approve

def run_engine(options: EngineOptions):
    print("========================================")
    print("  🚀 Infuser - Motor de Reconciliación  ")
    print("========================================")
    if options.dry_run:
        print("[DRY RUN MODE ENABLED] - Showing Execution Plan.")
    else:
        print("[APPLY MODE ENABLED] - Evaluating changes to persist.")
    
    print("\n[1/3] Construyendo el Estado Deseado desde YAMLs...")
    desired_state = parse_all_config()
    print(f"  👉 Users found: {len(desired_state['users'])}")
    print(f"  👉 Organizations found: {len(desired_state['organizations'])}")

    print("\n[2/3] Verificando Memoria Local (Estado Prevío / Actual)...")
    memory = LocalMemory()
    
    if not memory.state["users"] and not memory.state["organizations"]:
        print("  ⚠️ Local memory is empty. Assuming state was just exported from Gitea.")
        print("     Building base memory from current YAML files...")
        if not options.dry_run:
            memory.state = desired_state
            memory.save()
            print("  ✅ Initial memory persisted successfully.")
        else:
            print("  🚫 (Skipped saving in Dry Run mode).")
        return 

    import api_actions

    print("\n[3/3] Eventos Planeados (Diff Plan)...")
    actions = []

    # Diff Usuarios
    current_users = set(memory.state.get("users", {}).keys())
    desired_users = set(desired_state.get("users", {}).keys())

    for user in (desired_users - current_users):
        actions.append((f"  ➕ [CREATE] User: {user}", api_actions.create_user, (user, desired_state["users"][user]["spec"])))
    for user in (current_users - desired_users):
        actions.append((f"  ➖ [DELETE/ARCHIVE] User: {user}", api_actions.delete_user, (user,)))

    # Diff Orgs y Teams
    current_orgs = set(memory.state.get("organizations", {}).keys())
    desired_orgs = set(desired_state.get("organizations", {}).keys())

    for org in (desired_orgs - current_orgs):
        actions.append((f"  ➕ [CREATE] Organization: {org}", api_actions.create_organization, (org, desired_state["organizations"][org]["spec"])))
        
        # Si la organización es nueva, también debemos crear sus equipos y repositorios internos definidos
        d_org = desired_state["organizations"][org]
        d_teams = set(d_org.get("teams", {}).keys())
        for team in d_teams:
            spec = d_org["teams"][team].get("spec", {})
            def create_team_with_members_new_org(o=org, t=team, s=spec):
                t_id = api_actions.create_team(o, t, s)
                if t_id:
                    for m in s.get("members", []):
                        api_actions.add_team_member(t_id, m)
            actions.append((f"  ➕ [CREATE] Team: {team} (Org: {org})", create_team_with_members_new_org, ()))
            
        d_repos = set(d_org.get("repositories", {}).keys())
        for repo in d_repos:
            actions.append((f"  ➕ [CREATE] Repository: {repo} (Org: {org})", api_actions.create_org_repo, (org, repo, d_org["repositories"][repo].get("spec", {}))))
    
    for org in desired_orgs.intersection(current_orgs):
        c_org = memory.state["organizations"][org]
        d_org = desired_state["organizations"][org]
        
        c_teams = set(c_org.get("teams", {}).keys())
        d_teams = set(d_org.get("teams", {}).keys())
        
        for team in (d_teams - c_teams):
            spec = d_org["teams"][team].get("spec", {})
            def create_team_with_members(o=org, t=team, s=spec):
                t_id = api_actions.create_team(o, t, s)
                if t_id:
                    for m in s.get("members", []):
                        api_actions.add_team_member(t_id, m)
            actions.append((f"  ➕ [CREATE] Team: {team} (Org: {org})", create_team_with_members, ()))
            
        for team in (c_teams - d_teams):
            actions.append((f"  ➖ [DELETE] Team: {team} (Org: {org})", api_actions.delete_team, (org, team)))
            
        for team in d_teams.intersection(c_teams):
            c_members = set(c_org["teams"][team].get("spec", {}).get("members", []))
            d_members = set(d_org["teams"][team].get("spec", {}).get("members", []))
            
            for m in (d_members - c_members):
                def add_m(o=org, t=team, mbr=m):
                    t_id = api_actions.find_team_id(o, t)
                    if t_id: api_actions.add_team_member(t_id, mbr)
                actions.append((f"  👥 [ADD MEMBER] Usuario '{m}' -> Equipo: {team} (Org: {org})", add_m, ()))
                
            for m in (c_members - d_members):
                def rm_m(o=org, t=team, mbr=m):
                    t_id = api_actions.find_team_id(o, t)
                    if t_id: api_actions.remove_team_member(t_id, mbr)
                actions.append((f"  👥 [REMOVE MEMBER] Usuario '{m}' <- Equipo: {team} (Org: {org})", rm_m, ()))
        
        c_repos = set(c_org.get("repositories", {}).keys())
        d_repos = set(d_org.get("repositories", {}).keys())
        
        for repo in (d_repos - c_repos):
            actions.append((f"  ➕ [CREATE] Repository: {repo} (Org: {org})", api_actions.create_org_repo, (org, repo, d_org["repositories"][repo].get("spec", {}))))
                
        for repo in (c_repos - d_repos):
            actions.append((f"  ➖ [ARCHIVE] Repository: {repo} (Org: {org})", lambda: None, ()))

    for msg, func, args in actions:
        print(msg)

    print("\n----------------------------------------")
    if not actions:
        print("✨ EVERYTHING IN SYNC: Desired State (YAML) matches Local Memory.")
        return

    print(f"⚠️ Calculated {len(actions)} changes to reconcile infrastructure.")
    
    if options.dry_run:
        print("💡 Finished. Run with `--apply` to commit these changes to the server.")
        return
        
    if not options.auto_approve:
        resp = input("\n¿Estás seguro de que quieres aplicar estos cambios en Gitea? (y/n): ")
        if resp.lower() not in ['y', 'yes', 's', 'si']:
            print("🛑 Action canceled by user.")
            return

    from config import GITEA_ALLOW_WRITES
    if not GITEA_ALLOW_WRITES:
        print("\n🔒 [ERROR FATAL] Operación abortada.")
        print("   Attempted to use '--apply' but writes are disabled by configuration (GITEA_ALLOW_WRITES=false).")
        print("   Please modify environment variables to authorize writes in this environment.")
        return

    print("\n🚀 Aplicando cambios de verdad...")
    for msg, func, args in actions:
        func(*args)

    print("\n💾 Guardando el nuevo Estado Deseado en la memoria local...")
    memory.state = desired_state
    memory.save()
    print("✅ Mission Accomplished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Infuser Reconciliation Engine")
    parser.add_argument("--apply", action="store_true", help="Permanently applies changes in Gitea and saves them to memory")
    parser.add_argument("--auto-approve", action="store_true", help="Skips confirmation prompt if --apply is active")
    args = parser.parse_args()

    options = EngineOptions(dry_run=not args.apply, auto_approve=args.auto_approve)
    run_engine(options)

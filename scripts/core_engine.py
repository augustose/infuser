import argparse
from parser import parse_all_config
from memory import LocalMemory

class EngineOptions:
    def __init__(self, dry_run=True, auto_approve=False):
        self.dry_run = dry_run
        self.auto_approve = auto_approve

def run_engine(options: EngineOptions):
    print("========================================")
    print("  🚀 GiteAdmin - Motor de Reconciliación  ")
    print("========================================")
    if options.dry_run:
        print("[MODO DRY RUN ACTIVADO] - Mostrando Plan de Ejecución.")
    else:
        print("[MODO APPLY ACTIVADO] - Evaluando cambios a persistir.")
    
    print("\n[1/3] Construyendo el Estado Deseado desde YAMLs...")
    desired_state = parse_all_config()
    print(f"  👉 Usuarios encontrados: {len(desired_state['users'])}")
    print(f"  👉 Organizaciones encontradas: {len(desired_state['organizations'])}")

    print("\n[2/3] Verificando Memoria Local (Estado Prevío / Actual)...")
    memory = LocalMemory()
    
    if not memory.state["users"] and not memory.state["organizations"]:
        print("  ⚠️ La memoria local está vacía. Suponiendo que acabamos de exportar el estado desde Gitea.")
        print("     Construyendo memoria base desde los archivos YAML actuales...")
        if not options.dry_run:
            memory.state = desired_state
            memory.save()
            print("  ✅ Memoria inicial persistida con éxito.")
        else:
            print("  🚫 (Omitido guardar en modo Dry Run).")
        return 

    import api_actions

    print("\n[3/3] Eventos Planeados (Diff Plan)...")
    actions = []

    # Diff Usuarios
    current_users = set(memory.state.get("users", {}).keys())
    desired_users = set(desired_state.get("users", {}).keys())

    for user in (desired_users - current_users):
        actions.append((f"  ➕ [CREAR] Usuario: {user}", api_actions.create_user, (user, desired_state["users"][user]["spec"])))
    for user in (current_users - desired_users):
        actions.append((f"  ➖ [ELIMINAR/ARCHIVAR] Usuario: {user}", api_actions.delete_user, (user,)))

    # Diff Orgs y Teams
    current_orgs = set(memory.state.get("organizations", {}).keys())
    desired_orgs = set(desired_state.get("organizations", {}).keys())

    for org in (desired_orgs - current_orgs):
        actions.append((f"  ➕ [CREAR] Organización: {org}", api_actions.create_organization, (org, desired_state["organizations"][org]["spec"])))
    
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
            actions.append((f"  ➕ [CREAR] Equipo: {team} (Org: {org})", create_team_with_members, ()))
            
        for team in (c_teams - d_teams):
            actions.append((f"  ➖ [ELIMINAR] Equipo: {team} (Org: {org})", api_actions.delete_team, (org, team)))
            
        for team in d_teams.intersection(c_teams):
            c_members = set(c_org["teams"][team].get("spec", {}).get("members", []))
            d_members = set(d_org["teams"][team].get("spec", {}).get("members", []))
            
            for m in (d_members - c_members):
                def add_m(o=org, t=team, mbr=m):
                    t_id = api_actions.find_team_id(o, t)
                    if t_id: api_actions.add_team_member(t_id, mbr)
                actions.append((f"  👥 [AÑADIR MIEMBRO] Usuario '{m}' -> Equipo: {team} (Org: {org})", add_m, ()))
                
            for m in (c_members - d_members):
                def rm_m(o=org, t=team, mbr=m):
                    t_id = api_actions.find_team_id(o, t)
                    if t_id: api_actions.remove_team_member(t_id, mbr)
                actions.append((f"  👥 [REMOVER MIEMBRO] Usuario '{m}' <- Equipo: {team} (Org: {org})", rm_m, ()))
        
        c_repos = set(c_org.get("repositories", {}).keys())
        d_repos = set(d_org.get("repositories", {}).keys())
        
        for repo in (d_repos - c_repos):
            actions.append((f"  ➕ [CREAR] Repositorio: {repo} (Org: {org})", api_actions.create_org_repo, (org, repo, d_org["repositories"][repo].get("spec", {}))))
                
        for repo in (c_repos - d_repos):
            actions.append((f"  ➖ [ARCHIVAR] Repositorio: {repo} (Org: {org})", lambda: None, ()))

    for msg, func, args in actions:
        print(msg)

    print("\n----------------------------------------")
    if not actions:
        print("✨ TODO EN SINCRONÍA: El Estado Deseado (YAML) coincide con la Memoria Local.")
        return

    print(f"⚠️ Se calcularon {len(actions)} cambios para reconciliar la infraestructura.")
    
    if options.dry_run:
        print("💡 Terminado. Ejecuta indicando `--apply` para efectuar estos cambios en el servidor.")
        return
        
    if not options.auto_approve:
        resp = input("\n¿Estás seguro de que quieres aplicar estos cambios en Gitea? (y/n): ")
        if resp.lower() not in ['y', 'yes', 's', 'si']:
            print("🛑 Acción cancelada por el usuario.")
            return

    print("\n🚀 Aplicando cambios de verdad...")
    for msg, func, args in actions:
        func(*args)

    print("\n💾 Guardando el nuevo Estado Deseado en la memoria local...")
    memory.state = desired_state
    memory.save()
    print("✅ Misión Cumplida.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GiteAdmin Reconciliation Engine")
    parser.add_argument("--apply", action="store_true", help="Aplica permanentemente los cambios en Gitea y guarda en memoria")
    parser.add_argument("--auto-approve", action="store_true", help="Salta el prompt de confirmación si --apply está activo")
    args = parser.parse_args()

    options = EngineOptions(dry_run=not args.apply, auto_approve=args.auto_approve)
    run_engine(options)

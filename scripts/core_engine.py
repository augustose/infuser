import argparse
from parser import parse_all_config
from memory import LocalMemory

class EngineOptions:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run

def compare_dicts(name, path, current, desired):
    """Compara 2 diccionarios y reporta diferencias. Para simplificar, comparamos el 'spec' principal."""
    # Para la prueba, simplemente comprobaremos la presencia / ausencia total por el momento.
    pass

def run_engine(options: EngineOptions):
    print("========================================")
    print("  🚀 GiteAdmin - Motor de Reconciliación  ")
    print("========================================")
    if options.dry_run:
        print("[MODO DRY RUN ACTIVADO] - No se realizarán cambios en Gitea.")
    
    # 1. Obtenemos el estado deseado (Archivos YAML locales)
    print("\n[1/3] Construyendo el Estado Deseado desde YAMLs...")
    desired_state = parse_all_config()
    print(f"  👉 Usuarios encontrados: {len(desired_state['users'])}")
    print(f"  👉 Organizaciones encontradas: {len(desired_state['organizations'])}")

    # 2. Obtenemos el estado actual desde la Memoria Local (o asume un blank si no existe aún)
    # Por ahora tomamos la decisión de inicializar el state = local si no existe para que nuestro próximo engine pase se encargue.
    print("\n[2/3] Verificando Memoria Local (Estado Prevío / Actual)...")
    memory = LocalMemory()
    
    # IMPORTANTE: Si es la primera vez (estado vacío pero tenemos YAMLs locales),
    # tomaremos los YAMLs como nuestra memoria base, como si la 'Exportación' fuera el state(0).
    if not memory.state["users"] and not memory.state["organizations"]:
        print("  ⚠️ La memoria local está vacía. Suponiendo que acabamos de exportar el estado desde Gitea.")
        print("     Construyendo memoria base desde los archivos YAML actuales...")
        if not options.dry_run:
            memory.state = desired_state
            memory.save()
            print("  ✅ Memoria inicial persistida con éxito.")
        else:
            print("  🚫 (Omitido guardar en modo Dry Run).")
        return # Terminamos aquí la primera corrida

    # 3. Diff Engine (Básico para esta iteración)
    print("\n[3/3] Calculando Diferencias (Diff)...")
    changes_detected = 0

    # Diff Usuarios
    current_users = set(memory.state["users"].keys())
    desired_users = set(desired_state["users"].keys())

    users_to_create = desired_users - current_users
    users_to_delete = current_users - desired_users # Opciones de archivado, por ej.

    for user in users_to_create:
        print(f"  ➕ [CREAR] Usuario: {user}")
        changes_detected += 1
    for user in users_to_delete:
        print(f"  ➖ [ELIMINAR/ARCHIVAR] Usuario: {user}")
        changes_detected += 1

    # Diff Orgs y Teams
    current_orgs = set(memory.state.get("organizations", {}).keys())
    desired_orgs = set(desired_state.get("organizations", {}).keys())

    for org in (desired_orgs - current_orgs):
        print(f"  ➕ [CREAR] Organización: {org}")
        changes_detected += 1
    
    # Diff interno a las organizaciones
    for org in desired_orgs.intersection(current_orgs):
        c_org = memory.state["organizations"][org]
        d_org = desired_state["organizations"][org]
        
        # Diff Equipos
        c_teams = set(c_org.get("teams", {}).keys())
        d_teams = set(d_org.get("teams", {}).keys())
        
        for team in (d_teams - c_teams):
            print(f"  ➕ [CREAR] Equipo: {team} (Org: {org})")
            changes_detected += 1
        for team in (c_teams - d_teams):
            print(f"  ➖ [ELIMINAR] Equipo: {team} (Org: {org})")
            changes_detected += 1
            
        # Check miembros en los equipos que se mantienen
        for team in d_teams.intersection(c_teams):
            c_members = set(c_org["teams"][team].get("spec", {}).get("members", []))
            d_members = set(d_org["teams"][team].get("spec", {}).get("members", []))
            
            for m in (d_members - c_members):
                print(f"  👥 [AÑADIR MIEMBRO] Usuario '{m}' -> Equipo: {team} (Org: {org})")
                changes_detected += 1
            for m in (c_members - d_members):
                print(f"  👥 [REMOVER MIEMBRO] Usuario '{m}' <- Equipo: {team} (Org: {org})")
                changes_detected += 1
        
        # Diff Repositorios
        c_repos = set(c_org.get("repositories", {}).keys())
        d_repos = set(d_org.get("repositories", {}).keys())
        
        for repo in (d_repos - c_repos):
            print(f"  ➕ [CREAR] Repositorio: {repo} (Org: {org})")
            changes_detected += 1
        for repo in (c_repos - d_repos):
            print(f"  ➖ [ARCHIVAR] Repositorio: {repo} (Org: {org})")
            changes_detected += 1

    print("\n----------------------------------------")
    if changes_detected == 0:
        print("✨ TODO EN SINCRONÍA: El Estado Deseado (YAML) coincide con la Memoria Local.")
    else:
        print(f"⚠️ Se calcularon {changes_detected} cambios para reconciliar la infraestructura.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GiteAdmin Reconciliation Engine")
    # Activamos por defecto --dry-run para máxima seguridad 
    parser.add_argument("--dry-run", action="store_true", default=True, help="Ejecuta sin mutar el servidor ni la memoria")
    parser.add_argument("--apply", action="store_true", help="Aplica permanentemente los cambios en Gitea y guarda la memoria")
    args = parser.parse_args()

    # Si pasaron explicitamente --apply, desactivamos dry-run
    if args.apply:
        options = EngineOptions(dry_run=False)
    else:
        options = EngineOptions(dry_run=True)
        
    run_engine(options)

import os
import subprocess
import sys

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".infuser_state.json")

SCRIPTS = [
    ("Reconciler (dry-run)",
     "Shows what changes would be made without touching Gitea",
     "scripts/core_engine.py", []),
    ("Reconciler (apply)",
     "Applies pending changes to Gitea after interactive confirmation",
     "scripts/core_engine.py", ["--apply"]),
    ("Reconciler (apply + auto-approve)",
     "Applies pending changes without confirmation, intended for CI/CD",
     "scripts/core_engine.py", ["--apply", "--auto-approve"]),
    ("Export current Gitea state from gitea to local",
     "Downloads users, orgs, repos and protections from Gitea into YAML files",
     "scripts/export_state.py", []),
    ("Reset local memory",
     "Deletes .infuser_state.json and rebuilds it from current YAML files",
     None, None),
    ("Status report",
     "Generates a visual Markdown report with teams, permissions and branch protections per repo",
     "scripts/generate_report.py", []),
    ("User access report",
     "Lists every org, team and repo each user can reach, useful for offboarding audits",
     "scripts/generate_user_report.py", []),
    ("Access matrix report",
     "Generates a CSV+Markdown matrix of repos vs users with permission levels",
     "scripts/generate_matrix_report.py", []),
    ("Repository grid report",
     "Flat table with repository, description, organization, owner and users with access",
     "scripts/generate_repo_grid.py", []),
]


def reset_local_memory():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
        print("Local memory deleted (.infuser_state.json removed).")
    else:
        print("No local memory file found, nothing to delete.")

    print("Rebuilding memory from current YAML files...\n")
    subprocess.run([sys.executable, "scripts/core_engine.py", "--apply", "--auto-approve"])
    print("\nLocal memory has been reset.")


def main():
    print("========================================")
    print("  Infuser - Available Scripts")
    print("========================================\n")

    for i, (name, desc, _path, _args) in enumerate(SCRIPTS, 1):
        print(f"  {i}. {name}")
        print(f"     {desc}\n")

    print(f"  0. Exit\n")

    choice = input("Select an option: ").strip()

    if choice == "0" or choice == "":
        print("Bye.")
        return

    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(SCRIPTS):
            raise ValueError
    except ValueError:
        print("Invalid option.")
        return

    name, _desc, path, args = SCRIPTS[idx]

    if path is None:
        confirm = input("This will delete local memory and rebuild it. Continue? (y/n): ").strip().lower()
        if confirm not in ("y", "yes", "s", "si"):
            print("Cancelled.")
            return
        reset_local_memory()
        return

    print(f"\n>> Running: {name}\n")
    subprocess.run([sys.executable, path] + args)


if __name__ == "__main__":
    main()

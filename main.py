import os
import subprocess
import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

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


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_menu():
    clear_screen()
    console.print(Panel(
        "[bold white]Infuser[/bold white]\n"
        "[dim]Infrastructure as Code for Gitea / Forgejo[/dim]",
        style="bold cyan",
        padding=(1, 4),
    ))
    console.print()

    table = Table(show_header=True, header_style="bold magenta", expand=True)
    table.add_column("#", style="bold", width=4, justify="right")
    table.add_column("Action", style="bold")
    table.add_column("Description", style="dim")

    for i, (name, desc, _path, _args) in enumerate(SCRIPTS, 1):
        table.add_row(str(i), name, desc)

    table.add_row("0", "[red]Exit[/red]", "Quit the launcher")

    console.print(table)
    console.print()


def reset_local_memory():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
        console.print("[yellow]Local memory deleted (.infuser_state.json removed).[/yellow]")
    else:
        console.print("[yellow]No local memory file found, nothing to delete.[/yellow]")

    console.print("Rebuilding memory from current YAML files...\n")
    subprocess.run([sys.executable, "scripts/core_engine.py", "--apply", "--auto-approve"])
    console.print("\n[green]Local memory has been reset.[/green]")


def run_script(idx):
    name, _desc, path, args = SCRIPTS[idx]

    clear_screen()
    console.print(Panel(f"[bold]{name}[/bold]", style="bold green", padding=(0, 2)))
    console.print()

    if path is None:
        if not Confirm.ask("[yellow]This will delete local memory and rebuild it. Continue?[/yellow]", default=False):
            console.print("[red]Cancelled.[/red]")
            return
        reset_local_memory()
    else:
        subprocess.run([sys.executable, path] + args)


def main():
    while True:
        show_menu()

        choice = Prompt.ask("Select an option", default="0")

        if choice == "0":
            clear_screen()
            console.print("[bold cyan]Bye.[/bold cyan]")
            break

        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(SCRIPTS):
                raise ValueError
        except ValueError:
            console.print("[red]Invalid option.[/red]")
            console.input("\nPress Enter to continue...")
            continue

        run_script(idx)
        console.input("\n[dim]Press Enter to return to menu...[/dim]")


if __name__ == "__main__":
    main()

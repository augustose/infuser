import os
from parser import parse_all_config
from datetime import datetime

REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "reports")
REPORT_FILE = os.path.join(REPORT_DIR, "user_access_report.md")

def generate_user_report():
    os.makedirs(REPORT_DIR, exist_ok=True)
    state = parse_all_config()
    
    users = state.get("users", {})
    organizations = state.get("organizations", {})
    
    # Pre-calcular los accesos de cada usuario
    user_access = {u: {"orgs": set(), "teams": [], "repos": [], "personal_repos": [], "is_admin": False} for u in users}
    
    for org_name, org_data in organizations.items():
        teams = org_data.get("teams", {})
        repos = org_data.get("repositories", {})
        
        for team_name, t_data in teams.items():
            t_spec = t_data.get("spec", {})
            members = t_spec.get("members", [])
            for m in members:
                if m in user_access:
                    user_access[m]["orgs"].add(org_name)
                    user_access[m]["teams"].append({
                        "org": org_name,
                        "team": team_name,
                        "perm": t_spec.get("permission", "custom")
                    })
                    
                    # Si el equipo incluye todos los repositorios
                    if t_spec.get("includes_all_repositories", False):
                        for repo_name in repos.keys():
                            user_access[m]["repos"].append({
                                "org": org_name,
                                "repo": repo_name,
                                "via": f"Team: {team_name}",
                                "perm": t_spec.get("permission", "custom")
                            })

        for repo_name, r_data in repos.items():
            r_spec = r_data.get("spec", {})
            direct_collabs = r_spec.get("collaborators", {})
            for m, perm in direct_collabs.items():
                if m in user_access:
                    user_access[m]["orgs"].add(org_name)
                    # Evitamos duplicados si el loop anterior (Team) ya nos dio permiso? 
                    # Lo mostramos igual porque evidencia permisos directos superpuestos.
                    user_access[m]["repos"].append({
                        "org": org_name,
                        "repo": repo_name,
                        "via": "Direct Collab",
                        "perm": perm
                    })

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# 👥 Reporte de Accesos y Dependencias por Usuario\n\n")
        f.write(f"> **Generado el:** `{datetime.now().strftime('%B %d, %Y - %H:%M')}`\n")
        f.write("> *Este reporte detalla exactamente a qué Organizaciones, Equipos y Repositorios tiene acceso cada usuario, permitiendo auditorías de offboarding seguras.*\n\n")
        f.write("---\n\n")
        
        for u_name, u_details in users.items():
            access = user_access[u_name]
            u_spec = u_details.get("spec", {})
            is_admin = u_spec.get("is_admin", False)
            
            admin_badge = " 🛡️ **[GLOBAL ADMIN]**" if is_admin else ""
            
            f.write(f"<details>\n")
            f.write(f"  <summary><b>👤 {u_name}</b>{admin_badge}</summary>\n\n")
            f.write("  <blockquote>\n")
            
            if is_admin:
                f.write("  ⚠️ *Este usuario es administrador global y tiene acceso directo irrestricto a los recursos del servidor.*\n<br><br>\n")

            # Organizaciones
            orgs = access.get("orgs", set())
            if orgs:
                f.write(f"  <b>🏢 Organizaciones conectadas ({len(orgs)}):</b>\n")
                f.write("  <ul>\n")
                for o in orgs:
                    f.write(f"    <li>{o}</li>\n")
                f.write("  </ul>\n")
            else:
                f.write("  <i>No pertenece a ninguna organización.</i><br><br>\n")
                
            # Equipos
            teams = access.get("teams", [])
            if teams:
                f.write(f"  <b>👥 Equipos ({len(teams)}):</b>\n")
                f.write("  <ul>\n")
                for t in teams:
                    f.write(f"    <li>{t['team']} (<b>Org:</b> {t['org']}) — <code>Permiso: {t['perm'].upper()}</code></li>\n")
                f.write("  </ul>\n")
                
            # Repositorios
            repos = access.get("repos", [])
            if repos:
                f.write(f"  <b>📦 Repositorios y Proyectos ({len(repos)}):</b>\n")
                f.write("  <ul>\n")
                for r in repos:
                    f.write(f"    <li>{r['org']}/<b>{r['repo']}</b> — <i>Vía:</i> {r['via']} — <code>Permiso Efectivo: {r['perm'].upper()}</code></li>\n")
                f.write("  </ul>\n")

            # Personal
            personal_repos = u_details.get("repositories", {})
            if personal_repos:
                f.write(f"  <b>🏡 Espacio Personal (Repositorios Propios: {len(personal_repos)}):</b>\n")
                f.write("  <ul>\n")
                for r_name in personal_repos.keys():
                    f.write(f"    <li>{r_name}</li>\n")
                f.write("  </ul>\n")

            f.write("  </blockquote>\n")
            f.write("</details>\n\n")
            
    print(f"\n✨ Reporte de Offboarding de Usuarios Generado! 👉 {REPORT_FILE}")

if __name__ == "__main__":
    generate_user_report()

# Update Detection for All Entity Types

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add property-level change detection so the reconciliation engine detects updates (not just creates/deletes) for users, orgs, teams, and repos.

**Architecture:** Add a `diff_specs()` helper that compares two spec dicts and returns changed field names. Add PATCH-based update functions to `api_actions.py`. Wire update diffing into `core_engine.py` for all entity types. Dry-run output shows changed fields per entity.

**Tech Stack:** Python, requests (Gitea REST API PATCH endpoints)

---

### Task 1: Add `diff_specs` helper to `core_engine.py`

**Files:**
- Modify: `scripts/core_engine.py:1-9`

**Step 1: Add the helper function at the top of core_engine.py (after imports, before EngineOptions)**

```python
def diff_specs(current_spec, desired_spec, fields):
    """Compare two spec dicts on the given fields. Returns list of changed field names."""
    changed = []
    for f in fields:
        if current_spec.get(f) != desired_spec.get(f):
            changed.append(f)
    return changed
```

`fields` is an explicit allowlist so we only compare updatable properties (not nested structures like `members` or `collaborators` which have their own diff logic).

**Step 2: Verify syntax**

Run: `python -c "exec(open('scripts/core_engine.py').read().split('def run_engine')[0])"`
Expected: no errors

**Step 3: Commit**

```bash
git add scripts/core_engine.py
git commit -m "feat: add diff_specs helper for property-level change detection"
```

---

### Task 2: Add update API functions to `api_actions.py`

**Files:**
- Modify: `scripts/api_actions.py` (append new functions)

**Step 1: Add `update_user` function**

```python
def update_user(username, changed_spec):
    """Updates user properties via PATCH /admin/users/{username}."""
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/admin/users/{username}"
    payload = {"login_name": username, "source_id": 0}
    for key in ["email", "full_name", "active"]:
        if key in changed_spec:
            payload[key] = changed_spec[key]
    resp = requests.patch(url, headers=WRITE_HEADERS, json=payload, verify=False)
    if resp.status_code == 200:
        print(f"  [API] ✅ User {username} updated.")
        return True
    else:
        print(f"  [API] ❌ Error updating user {username}: {resp.text}")
        return False
```

Note: Gitea's PATCH `/admin/users/{username}` requires `login_name` and `source_id` in the payload.

**Step 2: Add `update_repo` function (works for both personal and org repos)**

```python
def update_repo(owner, repo_name, changed_spec):
    """Updates repository properties via PATCH /repos/{owner}/{repo}."""
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/repos/{owner}/{repo_name}"
    payload = {}
    for key in ["description", "private", "default_branch"]:
        if key in changed_spec:
            payload[key] = changed_spec[key]
    if not payload:
        return True
    resp = requests.patch(url, headers=WRITE_HEADERS, json=payload, verify=False)
    if resp.status_code == 200:
        print(f"  [API] ✅ Repository {owner}/{repo_name} updated.")
        return True
    else:
        print(f"  [API] ❌ Error updating repo {owner}/{repo_name}: {resp.text}")
        return False
```

**Step 3: Add `update_organization` function**

```python
def update_organization(org_name, changed_spec):
    """Updates organization properties via PATCH /orgs/{org}."""
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/orgs/{org_name}"
    payload = {}
    for key in ["description", "full_name"]:
        if key in changed_spec:
            payload[key] = changed_spec[key]
    if not payload:
        return True
    resp = requests.patch(url, headers=WRITE_HEADERS, json=payload, verify=False)
    if resp.status_code == 200:
        print(f"  [API] ✅ Organization {org_name} updated.")
        return True
    else:
        print(f"  [API] ❌ Error updating org {org_name}: {resp.text}")
        return False
```

**Step 4: Add `update_team` function**

```python
def update_team(org_name, team_name, changed_spec):
    """Updates team properties via PATCH /teams/{id}."""
    if not check_write_allowance(): return None
    team_id = find_team_id(org_name, team_name)
    if not team_id:
        print(f"  [API] ❌ Team {team_name} not found in {org_name}.")
        return False
    url = f"{GITEA_URL}/api/v1/teams/{team_id}"
    payload = {}
    for key in ["permission", "includes_all_repositories", "can_create_org_repo"]:
        if key in changed_spec:
            payload[key] = changed_spec[key]
    if "units_map" in changed_spec:
        payload["units_map"] = changed_spec["units_map"]
    if not payload:
        return True
    resp = requests.patch(url, headers=WRITE_HEADERS, json=payload, verify=False)
    if resp.status_code == 200:
        print(f"  [API] ✅ Team {team_name} ({org_name}) updated.")
        return True
    else:
        print(f"  [API] ❌ Error updating team {team_name}: {resp.text}")
        return False
```

**Step 5: Add `create_user_repo` function (missing — needed for personal repo creates)**

```python
def create_user_repo(username, repo_name, spec):
    """Creates a personal repository for a user via POST /admin/users/{username}/repos."""
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/admin/users/{username}/repos"
    payload = {
        "name": repo_name,
        "private": spec.get("private", True),
        "description": spec.get("description", ""),
        "default_branch": spec.get("default_branch", "main")
    }
    resp = requests.post(url, headers=WRITE_HEADERS, json=payload, verify=False)
    if resp.status_code == 201:
        print(f"  [API] ✅ Repository {username}/{repo_name} created.")
        return True
    else:
        print(f"  [API] ❌ Error creating repo {username}/{repo_name}: {resp.text}")
        return False
```

**Step 6: Add `delete_user_repo` function**

```python
def delete_user_repo(username, repo_name):
    """Deletes a personal repository."""
    if not check_write_allowance(): return False
    url = f"{GITEA_URL}/api/v1/repos/{username}/{repo_name}"
    resp = requests.delete(url, headers=WRITE_HEADERS, verify=False)
    if resp.status_code in [200, 204]:
        print(f"  [API] 🗑️ Repository {username}/{repo_name} deleted.")
        return True
    else:
        print(f"  [API] ❌ Error deleting repo {username}/{repo_name}: {resp.text}")
        return False
```

**Step 7: Verify syntax**

Run: `python -c "import scripts.api_actions"` (from project root)
Expected: no import errors

**Step 8: Commit**

```bash
git add scripts/api_actions.py
git commit -m "feat: add update/create/delete API functions for all entity types"
```

---

### Task 3: Add personal repo diffing for existing users in `core_engine.py`

**Files:**
- Modify: `scripts/core_engine.py:44-50` (after user create/delete loop)

**Step 1: Add personal repo diff block after line 50 (after user delete loop)**

Insert this block after the user delete loop and before the org diff section:

```python
    # Diff Personal Repos for existing users
    for user in desired_users.intersection(current_users):
        c_user = memory.state["users"][user]
        d_user = desired_state["users"][user]

        # Diff user properties
        c_spec = c_user.get("spec", {})
        d_spec = d_user.get("spec", {})
        user_changed = diff_specs(c_spec, d_spec, ["email", "full_name", "active"])
        if user_changed:
            update_spec = {f: d_spec[f] for f in user_changed}
            actions.append((f"  🔄 [UPDATE] User: {user} — changed: {', '.join(user_changed)}", api_actions.update_user, (user, update_spec)))

        # Diff personal repositories
        c_repos = set(c_user.get("repositories", {}).keys())
        d_repos = set(d_user.get("repositories", {}).keys())

        for repo in (d_repos - c_repos):
            actions.append((f"  ➕ [CREATE] Repository: {repo} (User: {user})", api_actions.create_user_repo, (user, repo, d_user["repositories"][repo].get("spec", {}))))

        for repo in (c_repos - d_repos):
            actions.append((f"  ➖ [DELETE] Repository: {repo} (User: {user})", api_actions.delete_user_repo, (user, repo)))

        for repo in d_repos.intersection(c_repos):
            c_repo_spec = c_user["repositories"][repo].get("spec", {})
            d_repo_spec = d_user["repositories"][repo].get("spec", {})
            repo_changed = diff_specs(c_repo_spec, d_repo_spec, ["description", "private", "default_branch"])
            if repo_changed:
                update_spec = {f: d_repo_spec[f] for f in repo_changed}
                actions.append((f"  🔄 [UPDATE] Repository: {repo} (User: {user}) — changed: {', '.join(repo_changed)}", api_actions.update_repo, (user, repo, update_spec)))
```

**Step 2: Verify with dry-run**

Run: `uv run scripts/core_engine.py`
Expected: should show update actions if YAML differs from `.infuser_state.json`

**Step 3: Commit**

```bash
git add scripts/core_engine.py
git commit -m "feat: add personal repo and user property diff detection"
```

---

### Task 4: Add org repo and org property update diffing in `core_engine.py`

**Files:**
- Modify: `scripts/core_engine.py` (within the `desired_orgs.intersection(current_orgs)` loop)

**Step 1: Add org property update detection**

At the start of the `for org in desired_orgs.intersection(current_orgs):` loop (after `d_org = ...`), add:

```python
        # Diff org properties
        c_org_spec = c_org.get("spec", {})
        d_org_spec = d_org.get("spec", {})
        org_changed = diff_specs(c_org_spec, d_org_spec, ["description", "full_name"])
        if org_changed:
            update_spec = {f: d_org_spec[f] for f in org_changed}
            actions.append((f"  🔄 [UPDATE] Organization: {org} — changed: {', '.join(org_changed)}", api_actions.update_organization, (org, update_spec)))
```

**Step 2: Add team property update detection**

Inside the `for team in d_teams.intersection(c_teams):` block, after the existing member diff logic, add:

```python
            # Diff team properties (excluding members, handled above)
            c_team_spec = c_org["teams"][team].get("spec", {})
            d_team_spec = d_org["teams"][team].get("spec", {})
            team_changed = diff_specs(c_team_spec, d_team_spec, ["permission", "includes_all_repositories", "can_create_org_repo", "units_map"])
            if team_changed:
                update_spec = {f: d_team_spec[f] for f in team_changed}
                actions.append((f"  🔄 [UPDATE] Team: {team} (Org: {org}) — changed: {', '.join(team_changed)}", api_actions.update_team, (org, team, update_spec)))
```

**Step 3: Add org repo property update detection**

After the existing org repo create/delete loops (after the `delete_org_repo` loop), add:

```python
        for repo in d_repos.intersection(c_repos):
            c_repo_spec = c_org["repositories"][repo].get("spec", {})
            d_repo_spec = d_org["repositories"][repo].get("spec", {})
            repo_changed = diff_specs(c_repo_spec, d_repo_spec, ["description", "private", "default_branch"])
            if repo_changed:
                update_spec = {f: d_repo_spec[f] for f in repo_changed}
                actions.append((f"  🔄 [UPDATE] Repository: {repo} (Org: {org}) — changed: {', '.join(repo_changed)}", api_actions.update_repo, (org, repo, update_spec)))
```

**Step 4: Verify with dry-run**

Run: `uv run scripts/core_engine.py`
Expected: should detect any property differences between YAML and `.infuser_state.json` for orgs, teams, and org repos

**Step 5: Commit**

```bash
git add scripts/core_engine.py
git commit -m "feat: add update detection for orgs, teams, and org repos"
```

---

### Task 5: End-to-end verification

**Step 1: Modify a personal repo description in YAML to test**

Edit any repo YAML (e.g. `infuser-config/users/augustose/repositories/CLIP.yaml`), change the description field temporarily.

**Step 2: Run dry-run**

Run: `uv run scripts/core_engine.py`
Expected output should include:
```
  🔄 [UPDATE] Repository: CLIP (User: augustose) — changed: description
```

**Step 3: Revert the test change and run again**

Expected: `EVERYTHING IN SYNC`

**Step 4: Final commit (if any cleanup needed)**

```bash
git add scripts/core_engine.py scripts/api_actions.py
git commit -m "feat: complete update detection for all entity types"
```

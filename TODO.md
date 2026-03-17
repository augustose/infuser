# Infuser - TODO List & Future Improvements

## 1. Engine & API Capabilities
- [ ] **Repository Updates (PUT/PATCH):** Implement the ability to update existing repositories. Currently, if a repository's `private` status, `description`, or `default_branch` changes in the YAML after creation, the engine needs to send a `PATCH` request to the Gitea API to apply these changes dynamically.
- [ ] **Team Member Synchronization:** Thoroughly test and validate the removal of members from a team (when a user is removed from a `team.yaml`). Ensure the API call successfully revokes access.
- [ ] **Resource Renaming Logic:** Handle the logic for renaming Organizations and Repositories gracefully. Currently, renaming a folder/YAML is treated as a deletion of the old resource and creation of a new one, which is dangerous for repositories. 
- [ ] **Branch Protections:** Implement the API calls to read, create, and update branch protections based on the YAML specifications.

## 2. Infrastructure & GitOps
- [ ] **Private Config Repository:** Move the `infuser-config` folder into its own isolated, private repository to ensure sensitive organizational data is not mixed with the open-source engine code.
- [ ] **CI/CD Integration:** Set up a pipeline (e.g., Gitea Actions) to automatically run `core_engine.py --dry-run` on Pull Requests to the config repository, and `--apply` when changes are merged to the main branch.

## 3. Reporting features
- [ ] Add further Dashboards or visual outputs if required by the organization's auditing team.

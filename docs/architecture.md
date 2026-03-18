# Architecture: Infuser Engine

This document defines the technical architecture specification of the Infuser engine.

## 1. Overview
Infuser is an Infrastructure as Code (IaC) engine designed to interact bidirectionally between a central Git configuration repository (`infuser-config`) and the target Gitea instance.

It is based on the principle that the YAML files hosted in the repository form the **Desired State**, and Gitea holds the **Current State**. 

## 2. Main Components

1. **State Manager / YAML Parser (Reader)**
   - Responsible for traversing the `infuser-config` folder and transforming all YAML files (`users/`, `teams/`, `repos/`, etc.) into Python data structures.

2. **Gitea API Client (Executor)**
   - A lightweight HTTP client structured across multiple scripts/classes.
   - Interacts via the `requests` library with Gitea (`/api/v1/`) using administrator authentication tokens.

3. **Reconciler (Differ Engine)**
   - The heart of the application.
   - Compares the **Desired State** (Local Memory + YAML Configuration) against the **Current State** of the API.
   - Generates an Action Plan (Create Team, Remove Access, Archive Repo, etc.).

4. **Local Memory (State / Cache)**
   - A local JSON file (`.infuser_state.json`) or a lightweight SQLite database (`state.db`).
   - Purpose: To save the signature and physical state of the last successful "apply".
   - Used for routing **Notifications** when detecting that a user/repo was specifically mutated, without needing to query the entire Gitea API on every run.

5. **Notification Module**
   - A reactive layer that dispatches events when the Reconciler detects or executes changes (e.g., "Repository Created").

## 3. Reconciliation Flow

1. **Base Trigger**: Executed via cron, manually through the CLI, or packaged as a service (Webhook trigger from GitHub/Gitea Actions).
2. **Read Config**: Parses YAMLs.
3. **Read Memory**: Parses `.infuser_state.json`.
4. **Diffing**: Calculates the required payload commands to send to Gitea.
5. **Apply API**: Calls the endpoints (`POST /orgs`, `POST /repos`, etc.).
6. **Update Memory & Notify**: Updates the local memory and invokes the notification module.

## 4. Technology Stack
- **Language:** Python
- **Package Manager:** `uv`
- **Core Libraries:** `requests`, `pyyaml`
- **Memory:** JSON file / SQLite embed.

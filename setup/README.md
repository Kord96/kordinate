# setup/

Setup scripts for kordinate — dispatched by `./setup.sh`.

## Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `lib.sh` | *(sourced by all)* | Shared utilities: colors, logging, shell RC detection, `_kc` kubectl resolver |
| `install.sh` | `./setup.sh install` | Copy framework (agents, commands, hooks, config) → `~/.claude/` |
| `profile.sh` | `./setup.sh profile` | Hydrate sensitive files from K8s or scaffold placeholders |
| `shell.sh` | `./setup.sh shell` | Configure shell RC: PATH, KORDINATE_HOME, tmux, claude alias |
| `client.sh` | `./setup.sh client` | SSH config for remote workstation access |
| `doctor.sh` | `./setup.sh doctor` | Check prerequisites, framework, profile, and connectivity |
| `bootstrap.sh` | `./setup.sh bootstrap` | Orchestrate cluster setup from scratch |
| `uninstall.sh` | `./setup.sh uninstall` | Remove kordinate-installed files from `~/.claude/` and shell |
| `hydrate.sh` | `./setup.sh hydrate` | Generate `profile/mcp.json` from `profile/config.yaml` + `pass` store |
| `export.sh` | `./setup.sh export` | Export `pass` store credentials to encrypted backup |
| `import.sh` | `./setup.sh import` | Import credentials from encrypted backup into `pass` store |

## Doctor Categories

Run a single category with `./setup.sh doctor --category <name>`.

| Category | Checks |
|----------|--------|
| `prereqs` | Required local tools: git, gh, python3, openssl, tmux, claude, curl, ssh |
| `framework` | `~/.claude/` installation: CLAUDE.md, agents, commands, hooks, settings, auth locks |
| `profile` | Sensitive config: `pass` store (`kordinate/`), profile/config.yaml, profile/mcp.json, shell RC |
| `connectivity` | External services: GitHub auth, Tailscale, K8s cluster, namespaces, secrets |

## Bootstrap Subcommands

Run with `./setup.sh bootstrap <subcommand>`.

| Subcommand | Purpose |
|------------|---------|
| `status` | Show what's set up and what isn't across all configured clusters |
| `cluster` | SSH to a node and run `setup-cluster.sh` (k3s install) |
| `rbac` | SCP `agent-rbac.yaml` and run `cluster-bootstrap` (readonly RBAC) |
| `gateway` | Prompt for Tailscale auth key, apply gateway kustomize overlay |
| `master` | Apply master kustomize (Grafana, workstation) |
| `platform` | Apply user additions from `~/.claude/profile/additions/` |
| `full` | End-to-end guided setup — all steps interactively |

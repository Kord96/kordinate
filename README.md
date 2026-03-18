# kordinate

A Claude Code operations framework for managing multi-cluster Kubernetes infrastructure. Kordinate provides a persistent workstation pod, specialized agents, safety guardrails, and a GitOps deployment pipeline — all orchestrated through Claude Code running inside a Kubernetes pod.

## Architecture

```
+-------------------------------------------------------------+
|  Workstation Pod (master namespace)                         |
|                                                             |
|  +------------------+    +-----------------------------+    |
|  |   Claude Code    |    |         Agents              |    |
|  |                  |--->|  deployer  sauron            |    |
|  |  /home/claude    |    |  designer  scribe            |    |
|  |  (PVC-backed)    |    +-----------------------------+    |
|  +------------------+                                       |
|         |                                                   |
|  +------+------------------------------------------------+  |
|  |                   Hooks (Safety Layer)                 |  |
|  |  guard-kubectl  guard-md  guard-grafana               |  |
|  |  guard-redis    guard-git auto-merge-to-dev           |  |
|  +-------------------------------------------------------+  |
|         |                                                   |
+---------|---------------------------------------------------+
          | SSH / kubectl
          |
    +-----+------+------------------+
    |            |                  |
+---v----+  +---v----+  +----------v---+
|cluster-a|  |cluster-b|  | cluster-n ...|
+---------+  +---------+  +--------------+

Remote Access: Tailscale SSH --> Workstation Pod
```

- The workstation pod runs in the `master` namespace and hosts Claude Code with a PVC-backed home directory at `/home/claude`.
- Agents operate via SSH to target clusters, with hooks enforcing safety at every boundary.
- Tailscale provides remote SSH access. Ephemeral Tailscale nodes are auto-cleaned via API on boot.

## Quick Start

### Prerequisites

- Linux machine with `git`, `gh` (authenticated), `curl`, `python3`
- Tailscale account
- GPG key (for encrypted credential store)

### Bootstrap

```bash
git clone <repo-url> kordinate
cd kordinate
# Edit profile/config.yaml with your cluster IPs, registry, namespaces
sudo ./kordinate init
```

### Additional Setup Commands

```bash
# Hydrate profile/mcp.json from profile/config.yaml (re-run after config changes)
./kordinate hydrate

# Export current profile for backup
./kordinate export

# Import a previously exported profile
./kordinate import <file>
```

## Configuration

Kordinate uses two configuration files with distinct purposes.

### config.yaml — Infrastructure

Machine-consumed configuration for cluster infrastructure. Lives at `profile/config.yaml`. Used by the bootstrap CLI, manifest templates, and the deployer agent.

```yaml
clusters:
  cluster-a:
    ip: 10.0.0.1
    nodes:
      - name: node-1
        ip: 10.0.0.2
    registry: registry.example.com:5000
    namespaces:
      - apps
      - monitoring
```

See `profile/README.md` for config structure.

### profile/topology.yaml — Operational Context

Human-oriented configuration that gives agents the context they need for decision-making. Defines application definitions, monitoring standards, and health thresholds.

```yaml
apps:
  your-app:
    cluster: cluster-a
    namespace: apps
    replicas: 3
    health:
      endpoint: /healthz
      threshold: 95
monitoring:
  standards:
    scrape_interval: 15s
    alert_threshold: 5m
```

### Credentials

Credentials are stored in a GPG-encrypted `pass` store under the `kordinate/` prefix. Agents retrieve secrets at runtime; nothing is stored in plaintext in the repository.

See [agents/README.md](agents/README.md) for agent documentation, hooks, and commands.

## Branch Model

```
session/* --> main --> test --> prod
```

- Session branches are auto-created as worktrees via `bin/claude-session`.
- The `auto-merge-to-dev.sh` hook fast-forwards `main` after each push to a session branch.
- Promotion from `main` to `test` and `test` to `prod` is manual.

## Repository Structure

```
kordinate/
├── agents/
│   ├── deployer/          # Deployment agent (manifests, commands)
│   ├── sauron/            # Monitoring & validation agent
│   ├── designer/          # Architecture review + pattern authority
│   └── scribe/            # Documentation agent
├── agent-memory/          # Per-agent knowledge
│   ├── deployer/
│   ├── sauron/
│   ├── designer/          # Includes patterns/ and patterns.md
│   └── scribe/
├── bin/                   # claude-session, tmux management
├── commands/              # Shared slash commands (boot, consult, merge)
├── hooks/                 # Safety guardrail hooks
├── setup/                 # Bootstrap helpers (lib.sh, auth-check.sh)
├── profile/               # Site-specific config (git-crypt encrypted)
│   ├── config.yaml        # Cluster infrastructure
│   ├── topology.yaml      # App topology, health thresholds
│   ├── locks/             # Agent auth locks
│   ├── keystore           # Symlink → pass store
│   ├── overlays/          # Per-stack kustomize overlays
│   └── additions/         # Extra k8s manifests
├── .mcp.json              # MCP server config (git-crypt encrypted)
├── kordinate              # Bootstrap CLI
├── settings.json          # Claude Code settings
└── CLAUDE.md              # Global agent guidelines
```

## Workstation

The workstation is a containerized Claude Code environment running as a Kubernetes pod.

- **Persistent storage**: A PVC backs `/home/claude`, preserving state across pod restarts.
- **Remote access**: Tailscale SSH connects directly to the workstation pod. Ephemeral Tailscale nodes are auto-cleaned via the Tailscale API on each boot.
- **Session management**: `tmux` auto-attaches on login, with session scripts in `bin/`.
- **Recovery**: If Tailscale SSH is unavailable, access the pod directly from a cluster node via `kubectl exec`.

## Framework vs User Content

Kordinate separates framework code (tracked in git) from user-specific configuration (git-crypt encrypted under `profile/`).

### Framework (tracked)

Everything outside `profile/`: agents, commands, hooks, `bin/`, base manifests with template placeholders, and `agent-memory/` files. This is the shared, portable layer that defines how the system operates.

### User content (profile/, git-crypt encrypted)

`config.yaml`, `topology.yaml`, kustomize overlays, agent auth locks, `mcp.json`, and the `keystore` symlink to the pass store. This is the site-specific layer that tells the framework what to operate on.

### How they connect

Agent memory files describe operational patterns and procedures in general terms. `topology.yaml` provides the concrete values — cluster names, app definitions, thresholds — that agents reference at runtime. The framework defines the "how"; the profile defines the "what" and "where."

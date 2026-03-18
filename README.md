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
cp profile/config.yaml.template profile/config.yaml
# Edit profile/config.yaml with your cluster IPs, registry, namespaces
sudo ./setup.sh
```

### Additional Setup Commands

```bash
# Hydrate profile/mcp.json from profile/config.yaml (re-run after config changes)
sudo ./setup.sh hydrate

# Export current profile for backup
sudo ./setup.sh export

# Import a previously exported profile
sudo ./setup.sh import
```

## Configuration

Kordinate uses two configuration files with distinct purposes.

### config.yaml — Infrastructure

Machine-consumed configuration for cluster infrastructure. Used by `setup.sh`, manifest templates, and the deployer agent.

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

Start from `profile/config.yaml.template` and fill in your values.

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

## Agents

Kordinate ships four specialized agents, each scoped to a specific operational domain.

| Agent    | Triggers                                           | Purpose                    |
|----------|---------------------------------------------------|----------------------------|
| deployer | `roll`, `migrate`, `stop`, `clean`, `diff`        | GitOps deployments         |
| sauron   | `add monitoring`, `health check`, `dashboard`, `run tests` | Observability & validation |
| designer | `review architecture`, `design review`            | Architecture review        |
| scribe   | `update docs`, `add api key`, `add mcp`, `write readme`   | Documentation (sole `.md` editor) |

### Consultation Protocol

Ask an agent a question without transferring full control:

```
/consult deployer "Is your-app healthy on cluster-a?"
```

### Async Messaging

Send a message to an agent via scribe relay:

```
/scribe:text sauron "Add a dashboard for your-app memory usage"
```

## Hooks (Safety Guardrails)

Hooks intercept tool calls and enforce authorization before execution.

| Hook                 | What It Guards                                                                 |
|----------------------|-------------------------------------------------------------------------------|
| `guard-kubectl.sh`   | Blocks kubectl write operations unless deployer is authorized. Hard-blocks ALL operations in the `master` namespace. |
| `guard-md.sh`        | Blocks `.md` file edits unless scribe is authorized.                          |
| `guard-grafana.sh`   | Blocks Grafana MCP calls unless sauron is authorized.                         |
| `guard-redis.sh`     | Blocks Redis MCP calls unless deployer is authorized.                         |
| `guard-git.sh`       | Guards destructive git operations (force push, reset, etc.).                  |
| `auto-merge-to-dev.sh` | Post-push hook that auto-merges session branches to main.                  |

### Token-Based Authorization

Agents authorize themselves by placing a secret token file before operating:

1. Agent copies secret to `/tmp/.<agent>-auth`
2. Hook checks for the token file and permits the operation
3. Agent removes the token file after completing work

## Commands

| Command           | Description                                          |
|-------------------|------------------------------------------------------|
| `/boot`           | Initialize the workstation environment               |
| `/consult`        | Query an agent without full handoff                  |
| `/merge`          | Merge current session branch                         |
| `/deployer:roll`  | Trigger a rolling deployment via the deployer agent  |
| `/scribe:text`    | Send an async message to an agent via scribe         |

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
│   ├── designer/          # Architecture review agent
│   └── scribe/            # Documentation agent
├── bin/                   # Shell scripts (claude-session, tmux management)
├── commands/              # Shared slash commands (boot, consult, merge)
├── hooks/                 # Safety guardrail hooks
├── setup/                 # Bootstrap helpers
├── agent-memory/          # Per-agent knowledge + patterns (tracked)
│   ├── patterns.md        # Shared pattern index
│   ├── deployer/          # Deployer agent knowledge
│   ├── sauron/            # Sauron agent knowledge + libraries/
│   ├── designer/          # Designer agent knowledge
│   └── scribe/            # Scribe agent knowledge + templates/
├── profile/               # User-specific (gitignored)
│   ├── config.yaml        # Cluster infrastructure
│   ├── config.yaml.template # Config template (tracked)
│   ├── topology.yaml      # Operational context for agents
│   ├── mcp.json           # MCP server config (generated by hydrate)
│   ├── secrets/           # Agent auth tokens
│   ├── keystore            # Symlink → ~/.password-store/kordinate/
│   ├── overlays/          # Per-cluster kustomize patches
│   └── additions/         # User platform manifests
├── .mcp.json              # Symlink → profile/mcp.json
├── settings.json          # Claude Code settings
├── setup.sh               # Bootstrap script
└── CLAUDE.md              # Global agent guidelines
```

## Workstation

The workstation is a containerized Claude Code environment running as a Kubernetes pod.

- **Persistent storage**: A PVC backs `/home/claude`, preserving state across pod restarts.
- **Remote access**: Tailscale SSH connects directly to the workstation pod. Ephemeral Tailscale nodes are auto-cleaned via the Tailscale API on each boot.
- **Session management**: `tmux` auto-attaches on login, with session scripts in `bin/`.
- **Recovery**: If Tailscale SSH is unavailable, access the pod directly from a cluster node via `kubectl exec`.

## Framework vs User Content

Kordinate separates framework code (tracked in git) from user-specific configuration (gitignored under `profile/`).

### Framework (tracked)

Everything outside `profile/`: agents, commands, hooks, `bin/`, base manifests with template placeholders, and `agent-memory/` files. This is the shared, portable layer that defines how the system operates.

### User content (profile/, gitignored)

`config.yaml`, `topology.yaml`, kustomize overlays, agent secrets, `mcp.json`, and the `keystore` symlink to the pass store. This is the site-specific layer that tells the framework what to operate on.

### How they connect

Agent memory files describe operational patterns and procedures in general terms. `topology.yaml` provides the concrete values — cluster names, app definitions, thresholds — that agents reference at runtime. The framework defines the "how"; the profile defines the "what" and "where."

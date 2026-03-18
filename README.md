# kordinate

A Claude Code operations framework for multi-cluster Kubernetes infrastructure.

## Architecture

- The workstation is a Kubernetes pod in the `master` namespace with a PVC-backed home directory at `/home/claude`, running Claude Code with 4 specialized agents.
- Agents manage remote clusters over SSH through Tailscale. Safety hooks enforce per-agent permissions.
- Each cluster runs independent dev/test/prod environments; the workstation orchestrates across all of them.

## Workflow

tmux auto-attaches on SSH login. Each project gets its own session.

```
tmux
├── kordinate (session)
│   ├── window 0 → main branch (direct)
│   ├── window 1 → session/w1-kordinate (worktree)
│   └── window 2 → session/w2-kordinate (worktree)
└── your-project (session)
    ├── window 0 → main branch
    └── window 1 → session/w1-your-project (worktree)
```

Each window runs `bin/claude-session`:
- **Open** — creates a git worktree + session branch, launches Claude Code
- **Exit** — pushes and creates a PR, or cleans up if no changes

Branch flow: `session/*` → `main` → `test` → `prod`. Session branches auto-merge to main. Promotion to test and prod is manual via the deployer agent.

## Quick Start

### Prerequisites

- Linux machine with `git`, `gh` (authenticated), `curl`, `python3`
- Tailscale account
- GPG key (for encrypted credential store)

### Bootstrap

```bash
git clone <repo-url> ~/kordinate
cd ~/kordinate
# Edit profile/config.yaml with your cluster IPs, registry, namespaces
sudo ./installer/kordinate-cli init
```

### Additional Setup Commands

```bash
# Hydrate profile/mcp.json from profile/config.yaml (re-run after config changes)
./installer/kordinate-cli hydrate

# Export current profile for backup
./installer/kordinate-cli export

# Import a previously exported profile
./installer/kordinate-cli import <file>
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

See [agents/README.md](agents/README.md) for agent documentation, hooks, and commands. See [profile/README.md](profile/README.md) for the full config structure.

## Repository Structure

```
~/kordinate/
├── kordinate/              # Claude Code framework (linked into ~/.claude/)
│   ├── agents/             # Agent definitions, commands, AGENT.md
│   │   ├── deployer/
│   │   ├── sauron/
│   │   ├── designer/
│   │   ├── scribe/
│   │   └── memory/         # Cross-project agent knowledge
│   ├── commands/            # Shared slash commands
│   ├── hooks/               # Safety guardrail hooks
│   └── profile/             # Site-specific config (git-crypt encrypted)
├── installer/               # Bootstrap + linking
│   ├── link.sh
│   ├── kordinate-cli
│   ├── lib.sh
│   └── auth-check.sh
├── bin/                     # Session + tmux helpers
└── README.md
```

## Further Reading

- [kordinate/README.md](kordinate/README.md) — Framework: agents, hooks, commands, profile
- [installer/README.md](installer/README.md) — Bootstrap CLI and linking

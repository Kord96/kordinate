# kordinate

A Claude Code operations framework for multi-cluster Kubernetes infrastructure.

## Architecture

```
                  Tailscale SSH
                       │
             ┌─────────▼──────────┐
             │  Workstation Pod    │
             │  (master namespace) │
             │                     │
             │  /home/claude (PVC) │
             │  Claude Code        │
             │  4 agents           │
             └────┬──────────┬────┘
                  │          │
           SSH + kubectl     │
          ┌───────┘          └───────┐
    ┌─────▼──────┐          ┌───────▼─────┐
    │  cluster-a  │          │  cluster-b   │
    │ dev│test│prod│          │ dev│test│prod │
    └─────────────┘          └──────────────┘
```

- Workstation runs in the `master` namespace with a PVC-backed home directory at `/home/claude`.
- Agents operate on remote clusters via SSH. Safety hooks enforce which agent can do what.
- Tailscale provides remote SSH access. Ephemeral nodes are auto-cleaned on boot.

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

See [agents/README.md](agents/README.md) for agent documentation, hooks, and commands. See [profile/README.md](profile/README.md) for the full config structure.

## Repository Structure

```
kordinate/
├── agents/                # Agent definitions (CLAUDE.md, commands/)
│   ├── deployer/          # Deployment + infrastructure
│   ├── sauron/            # Monitoring + validation
│   ├── designer/          # Architecture review + pattern authority
│   └── scribe/            # Documentation (sole .md editor)
├── agent-memory/          # Cross-project agent knowledge
│   ├── deployer/
│   ├── sauron/
│   ├── designer/          # Includes patterns/ and patterns.md
│   └── scribe/
├── bin/                   # claude-session, tmux helpers
├── commands/              # Shared slash commands (boot, consult, merge)
├── hooks/                 # Safety guardrail hooks
├── setup/                 # Bootstrap helpers
├── profile/               # Site-specific config (git-crypt encrypted)
├── .mcp.json              # MCP server config (git-crypt encrypted)
├── kordinate              # Bootstrap CLI
├── settings.json          # Claude Code settings
└── CLAUDE.md              # Global agent guidelines
```

## Further Reading

- [agents/README.md](agents/README.md) — Agent system: hooks, commands, lock-based authorization
- [profile/README.md](profile/README.md) — Site-specific configuration and layout
- [setup/README.md](setup/README.md) — Bootstrap scripts and doctor categories

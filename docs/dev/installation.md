# Installation

## Architecture

Kordinate installs in three tiers. Each tier builds on the previous.

### Tier 1: Bare Minimum

A workstation with the kordinate framework. No infrastructure agents, no monitoring, no networking. Enough to run Claude Code with guards, kords, and beorn.

**Pre-built image contains:**

- Ubuntu 24.04
- Git
- Claude Code
- pass + GPG
- Kordinate framework (pre-linked)

**Deployed:**

- k3s
- Workstation pod (pre-built image, 20Gi PVC)
- Core agents: root, scribe
- Core guards: guard-md.sh, guard-git.sh
- Core commands: /consult, /boot, /merge
- Beorn server (part of framework)

**Boot → `claude login` → working.**

### Tier 2: Default Team

Adds the infra team — specialized agents with their infrastructure dependencies.

- Deployer + sauron + designer agents
- Headscale (SSH access: `ssh claude@workstation`)
- Container registry (image builds and storage)
- Monitoring stack: Grafana, Prometheus, Loki, Alloy
- Infrastructure guards: guard-kubectl.sh, guard-grafana.sh, guard-redis.sh
- Infrastructure kords: pattern-review, monitoring-impact, defaults

### Tier 3: Addons

Project-specific services, deployed when needed.

- Postgres — project database
- Redis — project cache/queue
- Cloudflare Tunnel + DNS — public routing

## File Layout

Kordinate uses two directories:

| Path | Purpose |
|------|---------|
| `~/.kord/` | Portable kordinate format — the source of truth |
| `~/.claude/` | Runtime format — what Claude Code reads |

On install, the framework is copied from `~/.kord/` to `~/.claude/` in the format Claude Code expects. No symlinks. Claude Code works natively with real files.

Export (future): convert `~/.claude/` back to `~/.kord/` for backup, git, or sharing.

## Credentials

All credentials live in the `pass` store under `kordinate/`. `auth-check.sh` manages setup:

| Credential | Tier | Setup |
|-----------|------|-------|
| Claude | 1 | `claude login`, saved to pass |
| GPG key | 1 | Auto-generated if missing |
| Pass store | 1 | Auto-initialized |
| GitHub | 2 | `gh auth login`, token saved to pass |
| Tailscale/Headscale | 2 | Auth key saved to pass |
| Grafana | 2 | API key saved to pass |
| Cloudflare | 3 | API token saved to pass |

Credentials are portable via `kordinate export` / `kordinate import`:

```bash
# Bundle GPG key + pass store to encrypted archive
./installer/kordinate-cli export backup.gpg

# Restore on another machine
./installer/kordinate-cli import backup.gpg
```

## Current Implementation

!!! warning "Work in progress"
    The tier system is the target architecture. The current `kordinate-cli init` installs everything together (tiers 1+2). Tier separation is planned.

### Quick Start

```bash
git clone https://github.com/kord96/kordinate.git
cd kordinate
sudo ./installer/kordinate-cli init
```

After init:

```bash
# Access the workstation
kubectl -n master exec -it deploy/workstation -c workstation -- bash
# Or via SSH (after headscale connects):
ssh claude@workstation

# Log in to Claude
claude login
```

### Multi-Node

```bash
sudo ./installer/kordinate-cli join
```

Discovers reachable clusters from `config.yaml`, installs k3s agent.

### MCP Hydration

```bash
./installer/kordinate-cli hydrate
```

Generates `mcp.json` from `profile/config.yaml` and the pass store.

### After Install

Build your team:

```bash
# Add agents
/scribe:onboard myagent "manages database migrations"

# Define kords
/scribe:kord migration-review "architecture review for migration changes"
```

Or use the default team:

```bash
/deployer:bootstrap setup-namespaces
/deployer:bootstrap setup-storage
/deployer:bootstrap deploy-master <cluster>
/deployer:bootstrap deploy-gateway <cluster>
```

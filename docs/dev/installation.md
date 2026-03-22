# Installation

## Tiers

### Tier 0: Image Build

What's baked into the workstation image. Built once, never seen by the user.

- Ubuntu 24.04
- Git
- Claude Code
- pass + GPG
- Tailscale client
- tmux (auto-attach to `0-general` on login)
- Shell configured (PATH, KORDINATE_HOME, .bashrc)
- Kordinate framework pre-linked to `~/.claude/`
- Beorn server pre-installed
- Core agents: root, scribe
- Core guards: guard-md.sh, guard-git.sh
- Core commands: /consult, /boot, /merge
- Recall system (static/dynamic memory structure)
- Kord protocol (pre-consult.sh, /consult)
- Worktree sessions (claude-session, tmux-new-window)

### Tier 1: Install

What the user runs. One command, SSH access ready.

```bash
curl -sL kordinate.dev/install | sudo bash
```

```
Installing k3s... done
Deploying headscale... done
Deploying workstation... done
Installing Tailscale... done
Connecting... done

Welcome to Kordinate. Run 'claude login' to get started.
  ssh claude@workstation
```

Behind the scenes:

1. Installs k3s
2. Deploys headscale pod (self-hosted Tailscale coordination)
3. Pulls pre-built workstation image
4. Deploys workstation pod (20Gi PVC, auto-registers with headscale)
5. Installs Tailscale on the user's machine and connects to headscale
6. SSH access ready: `ssh claude@workstation`

The user runs `claude login`. Done.

### Tier 2: Default Team

From inside the workstation. Installs the infra team and its dependencies.

```
"install the default team"
```

1. Deploys container registry
2. Deploys monitoring stack (Grafana, Prometheus, Loki, Alloy)
3. Enables deployer, sauron, designer agents
4. Enables infrastructure guards (guard-kubectl.sh, guard-grafana.sh, guard-redis.sh)
5. Enables infrastructure kords (pattern-review, monitoring-impact, defaults)
6. Credential setup (GitHub, Grafana)

### Tier 3: Addons

From inside the workstation. Project-specific services.

```
/deployer:bootstrap addon postgres
/deployer:bootstrap addon redis
/deployer:bootstrap addon cloudflare
```

Each addon deploys its manifests and configures MCP.

- Postgres — project database
- Redis — project cache/queue
- Cloudflare Tunnel + DNS — public routing

## File Layout

| Path | Purpose |
|------|---------|
| `~/.kord/` | Portable kordinate format — source of truth |
| `~/.claude/` | Runtime format — what Claude Code reads |

On image build, the framework is copied from `~/.kord/` to `~/.claude/`. No symlinks. Claude Code works natively with real files.

Export (future): convert `~/.claude/` back to `~/.kord/` for backup, git, or sharing.

## Credentials

All credentials live in the `pass` store under `kordinate/`.

| Credential | Tier | Setup |
|-----------|------|-------|
| Claude | 1 | `claude login`, saved to pass |
| GPG key | 0 | Pre-installed in image |
| Pass store | 0 | Pre-initialized in image |
| Headscale | 1 | Auto-configured during install |
| GitHub | 2 | `gh auth login`, token saved to pass |
| Grafana | 2 | API key saved to pass |
| Cloudflare | 3 | API token saved to pass |

Credentials are portable:

```bash
kordinate export backup.gpg    # bundle to encrypted archive
kordinate import backup.gpg    # restore on another machine
```

## Current Implementation

!!! warning "Work in progress"
    The tier system is the target architecture. The current `kordinate-cli init` installs tiers 1+2 together. Tier separation and the `curl` installer are planned.

### Quick Start (current)

```bash
git clone https://github.com/kord96/kordinate.git
cd kordinate
sudo ./installer/kordinate-cli init
```

```bash
kubectl -n master exec -it deploy/workstation -c workstation -- bash
claude login
```

### Multi-Node

```bash
sudo ./installer/kordinate-cli join
```

### After Install

```bash
# Build your own team:
/scribe:onboard myagent "manages database migrations"
/scribe:kord migration-review "architecture review for migration changes"

# Or use the default team:
/deployer:bootstrap setup-namespaces
/deployer:bootstrap deploy-master <cluster>
```

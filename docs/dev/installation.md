# Installation

## Prerequisites

- A Linux machine (bare metal or VM) with root access
- Git, curl, Python 3

## Quick Start

```bash
git clone https://github.com/kord96/kordinate.git
cd kordinate
sudo ./installer/kordinate-cli init
```

This installs k3s, builds and deploys the workstation pod, sets up credentials, and generates a cluster config. Once complete:

```bash
# From the same machine:
kubectl -n master exec -it deploy/workstation -c workstation -- bash

# Or via SSH (after Tailscale connects):
ssh claude@workstation
```

Then link the framework and log in:

```bash
./installer/link-claude.sh
claude login
```

## What `init` Does

1. **Kubernetes** — installs k3s (or joins an existing cluster if detected)
2. **Namespace** — creates the `master` namespace
3. **Workstation image** — builds multi-arch Docker image (Ubuntu 24.04 + Claude Code + Tailscale + tools)
4. **Workstation pod** — deploys to the cluster with a 20Gi persistent volume
5. **Repo link** — clones the kordinate repo into the workstation (auto-creates a private GitHub repo if needed)
6. **Credentials** — imports GPG key and pass store if provided
7. **Auth** — runs `auth-check.sh` to verify GitHub, Tailscale, Claude credentials
8. **Config** — generates `profile/config.yaml` for the cluster

## What `link-claude.sh` Does

Links the kordinate framework into Claude Code's expected paths:

- Copies `IDENTITY.md` → `CLAUDE.md` for root and all agents
- Symlinks settings, commands, hooks, profiles, agent memory
- Installs and starts the [beorn server](../framework/beorn.md)
- Registers beorn as an MCP server

See [Linking](linking.md) for details.

## Credentials

All credentials live in the `pass` store under `kordinate/`. `auth-check.sh` handles setup:

| Credential | How it's set up |
|-----------|----------------|
| GPG key | Auto-generated if missing |
| Pass store | Auto-initialized |
| GitHub | Interactive `gh auth login`, token saved to pass |
| Tailscale | User provides auth key, saved to pass |
| Claude | `claude login`, credentials saved to pass |
| Grafana, Cloudflare | Optional, prompted during auth-check |

Credentials are portable via `kordinate export` / `kordinate import`:

```bash
# Bundle GPG key + pass store to encrypted archive
./installer/kordinate-cli export backup.gpg

# Restore on another machine
./installer/kordinate-cli import backup.gpg
```

## Multi-Node

To add a node to an existing cluster:

```bash
sudo ./installer/kordinate-cli join
```

Discovers reachable clusters from `config.yaml`, fetches the node token via SSH, installs k3s agent.

## MCP Hydration

Generates `mcp.json` from `profile/config.yaml` and the pass store:

```bash
./installer/kordinate-cli hydrate
```

Creates MCP server entries for Postgres, Redis, Grafana, and beorn based on cluster services.

## After Install

From the workstation, bootstrap the infrastructure:

```bash
/deployer:bootstrap setup-namespaces
/deployer:bootstrap setup-storage
/deployer:bootstrap deploy-master <cluster>
/deployer:bootstrap deploy-gateway <cluster>
```

Or build your own team:

```bash
# Add agents
/scribe:onboard myagent "manages database migrations"

# Define kords between agents
/scribe:kord migration-review "architecture review for migration changes"
```

# Installation

Kordinate runs on k3s. The installer pulls a pre-built workstation image and deploys it.

## Requirements

- A machine (local or remote) with SSH access
- A [Tailscale auth key](https://login.tailscale.com/admin/settings/keys) (for remote access, optional for local)
- An Anthropic API key

## Quick Start

```bash
# Local — no remote access
curl -sL https://kordinate.dev/install | bash -s -- --anthropic-key=sk-xxx

# With remote access
curl -sL https://kordinate.dev/install | bash -s -- --anthropic-key=sk-xxx --ts-key=tskey-xxx

# Remote target
curl -sL https://kordinate.dev/install | bash -s -- --remote user@server --anthropic-key=sk-xxx --ts-key=tskey-xxx
```

## What the Installer Does

1. Installs k3s (if not present)
2. Creates a Secret with provided keys
3. Applies the workstation manifest — pulls pre-built image from registry
4. Installs Tailscale client and connects (if `--ts-key` provided)

The workstation image contains:

- Claude Code
- Root + Scribe
- Framework machinery (guards, kords, recall system)
- Tailscale client

## After Install

```bash
# Local access
kubectl exec -it workstation -- bash

# Remote access (if Tailscale configured)
ssh claude@workstation
```

From the workstation, use `/scribe:onboard` to add agents and `/scribe:kord` to define kords between them.

## Tiers

| Tier | What it adds | Requires |
|------|-------------|----------|
| **Local** | k3s + workstation + core framework | A machine |
| **Remote** | Tailscale SSH access | Auth key (one-time) |
| **Team** | Additional agents, kords, guards | `/scribe:onboard` |

## Networking

Default networking is Tailscale cloud. To switch to self-hosted headscale:

```bash
kordinate network switch headscale
```

Headscale runs as a pod in the cluster. No external tokens needed after switching, but you own the maintenance.

The networking layer is pluggable — workstation and agents don't care what provides connectivity.

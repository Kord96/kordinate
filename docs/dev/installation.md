# Installation

Kordinate runs on k3s with self-hosted networking via headscale. One command, no keys, no tokens.

## Quick Start

```bash
curl -sL https://kordinate.dev/install | bash
```

```
Kordinate installed. Connect:
  ssh claude@workstation
```

First login, authenticate from inside the workstation:

```bash
claude auth login
```

## What the Installer Does

1. Installs k3s (if not present)
2. Deploys headscale pod (self-hosted Tailscale coordination)
3. Deploys workstation pod — pre-built image with Claude Code, root, scribe, framework machinery
4. Workstation auto-registers with headscale
5. Installs Tailscale client on the user's machine and connects to headscale
6. SSH is ready — `ssh claude@workstation`

No manual tokens. The installer generates auth keys via headscale's API automatically.

## Remote Target

To install on a remote machine instead of locally:

```bash
curl -sL https://kordinate.dev/install | bash -s -- --remote user@server
```

SSHs into the server, sets up k3s + headscale + workstation there, installs Tailscale locally, connects them.

## After Install

From the workstation, build your team:

- `/scribe:onboard` — add agents
- `/scribe:kord` — define kords between agents

## Networking

Default networking is self-hosted headscale — zero-friction, no external accounts needed. To switch to Tailscale cloud:

```bash
kordinate network switch tailscale --ts-key=tskey-xxx
```

The networking layer is pluggable — workstation and agents don't care what provides connectivity.

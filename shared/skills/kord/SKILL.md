---
name: kord
description: Discover and prompt daemon-backed agent pods with cached discovery and shorthand syntax like `kord opus on ...`.
---

# Kord

Use this skill for all normal agent discovery and prompting.

`kord` does three things:
- keeps a cached discovery snapshot
- refreshes discovery when stale or on demand
- resolves agent aliases and prompts the right daemon-backed pod

## Usage

List known agents:

```bash
KUBECTL_CMD="sudo k3s kubectl" /kord/workstation/home/project/kordinate/lib/scripts/kord agents
```

Show full discovery:

```bash
KUBECTL_CMD="sudo k3s kubectl" /kord/workstation/home/project/kordinate/lib/scripts/kord discover
KUBECTL_CMD="sudo k3s kubectl" /kord/workstation/home/project/kordinate/lib/scripts/kord --verbose discover
```

Prompt an agent:

```bash
KUBECTL_CMD="sudo k3s kubectl" /kord/workstation/home/project/kordinate/lib/scripts/kord augur-gpt54 on "Analyze the auth layer"
KUBECTL_CMD="sudo k3s kubectl" /kord/workstation/home/project/kordinate/lib/scripts/kord opus on "Review this design"
```

Submit a request asynchronously and let `kord` start a background watcher:

```bash
KORD_API_URL="http://kord-api.kord.svc.cluster.local:9091" \
KORD_API_KEY="replace-me" \
/kord/workstation/home/project/kordinate/lib/scripts/kord --async augur-opus on "Analyze the auth layer"
```

That returns:
- `request_id`
- `status_path`
- `log_path`

Use the unified authenticated API instead of direct Kafka/Kubernetes transport:

```bash
KORD_API_URL="http://kord-api.kord.svc.cluster.local:9091" \
KORD_API_KEY="replace-me" \
/kord/workstation/home/project/kordinate/lib/scripts/kord agents

KORD_API_URL="http://kord-api.kord.svc.cluster.local:9091" \
KORD_API_KEY="replace-me" \
/kord/workstation/home/project/kordinate/lib/scripts/kord augur-opus on "Analyze the auth layer"
```

Notes:
- bare model aliases prefer `generic-*` when present, so `opus` resolves to `generic-opus`
- exact names always win over aliases
- if discovery is older than 5 minutes, `kord` refreshes it automatically
- if `KORD_API_URL` is set, `kord` uses the authenticated HTTP API instead of the internal Kafka helper path
- `--async` submits through `kord-api`, returns immediately, and launches a background watcher that writes the final response JSON into `$CODEX_HOME/state/kord-requests/<request_id>.json`
- default discovery is compact: `name`, `capabilities`, `backend_provider`, `backend_model`, `supported_agent_params`, `active`
- use `--verbose` to include runtime and transport details such as `specialization`, `runtime`, `health_url`, `last_seen_at`, `request_topic`, and `default_working_dir`

`agent_prompt.py` remains as internal transport plumbing.
`kord` is the only public skill surface for agent discovery and prompting.

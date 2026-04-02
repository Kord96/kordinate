---
description: Dependency map for kordinate project
generated: 2026-03-28
project: kordinate
---
# Dependency Map

## Summary

Kordinate is a multi-agent orchestration platform running on k3s. A main Claude Code session delegates to 6 specialized agents (alfred, deployer, designer, sauron, scribe, warden) via kord contracts and the beorn MCP server. The platform uses a shared PVC (`kord`) for state, `pass` (GPG) for secrets, Prometheus/Loki/Grafana for observability, and Alloy for metrics/log collection. The installer CLI bootstraps k3s and a workstation pod; all subsequent infrastructure operations are agent-driven.

## Internal Module Graph

### Agent -> Skill Dependencies

| Agent | Skills | Description |
|-------|--------|-------------|
| alfred | `/config`, `/keys`, `/overlay`, `/preflight` | Profile config, credentials, kustomize overlays, preflight checks |
| deployer | `/infra` | Bootstrap, roll, stop, clean, diff, migrate, preflight, rollback |
| designer | `/detect-patterns`, `/review-api`, `/assess-debt`, `/map-dependencies`, `/architect` | Architecture review, pattern detection, dependency mapping |
| sauron | `/scan-observability`, `/diagnose-issue` | Monitoring gap scans, issue diagnosis |
| scribe | `/audit-kordinate`, `/onboard`, `/create-kord`, `/illustrate-architecture`, `/audit-skills` | Memory writes (via memory-update endpoint), kordinate health, agent onboarding, kord creation |
| warden | `/sanitize`, `/scan-breaches`, `/audit-secrets` | Secret stripping, breach scanning, secret reconciliation |
| main | (none -- orchestrator) | Delegates to all agents via kords; runs `/boot` at start |

### Kord Contracts (Inter-Agent Communication)

| Agent | Provider Kords | Description |
|-------|---------------|-------------|
| alfred | `alfred-default`, `config-route`, `environment-ready`, `preflight-check` | Config routing, environment readiness, preflight |
| deployer | `deployer-default`, `cluster-topology`, `deployment-status`, `setup-secrets` | Deployment ops, topology, secrets setup |
| designer | `designer-default`, `concept-lookup`, `pattern-review`, `project-analysis` | Pattern review, concept lookup |
| sauron | `sauron-default`, `dashboard-catalog`, `monitoring-impact` | Dashboard catalog, monitoring impact analysis |
| scribe | `scribe-default`, `audit`, `create-kord`, `doc-check`, `onboard`, `remember` | Memory writes, audits, onboarding |
| warden | `warden-default`, `pre-commit-scan`, `sanitize` | Pre-commit scanning, content sanitization |

### Agent -> Hook Dependencies

| Hook | Triggered By | Matcher | Purpose |
|------|-------------|---------|---------|
| `guard.sh` | PreToolUse | `Write\|Edit\|Bash`, `mcp__grafana` | Enforces domain boundaries: scribe owns .kord/ writes, deployer owns kubectl/git-push, sauron owns Grafana. Field-level ACL on config.yaml via config-acl.yaml + Python |
| `agent-memory.sh` | PreToolUse | `Agent` | Regenerates MEMORY.md before spawning a subagent. Combines shared memory + instructions + static knowledge + kord discovery. Hash-based caching |
| `worktree-push.sh` | PostToolUse | `Bash` | After git push from a worktree on session/* branch, merges to main (fast-forward or rebase) |

### Agent -> Library Dependencies

| Library | Used By | Purpose |
|---------|---------|---------|
| `lib/cache.sh` | `agent-memory.sh`, `kord-expiry.sh` | Hash-based cache invalidation (md5sum of file trees) |
| `lib/kord-expiry.sh` | beorn (kord tool) | Two-stage kord cache expiry: change magnitude + age decay scoring |
| `lib/mcp-agent-server/server.js` | agent-factory pod, beorn | MCP server: `delegate`, `kord`, `status` tools. Spawns Claude Code with agent identity |
| `shared/auth-protocol.md` | All agents (preloaded) | `/authenticate` protocol for guarded operations |
| `shared/credentials-protocol.md` | All agents (preloaded) | Credential handling protocol |
| `shared/memory-protocol.md` | All agents (preloaded) | Memory management protocol |
| `profile/config.yaml` | installer, kord-hydrate, deployer, alfred, guard.sh | Central cluster config (IPs, ports, services, namespaces) |
| `profile/config-acl.yaml` | guard.sh | Field-level access control for config.yaml edits |
| `profile/.mcp.json` | Claude Code runtime | MCP server definitions (git-crypt encrypted) |
| `KORD.json` | beorn (agent discovery), guard.sh (curated check), scribe | Catalog of all agents, memory files, and kord entries |
| `settings.json` | Claude Code runtime | Hook registration, env vars, effort level |

### Beorn -> Agent Connection

Beorn (`lib/mcp-agent-server/server.js`) connects to agents by:
1. Discovering agent names from `KORD.json` (fallback: scanning `agents/` directory)
2. Loading `IDENTITY.md` + all `memory/*.md` files as a system prompt
3. Running `agent-memory.sh` hook to regenerate dynamic memory
4. Spawning `claude --print --dangerously-skip-permissions --system-prompt <prompt> <user-message>`
5. For kord requests: looking up `agents/*/kords/<name>/contract.md`, checking expiry via `kord-expiry.sh`, caching results

## External Dependencies

### Node.js (npm)

| Package | Version | Purpose |
|---------|---------|---------|
| `@modelcontextprotocol/sdk` | ^1.27.1 | MCP protocol server SDK (StreamableHTTPServerTransport) |
| `express` | ^5.1.0 | HTTP server for MCP endpoint and health checks |
| `zod` | ^4.3.6 | Schema validation for MCP tool parameters |
| `@anthropic-ai/claude-code` | latest (global) | Claude Code CLI -- installed in workstation + agent-factory images |

### Python (System)

| Package | Version | Purpose |
|---------|---------|---------|
| `python3` | 3.x (system) | YAML parsing in installer, config-acl evaluation in guard.sh, kord-expiry scoring |
| `python3-yaml` (PyYAML) | system | YAML parsing for config.yaml in installer and hooks |

### Python (CI/Docs)

| Package | Version | Purpose |
|---------|---------|---------|
| `mkdocs-material` | latest | Documentation site build (GitHub Pages workflow) |

### CLI Tools (System)

| Tool | Used By | Purpose |
|------|---------|---------|
| `kubectl` | deployer, installer, guard.sh | Kubernetes cluster management |
| `git` | all agents, worktree-push.sh, claude-session, installer | Version control, worktree management |
| `git-crypt` | profile/.mcp.json | Encrypts sensitive config files in-repo |
| `pass` | alfred, warden, kord-hydrate, kord-export/import | GPG-encrypted credential store |
| `gpg` / `gnupg` | pass dependency, kord-export/import | Encryption for credentials and exports |
| `tmux` | workstation entrypoint, bin/tmux-*, claude-session | Terminal multiplexing for persistent sessions |
| `ssh` / `sshd` | installer (connect), workstation | Cluster access, Cloudflare tunnel SSH |
| `cloudflared` | installer (connect), workstation sidecar | Cloudflare tunnel for external SSH access |
| `tailscale` | workstation, gateway pod | Tailnet mesh networking for internal access |
| `curl` | installer, Dockerfiles | HTTP client for k3s install, package downloads |
| `jq` | guard.sh, hooks | JSON parsing in shell scripts |
| `python3` | guard.sh, agent-memory.sh, kord-expiry.sh, installer | YAML/JSON parsing, ACL evaluation, staleness scoring |
| `md5sum` | cache.sh, config-reloader sidecars | Hash-based cache invalidation |
| `docker` / `docker buildx` | installer (init) | Multi-arch image builds for workstation |
| `k3s ctr` | installer (init) | Image import to k3s containerd |
| `gh` (GitHub CLI) | workstation image (pinned v2.67.0) | GitHub operations |
| `helm` | (available but not directly referenced in base manifests) | Potential K8s package management |
| `node` / `npm` | agent-factory, workstation | Runtime for beorn MCP server, Claude Code |

### Container Images

| Image | Used By | Purpose |
|-------|---------|---------|
| `ubuntu:24.04` | workstation Dockerfile | Base for interactive workstation |
| `node:22-alpine` | agent-factory Dockerfile | Slim base for beorn MCP server |
| `python:3.12-alpine` | log-puller, loki-federate Dockerfiles | Base for Python utilities |
| `prom/prometheus:v2.51.0` | prometheus deployment | Metrics storage and querying |
| `grafana/loki:3.0.0` | loki deployment | Log aggregation |
| `grafana/grafana:11.4.0` | grafana deployment | Visualization and dashboards |
| `grafana/grafana-image-renderer:latest` | grafana pod (sidecar) | Dashboard image rendering |
| `grafana/alloy:v1.5.1` | alloy deployments (monitor + master) | Metrics scraping and log tailing |
| `minio/minio:latest` | minio deployment | S3-compatible object storage for Loki |
| `ghcr.io/tailscale/tailscale:latest` | gateway pod | Tailnet identity for cluster |
| `cloudflare/cloudflared:latest` | workstation pod (sidecar) | Cloudflare tunnel for external access |
| `caddy:2-alpine` | workstation pod (sidecar) | Reverse proxy for HTTP services |
| `busybox:1.36` | config-reloader sidecars, init containers | Config reload, permission fixing |
| `alpine/git` | kord-init job | PVC directory structure initialization |
| `registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.12.0` | kube-state-metrics | K8s object state as Prometheus metrics |
| `prom/node-exporter:v1.8.2` | node-exporter DaemonSet | Host-level metrics (CPU, memory, disk) |

## Infrastructure Dependencies

### Kubernetes Namespaces

| Namespace | Purpose |
|-----------|---------|
| `gateway` | Tailscale gateway, MinIO |
| `monitor` | Alloy collector, kube-state-metrics, node-exporter |
| `master` | Workstation, agent-factory, Grafana, Prometheus, Loki, docs, Alloy (federation) |
| `dev` | Development workloads |
| `test` | Testing workloads |
| `prod` | Production workloads |

### Kubernetes Services

| Service | Namespace | Port | Depends On | Purpose |
|---------|-----------|------|------------|---------|
| workstation | master | N/A (pod) | kord PVC, cloudflared-tunnel secret, Caddy ConfigMap | Interactive Claude Code session with tmux |
| agent-factory | master | 3100 | kord PVC, beorn (server.js), KEDA (optional) | MCP server that spawns agents on demand |
| prometheus | master | 9090 | prometheus-config ConfigMap | Metrics TSDB, remote write receiver |
| loki | master | 3100 | loki-config ConfigMap, loki-data PVC | Log aggregation with TSDB schema |
| grafana | master | 3000 | grafana-data PVC, grafana-provisioning CMs, Prometheus, Loki | Visualization dashboards |
| minio | gateway | 9000/9001 | minio-data PVC, minio-credentials secret | S3-compatible storage for Loki chunks |
| gateway (tailscale) | gateway | TCP proxy 9090/9000 | gateway-tailscale secret | Exposes Prometheus + MinIO on tailnet |
| alloy (monitor) | monitor | N/A | alloy-config CM, Prometheus (remote write), Loki (push) | Per-cluster metrics scraper + log tailer |
| alloy (master) | master | N/A | alloy-config CM, log-puller sidecar, gateway-registry CM | Federation: pulls metrics/logs from gateway clusters |
| kube-state-metrics | monitor | 8080 | K8s API | Exposes K8s object state as Prometheus metrics |
| node-exporter | monitor | 9100 (DaemonSet) | Host /proc, /sys | Host-level metrics |
| docs | master | 4321 (port 80 svc) | kord PVC | Astro Starlight documentation site |

### RBAC

| Role | Scope | Used By | Permissions |
|------|-------|---------|-------------|
| agent-readonly | ClusterRole | workstation SA, agent-factory SA | Read all resources, pod exec, pod logs, metrics |
| alloy | ClusterRole | alloy SA (monitor) | Read nodes, pods, services, endpoints, metrics |
| kube-state-metrics | ClusterRole | kube-state-metrics SA | List/watch core + apps + batch resources |
| gateway | Role (gateway ns) | gateway SA | Secrets CRUD, events |

### Inter-Service Communication

```
Alloy (monitor) --remote-write--> Prometheus (master:9090)
Alloy (monitor) --loki-push-----> Loki (master:3100)
Alloy (master)  --remote-write--> Prometheus (master:9090)
Alloy (master)  <--log-puller---- Gateway clusters (Loki API)
Gateway (TS)    --TCP-proxy------> Prometheus (monitor:9090)
Gateway (TS)    --TCP-proxy------> MinIO (gateway:9000)
Grafana         --query----------> Prometheus (master:9090)
Grafana         --query----------> Loki (master:3100)
KEDA            --query----------> Prometheus (master:9090)  [agent-factory scaling]
Workstation     --caddy-proxy----> Grafana, docs (localhost in pod network)
Cloudflared     --tunnel---------> Workstation SSH (localhost:2222)
Tailscale (ws)  --SSH------------> Workstation (port 22)
```

### Storage / State

| Store | Type | Used By | Purpose |
|-------|------|---------|---------|
| `kord` PVC (20Gi RWX) | Longhorn PVC | workstation, agent-factory, docs, kord-init | Primary system volume: `/kord/pass/`, `/kord/gnupg/`, `/kord/ssh/`, `/kord/kordinate/`, `/kord/projects/`, `/kord/claude-home/` |
| `grafana-data` PVC (5Gi) | PVC | grafana | Grafana databases and plugin storage |
| `loki-data` PVC (50Gi) | PVC | loki | Log chunks, TSDB index, compactor data |
| `minio-data` PVC (10Gi) | PVC | minio | S3 object storage for Loki federation |
| `prometheus-data` | emptyDir (base) | prometheus | Metrics TSDB (overlays may use PVC) |
| `pass` store | GPG-encrypted files on kord PVC | alfred, warden, kord-hydrate | Credentials: API keys, tokens, passwords |
| `git` repos | Directories on kord PVC | all agents | Source code, kordinate runtime, worktrees |
| `KORD.json` | JSON file | beorn, scribe, guard.sh | Agent/memory/kord catalog |
| `config.yaml` | YAML file | installer, deployer, alfred, kord-hydrate | Cluster topology, service endpoints |
| `MEMORY.md` (dynamic) | Generated .md files | agent-memory.sh -> each agent | Per-agent combined memory (shared + instructions + static + kords) |
| Kord cache (`data-*.md`, `.valid`, `.snapshot`) | Files in kords/ dirs | beorn, kord-expiry.sh | Cached kord responses with hash-based expiry |
| tmux layout | JSON on kord PVC | tmux-save, tmux-restore | Persistent tmux session state across pod restarts |
| `.mcp.json` | git-crypt encrypted | Claude Code runtime | MCP server endpoint definitions |

### Secrets

| Secret | Namespace | Source | Used By |
|--------|-----------|--------|---------|
| `cloudflared-tunnel` | master | pass store (deployed at deploy time) | workstation (cloudflared sidecar) |
| `minio-credentials` | gateway | pass store | minio deployment |
| `gateway-tailscale` | gateway | Tailscale auth key | gateway (tailscale container) |

## Dependency Risks

| Risk | Severity | Description |
|------|----------|-------------|
| Single PVC (kord) shared across pods | HIGH | All pods (workstation, agent-factory, docs) share the 20Gi `kord` PVC. Longhorn RWX failure or corruption affects all services simultaneously. No backup automation visible in manifests. |
| GPG/pass as sole credential store | MEDIUM | All secrets flow through `pass` on the kord PVC. Loss of GPG key or PVC data loses all credentials. `kord-export`/`kord-import` exist but require manual execution. |
| git-crypt for .mcp.json | MEDIUM | MCP server configs are git-crypt encrypted. If git-crypt key is lost or not initialized, Claude Code cannot discover MCP servers. |
| No container image pinning | MEDIUM | Several images use `latest` tags (minio, cloudflared, tailscale, grafana-image-renderer). Upstream breaking changes could affect stability. |
| KEDA optional dependency | LOW | Agent-factory KEDA ScaledObject is ignored if KEDA is not installed, leaving replicas at 0. Manual scaling is required without KEDA. |
| Python3 required in shell paths | LOW | `guard.sh`, `agent-memory.sh`, `kord-expiry.sh`, and installer all shell out to `python3` for YAML/JSON parsing. Missing python3 silently fails some code paths. |
| Single Prometheus instance | MEDIUM | No HA/federation for Prometheus itself. Base manifest uses emptyDir for data (lost on pod restart). Overlays may fix this. |
| Workstation self-modification block | LOW | Guard blocks `kubectl` commands targeting the workstation deployment from inside the pod, but the check is regex-based and could be bypassed with creative command construction. |

## ASCII Dependency Graph

```
+=====================================================================+
|                        KORDINATE PLATFORM                           |
+=====================================================================+

  +---------+    delegates    +------------------------------------------+
  |  main   | ------------->  | alfred | deployer | designer | sauron    |
  | (orch)  |    via kords    | scribe | warden                         |
  +---------+                 +------------------------------------------+
       |                           |         |         |
       | settings.json             | hooks   | skills  | kords
       | (hook registration)       v         v         v
       |                  +--------------------------------------+
       |                  | guard.sh  | agent-memory.sh          |
       |                  | worktree-push.sh                     |
       |                  +--------------------------------------+
       |                           |
       |                    uses   v
       |                  +--------------------------------------+
       |                  | lib/cache.sh | lib/kord-expiry.sh    |
       |                  +--------------------------------------+
       |
       |  MCP (StreamableHTTP)
       v
  +------------------+     spawns claude --print     +-------------+
  | beorn            | ----------------------------> | Agent pods  |
  | (agent-factory)  |     with IDENTITY.md +        | (ephemeral) |
  | server.js        |     MEMORY.md as system       +-------------+
  | port 3100        |     prompt
  +------------------+
       |
       | reads
       v
  +------------------+
  | KORD.json        |  agent catalog + memory index
  | IDENTITY.md      |  per-agent identity
  | memory/*.md      |  static + dynamic knowledge
  | kords/*/         |  contract.md + data cache
  +------------------+

  +=====================================================================+
  |                     KUBERNETES (k3s)                                |
  +=====================================================================+

  MASTER namespace                    GATEWAY namespace
  +----------------------------+      +---------------------------+
  | workstation (pod)          |      | gateway (tailscale)       |
  |  +- claude (main)         |      |  TCP proxy:               |
  |  +- cloudflared (tunnel)  |      |   9090 -> prometheus      |
  |  +- caddy (reverse proxy) |      |   9000 -> minio           |
  |                            |      +---------------------------+
  | agent-factory (beorn)      |      | minio                     |
  |  +- KEDA scaled 0->1      |      |  S3 storage for Loki      |
  |                            |      |  PVC: minio-data (10Gi)   |
  | prometheus (:9090)         |      +---------------------------+
  | loki (:3100)               |
  | grafana (:3000)            |      MONITOR namespace
  |  +- image-renderer (:8081) |      +---------------------------+
  | alloy (federation)         |      | alloy (collector)         |
  |  +- log-puller sidecar     |      |  -> remote-write to       |
  | docs (:4321)               |      |     prometheus            |
  +----------------------------+      |  -> loki push             |
                                      | kube-state-metrics (:8080)|
  Shared: kord PVC (20Gi RWX)        | node-exporter (:9100 DS)  |
  /kord/pass, /kord/gnupg,           +---------------------------+
  /kord/kordinate, /kord/projects,
  /kord/claude-home

  +=====================================================================+
  |                     DATA FLOW                                       |
  +=====================================================================+

  alloy (monitor) --metrics--> prometheus (master)
  alloy (monitor) --logs-----> loki (master)
  alloy (master)  --metrics--> prometheus (master)  [federated]
  grafana --------queries----> prometheus + loki
  keda -----------queries----> prometheus  [scaling decisions]
  workstation ----caddy------> grafana, docs  [HTTP proxy]
  cloudflared ----tunnel-----> workstation SSH
  tailscale -----mesh-------> workstation, gateway
  pass ----------GPG---------> credentials (PVC)
  git -----------worktrees---> session branches -> main (auto-merge)
```

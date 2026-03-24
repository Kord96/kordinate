# Feature Inventory

Complete inventory of everything in kordinate — implemented and planned. Use this to plan installation tiers and identify gaps.

## Framework Core

### Agents

| Agent | Identity | Commands | Instructions | Memory (static) | Memory (dynamic) |
|-------|----------|----------|-------------|-----------------|-----------------|
| general | IDENTITY.md | /boot, /consult, /merge | — | — | consultations/ |
| scribe | IDENTITY.md | onboard, kord, add-mcp, update-agent-docs, update-project-docs, update-subagent-memory, audit-docs | workflow.md, tools.md | templates/ | MEMORY.md, operational_notes.md |
| deployer | IDENTITY.md | bootstrap, roll, stop, clean, diff, migrate-workstation | auth.md, tools.md | infra.md, migration.md, troubleshooting.md | operational_notes.md, infra-monitoring.md |
| sauron | IDENTITY.md | scan, diagnose | auth.md, workflow.md, tools.md | monitoring.md, logging.md, manifest.yaml | grafana_renderer.md, operational_notes.md |
| designer | IDENTITY.md | detect-patterns | workflow.md, tools.md | patterns/ (18 patterns), libraries/ (4 libs), app-contract.md | MEMORY.md |

### Guards

| Guard | Protects | Agent |
|-------|----------|-------|
| guard-md.sh | .md file edits | scribe |
| guard-git.sh | Git operations | all |
| guard-kubectl.sh | kubectl writes | deployer |
| guard-grafana.sh | Grafana API (Edit/Write, Bash, MCP) | sauron |
| guard-redis.sh | Redis MCP | deployer |

### Hooks

| Hook | Trigger | Purpose |
|------|---------|---------|
| agent-memory.sh | PreToolUse (Agent) | Regenerate agent MEMORY.md before spawning |
| auto-merge-to-dev.sh | PostToolUse (Bash) | Fast-forward main after push |

### Kords

| Kord | Requester | Provider |
|------|-----------|----------|
| deployer-default | any | deployer |
| sauron-default | any | sauron |
| designer-default | any | designer |
| scribe-default | any | scribe |
| pattern-review | deployer, sauron | designer |
| monitoring-impact | deployer | sauron |

### Skills

| Skill | Scope | Purpose |
|-------|-------|---------|
| /boot | general | Catch up on parent context + code changes |
| /consult | general | Invoke agent via kord protocol |
| /merge | general | Merge session branch forward |
| /scribe:onboard | scribe | Add new agent to team |
| /scribe:kord | scribe | Define new kord |
| /scribe:add-mcp | scribe | Add MCP server entry |
| /scribe:update-agent-docs | scribe | Update agent documentation |
| /scribe:update-project-docs | scribe | Update project documentation |
| /scribe:update-subagent-memory | scribe | Update agent memory |
| /scribe:audit-docs | scribe | Audit docs for consistency |

### Configuration

| File | Purpose |
|------|---------|
| settings.json | Hook configuration (guards, auto-merge, memory regen) |
| profile/.mcp.json | MCP server registration (playwright, beorn) |
| profile/keybindings.json | Claude Code key bindings |
| profile/config.yaml | Cluster configuration (IPs, namespaces, services) |
| agents/registry.yaml | Machine-readable agent list for beorn |

### Libraries

| File | Purpose |
|------|---------|
| lib/cache.sh | Hash-based cache check/store/invalidate |
| lib/mcp-agent-server/server.js | Beorn MCP server (Express + MCP SDK) |

## Installer

| Script | Purpose |
|--------|---------|
| kordinate-cli | Bootstrap CLI (init, join, hydrate, export, import) |
| link-claude.sh | Copy framework to ~/.claude/, install beorn, register MCP |
| setup-shell.sh | PATH, KORDINATE_HOME, tmux config |
| auth-check.sh | Credential setup (GPG, pass, GitHub, Tailscale, Claude, Grafana) |
| lib.sh | Shared utilities (logging, kubectl resolution) |

## Bin

| Script | Purpose |
|--------|---------|
| claude-session | Worktree-based Claude sessions with auto-PR |
| tmux-session.bash | Auto-attach on SSH, default session, tmux.conf generation |
| tmux-new-window | Route new tmux windows to repo-named sessions |

## Kubernetes Manifests

### Gateway Namespace

| Manifest | Purpose |
|----------|---------|
| gateway.yaml | Gateway Tailscale pod (cluster front door) |
| workstation.yaml | Workstation deployment + PVC |
| beorn.yaml | Beorn MCP server deployment + service |
| ingress.yaml | Ingress configuration |
| minio.yaml | MinIO object storage |
| workstation/Dockerfile | Workstation image |
| workstation/entrypoint.sh | Workstation boot script |
| beorn/entrypoint.sh | Beorn boot script |

### Master Namespace

| Manifest | Purpose |
|----------|---------|
| prometheus.yaml | Master Prometheus (30d retention) |
| loki.yaml | Master Loki (30d retention) |
| grafana.yaml | Grafana + datasources |
| alloy.yaml | Master Alloy collector |
| gateway-registry.yaml | Container registry |
| dashboards/ | Dashboard provisioning + JSON definitions |
| log-puller/ | Loki federation sidecar (Python + Dockerfile) |

### Monitor Namespace

| Manifest | Purpose |
|----------|---------|
| prometheus.yaml | Cluster Prometheus |
| loki.yaml | Cluster Loki |
| alloy.yaml + alloy-config.yaml | Cluster Alloy + config |
| node-exporter.yaml | Host metrics |
| kube-state-metrics.yaml | K8s state metrics |
| loki-federate/ | Loki federation script (Python + Dockerfile) |

### RBAC

| Manifest | Purpose |
|----------|---------|
| agent-rbac.yaml | Agent readonly service account |
| agent-scaler-rbac.yaml | Workstation → beorn scaling permissions |

### Bootstrap

| File | Purpose |
|------|---------|
| namespaces.yaml | Namespace definitions |
| setup-cluster.sh | Cluster bootstrap script |

## Agent Utilities

| File | Agent | Purpose |
|------|-------|---------|
| deployer/postgres.py | deployer | PostgreSQL operations |
| sauron/grafana_api.py | sauron | Grafana dashboard push/pull |
| sauron/metrics_pusher.py | sauron | Metrics pushing |

## Designer Knowledge Base

### Patterns (18)

circuit-breaker, sidecar, api-gateway, stream-to-store, event-sourcing, etl, retry, cqrs, hexagonal, service-manager, ddd, bulkhead, choreography, saga, backpressure, plugin

### Libraries (4)

klog, orchestrator, stoik, nokrashi-tools

## CI/CD

| File | Purpose |
|------|---------|
| .github/workflows/deploy-docs.yml | Deploy mkdocs to GitHub Pages on push to main |

## Documentation Site

37 pages across: framework (5), infra (2), reference (agents, linking, source-map, patterns, libraries), dev (installation, linking, sessions)

## Referenced but Not Implemented

| Feature | Where Referenced |
|---------|-----------------|
| Gemini MCP validation | designer IDENTITY.md |
| Pattern TODOs (examples, implementation guides) | 18 pattern files in designer memory |
| Project-level agent dirs (`<project>/<agent>/`) | linking docs, shared MEMORY.md |
| ~/.kord/ portable format | installation docs (planned) |
| Tier-based installation | installation docs (planned) |

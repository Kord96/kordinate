# Platform Health Checklist

Run through this checklist to verify the kordinate platform is healthy. Each section can be checked independently. Report findings as PASS, WARN, or FAIL with details.

## Runtime PVC (/kord/)

### Agent directories
For each agent (augur, charon, sauron, alfred, warden):
- `/kord/agents/<name>/` exists
- Has `.claude/settings.json`
- Has `.model` containing one of: opus, sonnet, haiku
- Has `identity.md` (not empty)
- Has `memory/global/` (not empty for augur/charon/sauron)
- Has `memory/projects/` directory
- Has `skills/` with at least one symlinked skill

### Agent-specific
- Augur: `memory/global/concepts/` has ~267 subdirectories
- Augur: `memory/global/concepts.md` and `memory/global/anti-patterns.md` exist
- Alfred/warden: memory/global/ may be minimal (scratchpad only) — not a failure

### Team directory
- `/kord/team/memory/global/` exists
- Contains `team.md` with current agent roster (5 agents, no scribe)
- Contains `memory-protocol.md`
- Contains `credentials-protocol.md`

### No stale state
- No `/kord/agents/scribe/` directory
- No `/kord/agents/shared/` directory
- No `/kord/agents/*/CLAUDE.md` files
- No `/kord/agents/*/shared` symlinks
- No `/kord/agents/*/memory/local-global/` directories
- No `/kord/agents/*/memory/shared/` directories
- No flat .md files directly in `/kord/agents/*/memory/` (should all be in `global/`)

## Data PVC (/data/)

- `/data/repos/kordinate/` exists and is a git repo
- `git -C /data/repos/kordinate status` shows clean working tree (or known changes)
- Repo is on `main` branch and reasonably up to date
- Skills symlinks in `/kord/agents/*/skills/` resolve to paths under `/data/repos/kordinate/`

## Kubernetes Resources

### Secrets
- `anthropic-api` Secret exists in the target namespace with key `api-key`

### PVCs
- `kord` PVC exists, is bound, and has sufficient free space
- `data` PVC exists, is bound, and has sufficient free space

### Operators
- KEDA operator is running (`kubectl get pods -n keda-system`)
- Strimzi Kafka operator is running (if using Strimzi)

## Platform Pods

### Kafka
- Kafka cluster is running in KRaft mode
- Broker is reachable at the configured address
- Topics exist:
  - `agent.augur`, `agent.charon`, `agent.warden`, `agent.sauron`, `agent.alfred`
  - `agent.dlq`
  - `memory.updates.augur`, `memory.updates.charon`, `memory.updates.warden`, `memory.updates.sauron`, `memory.updates.alfred`

### Agent Pods
- KEDA ScaledObjects exist for all 5 agents
- Standby pods are running per scaling config (augur: 1, charon: 1, warden: 1, sauron: 0, alfred: 0)
- Running pods pass readiness probe (`/health` on :9090)
- Each pod mounts both `kord` (rw) and `data` (ro) PVCs
- Claude process is alive inside running pods

### Scribe Pods
- One scribe deployment per agent (5 total)
- Each has replicas=1, strategy=Recreate
- Pods are running and consuming from `memory.updates.<agent>` topics
- ANTHROPIC_API_KEY env var is set (from Secret)

## End-to-End Flow

### Job delegation
- Publish a simple job to `agent.charon` with at least `{ prompt, reply_to }`
- `reply_to` is required
- Response contains `status` and `output`
- If reflection is requested, response may include `reflection.project` and/or `reflection.general`
- The reply topic receives the result message with matching `correlation_id` when provided

### Memory pipeline
- Agent reflection produces a curl to `:9090/memory-update`
- The `/memory-update` endpoint returns 200 ("queued")
- Message appears on `memory.updates.<agent>` Kafka topic
- Scribe consumes the message and writes to `memory/global/` or `memory/projects/<project>/`
- On next job, daemon detects the hash change and reports it to Claude

### Read-only enforcement
- Agent pods cannot write to `/data/repos/` (read-only mount)
- Memory intercept hook blocks direct writes to `memory/` paths
- Memory intercept hook blocks writes to `.claude/` paths on pods

## Post-Deploy Verification

After deploying a change via `deploy-runtime.sh`:
- New memory files appear in `/kord/agents/*/memory/global/`
- Updated team protocols appear in `/kord/team/memory/global/`
- Running pods detect changes on their next job (hash-based detection)
- Skills symlinks still resolve correctly

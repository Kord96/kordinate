# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Kordinate is a framework for running specialized AI agents as Kubernetes pods with persistent Claude sessions. Each agent runs the `openclaude` CLI in `--input-format stream-json` mode, managed by `agent-pod-daemon`. The daemon bridges Kafka jobs to Claude's stdin/stdout and publishes results back to Kafka.

## Running the Services

```bash
# Agent pod daemon (per-agent, needs AGENT_NAME env)
cd lib/agent-pod-daemon && AGENT_NAME=charon node daemon.js
```

Key environment variables for the daemon:
- `AGENT_NAME` — required; selects which Kafka topic (`agent.<AGENT_NAME>`) to consume
- `AGENT_PROJECT_DIR` — agent working dir, defaults to `/runtime/<AGENT_NAME>`
- `AGENT_STATE_DIR` — persistent state dir, defaults to `/kord/<AGENT_NAME>`
- `KAFKA_BROKERS` — defaults to `kafka-kafka-bootstrap.dev.svc.cluster.local:9092`

## Deployment Scripts

```bash
# Deploy agent runtime files (memory, identity, skills) from repo → /runtime/<agent>/
lib/scripts/deploy-runtime.sh <agent-name|all>

# Generate agent bundle (AGENT.md static preload)
lib/scripts/generate-agent-bundle.py <agent>

# Generate platform kustomization overlay
lib/scripts/generate-platform-kustomization.py

# Toggle an agent's backend profile
lib/scripts/toggle-profile.sh <agent> <backend-name>
```

## Architecture

### Job Routing

Each agent has a single Kafka inbox: `agent.<name>`. Messages are routed there directly — no HTTP router, no shared result topic.

The daemon consumes `agent.<AGENT_NAME>` one message at a time (pauses/resumes the consumer around each job). When a job has a `reply_to` field, the daemon publishes the result to that topic. Agent-to-agent delegation sets `reply_to: agent.<sender>`.

### Agent Pod Daemon (`lib/agent-pod-daemon/daemon.js`)

- Spawns `openclaude` as a child process with `--input-format stream-json --output-format stream-json --dangerously-skip-permissions`
- Claude is kept alive across jobs (persistent session). Auto-respawns on exit after 3s.
- Before each job, diffs MD5 hashes of `memory/global/` and `shared/memory/` dirs; prepends a change summary to the job prompt so Claude re-reads updated files
- Appends memory paths and backend context to every job prompt
- Result is published to `job.reply_to` topic (if set); no reply_to means fire-and-forget
- Status/cancel/health endpoints on port 9090 (`/status`, `/cancel`, `/health`, `/memory-update`)

### Agent Structure (`agents/<name>/`)

Each agent has:
- `IDENTITY.md` — YAML frontmatter (name, model, profile, backend) + identity/rules loaded at boot
- `memory/global/` — long-term knowledge, seeded from repo and read-only updated by the curator
- `skills/` — slash-command skill files invokable by the agent
- Optional `BACKENDS.json` (v2 schema) or reference to `BACKENDS.yaml` at the repo root

### Backend Selection

`BACKENDS.yaml` at the repo root defines named backends (Anthropic, OpenAI-compatible, Gemini, Ollama). Each agent's IDENTITY.md frontmatter references a backend by name. `deploy-runtime.sh` writes `.openclaude-profile.json` and `.openclaude-backends.json` to `AGENT_PROJECT_DIR` at deploy time. The daemon reads these at startup to determine `MODEL_ENV` and passes them as environment variables when spawning `openclaude`.

Selection modes: `first`, `random`, `hash` (hash of pod name — deterministic per-replica routing).

### Shared Protocols (`shared/memory/`)

Markdown files loaded by agents at boot via `@` imports in CLAUDE.md:
- `delegation-protocol.md` — when/how to delegate; agent roster
- `memory-protocol.md` — how to write persistent memory via `POST /memory-update`
- `auth-protocol.md`, `credentials-protocol.md` — credential handling rules
- `openclaude-backends-schema.md` — `BACKENDS.json` v2 shape
- `agent-index-schema.md` — `INDEX.yaml` schema for static bundle generation

### Memory System

- **Global** (`/kord/<agent>/memory/global/`) — agent-specific durable knowledge, seeded from `agents/<agent>/memory/` on first deploy
- **Shared** (`/kord/shared/memory/`) — cross-agent facts, seeded from `shared/memory/`
- **Team** — team-scoped directory (see `runtime-ownership.yaml`)
- The daemon watches for changes via MD5 hashing before each job and injects a diff summary into the prompt
- Agents write new memories via `POST http://localhost:9090/memory-update`; the scribe (`lib/agent-scribe/`) deduplicates and merges

### Infrastructure Manifests

Kubernetes manifests live in `agents/charon/skills/bootstrap/manifests/`. KEDA scales agent pods. Alfred owns the profile source under `agents/alfred/profile/`, and the runtime projection lives under `shared/runtime/profile/`. Bootstrap scripts are in `installer/`.

## Settings

`settings.json` at repo root configures the workstation harness:
- `env` — injects `KORD_SOURCE_ROOT`, `KORD_LOCAL_STATE`, `KORD_WORKTREES_DIR`, etc.
- `hooks.PreToolUse` — runs `guard.sh` before Write/Edit/Bash/Grafana tool calls

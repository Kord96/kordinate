# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Kordinate is a framework for running specialized AI agents as Kubernetes pods with persistent Klaude sessions. Klaude owns the harness/runtime, including Kafka mode. Kordinate owns platform orchestration: images, manifests, PVC layout, runtime seeding, and agent metadata.

Each agent consumes its own Kafka request topic. Requests follow the runtime contract:
- `{ prompt, timeout_ms?, reflect?, reply_to }`
- `reply_to` is required

Responses are published by Klaude and follow:
- `{ status, output, reflection?: { project, general }, errors?: string[] }`

Agent-to-agent communication is direct through Kafka; no HTTP router is required.

"},{
## Running the Services

```bash
# Klaude daemon package (per-agent, needs AGENT_NAME env)
cd shared/klaude-daemon
AGENT_NAME=charon npm run start
```

Key environment variables for the daemon:
- `AGENT_NAME` — required; selects which Kafka topic (`agent.<AGENT_NAME>`) to consume
- `AGENT_PROFILE` — optional; selects the specialist flavor/profile independently of the deployed agent name
- `AGENT_PROJECT_DIR` — agent working dir, defaults to `/runtime/<AGENT_NAME>`
- `AGENT_STATE_DIR` — persistent state dir, defaults to `/kord/<AGENT_NAME>`
- `KAFKA_BROKERS` — defaults to `kafka-kafka-bootstrap.dev.svc.cluster.local:9092`

## Deployment Scripts

```bash
# Deploy agent runtime files from repo → runtime
# Optional second arg seeds one agent flavor into another deployed agent name.
lib/scripts/deploy-runtime.sh <source-agent|all> [destination-agent]

# Generate agent bundle (AGENT.md static preload)
lib/scripts/generate-agent-bundle.py <agent>

# Generate platform kustomization overlay
lib/scripts/generate-platform-kustomization.py

# Toggle an agent's backend profile
lib/scripts/toggle-profile.sh <agent> <backend-name>
```

## Architecture

### Job Routing

Each agent has a single Kafka request topic: `agent.<name>`. Messages are routed there directly — no HTTP router and no shared result topic.

Requests must include:
- `prompt`
- optional `timeout_ms`
- optional `reflect`
- required `reply_to`

Klaude consumes `agent.<AGENT_NAME>`, runs the persistent agent session, and publishes the result to `reply_to`.

### Klaude daemon runtime

- Klaude owns the persistent harness/runtime and Kafka mode
- Kordinate provides runtime seeding, PVC layout, image composition, and deployment manifests
- The shared daemon implementation lives in `shared/klaude-daemon/`
- Before each job, the runtime can diff shared/agent memory state so updated files are re-read
- Results follow the runtime contract: `{ status, output, reflection?: { project, general }, errors?: string[] }`
- Status and memory endpoints remain on port 9090 (`/status`, `/health`, `/memory-update`)

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
- **Team** — team-scoped directory (see `ownership-policy.yaml`)
- The daemon watches for changes via MD5 hashing before each job and injects a diff summary into the prompt
- Agents write new memories via `POST http://localhost:9090/memory-update`; the scribe (`lib/agent-scribe/`) deduplicates and merges

### Infrastructure Manifests

Kubernetes manifests live in `agents/charon/skills/bootstrap/manifests/`. KEDA scales agent pods. Alfred owns the profile source under `agents/alfred/profile/`, and the runtime projection lives under `shared/runtime/profile/`. Bootstrap scripts are in `installer/`.

## Settings

`settings.json` at repo root configures the workstation harness:
- `env` — injects `KORD_SOURCE_ROOT`, `KORD_LOCAL_STATE`, `KORD_WORKTREES_DIR`, etc.
- `hooks.PreToolUse` — runs `guard.sh` before Write/Edit/Bash/Grafana tool calls

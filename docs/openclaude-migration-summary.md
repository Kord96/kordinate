# OpenClaude Migration Summary

## Overview

Kordinate now uses OpenClaude as the harness layer while allowing each agent pod to target different backend model providers. The runtime no longer assumes a single hardcoded provider mapping like `profile: openai -> deepseek`. Instead, each agent gets a generated per-agent backend config, and the daemon records which backend actually handled each job.

## Current Runtime Model

### 1. Agent identity stays simple

Agents still declare a primary runtime in `IDENTITY.md`:
- `profile` — OpenClaude harness profile (`anthropic`, `openai`, `gemini`, `ollama`, etc.)
- `model` — backend model name
- optional `base_url`
- optional `api_key_env`
- optional `api_key_ref`
- optional `backend_name`
- optional `backend_strategy`

This keeps single-backend agents simple.

### 2. deploy-runtime generates two runtime files

The generic `BACKENDS.json` format is documented in `shared/openclaude-backends-schema.md` and can be used by any agent.


For each runtime agent directory, `lib/scripts/deploy-runtime.sh` now writes:

- `.openclaude-profile.json`
  - the active backend configuration the daemon should boot with
  - generated runtime/local state, not a repo-managed source file
- `.openclaude-backends.json`
  - the full backend pool for that agent

If `agents/<name>/BACKENDS.json` exists, it becomes the source of truth for the pool.
If it does not exist, the deploy script synthesizes a one-backend pool from `IDENTITY.md`.

### 3. backend selection happens at pod startup

`lib/agent-pod-daemon/daemon.js` now:
- reads `.openclaude-backends.json`
- selects a backend using the configured strategy
- hydrates provider-specific environment variables at runtime from real pod env vars
- starts OpenClaude with the selected backend profile/model

Supported selection modes today:
- `first`
- `random`
- `hash`

`hash` is deterministic per pod name, which makes multi-replica deployments stable while still distributing replicas across a backend set.

### 4. attribution is included in job results

Each job result now includes backend metadata:
- backend name
- profile
- provider
- model
- model spec
- selection strategy

This metadata is emitted by the daemon and preserved in Kafka result messages.

That gives us a clean way to later compare strengths/weaknesses by backend for the same logical agent.

## Why this is better than `profile: openai -> deepseek`

That older mapping was too opinionated. `openai` is a harness compatibility mode, not a specific model vendor.

With the new shape:
- `profile: openai` means “use OpenAI-compatible transport”
- the actual backend identity comes from `backend_name`, `base_url`, and `model`
- multiple OpenAI-compatible backends can coexist in one agent pool

Examples:
- DeepSeek via OpenAI-compatible API
- Fireworks-hosted DeepSeek
- Codex/OpenAI-compatible endpoints
- Ollama using OpenAI-compatible transport

## Secrets handling

The deploy step no longer tries to resolve secrets into generated JSON.
Instead, generated runtime config stores metadata such as `api_key_env` / `api_key_ref`, and the daemon hydrates credentials from the pod environment at runtime.

This avoids writing broken literal command substitutions into JSON and keeps secrets out of generated config files.

## Backward compatibility

Legacy files are still generated:
- `.model`
- `.provider`
- `.model-spec`

But they are now derived from the normalized active backend profile rather than forcing special-case provider aliases.

## Testing helpers updated

The local helper scripts now reflect the new architecture:
- `toggle-profile.sh` now acts as a per-agent backend selector against `/kord/agents/<agent>/`

The older top-level scratch helpers (`test_deploy.sh`, `test-spawn.js`, `test_parse.sh`) were temporary migration aids and are no longer part of the supported runtime workflow.

## Recommended multi-backend pattern

For agents that may run multiple replicas, especially `augur`, use a `BACKENDS.json` file like:

```json
{
  "selection": "hash",
  "backends": [
    {
      "name": "anthropic-opus",
      "profile": "anthropic",
      "provider": "anthropic",
      "model": "claude-opus-4-6",
      "api_key_env": "ANTHROPIC_API_KEY"
    },
    {
      "name": "deepseek-reasoner",
      "profile": "openai",
      "provider": "openai",
      "model": "deepseek-reasoner",
      "base_url": "https://api.deepseek.com",
      "api_key_env": "DEEPSEEK_API_KEY"
    }
  ]
}
```

That gives:
- one logical agent identity
- multiple backend implementations
- stable replica/backend assignment when desired
- backend attribution in results for later reflection

## Migration status

### Done
- OpenClaude is the harness runtime
- deploy-runtime generates normalized backend config
- daemon backend selection is driven by backend entries rather than legacy model maps
- daemon selects a backend and hydrates env at runtime
- Kafka result messages preserve backend attribution in delegated responses
- helper scripts match the new per-agent runtime model

### Still to do
- expose backend attribution in any downstream dashboards/log consumers that should compare model quality
- decide whether reflection memory should automatically include backend attribution in saved notes
- automate pass-store-to-runtime-secret reconciliation so Alfred-owned credentials flow into agent runtime without manual steps

## Files touched by this migration work

- `/kord/projects/kordinate/lib/scripts/deploy-runtime.sh`
- `/kord/projects/kordinate/lib/agent-pod-daemon/daemon.js`
- `/kord/projects/kordinate/lib/scripts/toggle-profile.sh`

## Repo ownership note

Treat `.openclaude-profile.json` as generated runtime/local state. The repo may contain examples or test fixtures, but normal local profile files should stay untracked.

## Practical outcome

The platform can now move toward:
- “OpenClaude as harness”
- “backend chosen per agent pod”
- “replicas distributed across a backend set”
- “job outputs labeled with the backend that produced them”

That is the right base for later comparing which backend is strongest for which agent role.

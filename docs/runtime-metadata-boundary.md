# Runtime metadata boundary

This repo currently has two different metadata systems that serve different purposes. They should not be conflated during cleanup.

## 1. `KORD.json` — former runtime routing/resource metadata

`KORD.json` was the legacy runtime-facing registry. It has now been removed from the primary runtime path.

Historically it described things like:

- public skills and route exposure
- resource catalogs and cache metadata
- some guard/validation ownership metadata

### Cleanup direction

The platform has moved toward explicit pod-agent delegation through the job router REST/MCP surfaces, not local `/kord` orchestration. `KORD.json` has been retired from the active runtime path after those responsibilities were replaced.

Do **not** move routing or guard metadata into `INDEX.yaml`.

## 2. `INDEX.yaml` — static agent bundle metadata

`INDEX.yaml` is a per-agent static content manifest.

It is defined by:

- `shared/agent-index-schema.md`

It is consumed by:

- `lib/scripts/generate-agent-bundle.py`

It describes:

- which repo files belong in an agent's deterministic static bundle
- what should be preloaded versus read on demand
- what is repo-authored versus generated versus runtime-only

### Cleanup direction

`INDEX.yaml` should remain focused on static bundle generation and preload boundaries. It must not become a replacement runtime registry.

## Intended end state

### Keep or evolve separately

- **Delegation API / Kafka dispatch** — explicit `agent + prompt` job routing
- **`INDEX.yaml`** — static bundle manifest per agent

### Replace and then remove

- **`KORD.json` route catalogs**
- **`KORD.json` resource catalogs**
- **legacy `/kord` compatibility routing**

## Practical rule for future changes

- If the metadata decides **what an agent bundle contains**, it belongs in `INDEX.yaml`.
- If the metadata decides **how runtime requests are routed or guarded**, it should live in a dedicated runtime config surface — and not in `INDEX.yaml`.

The old `KORD.json` role has been removed rather than folded into the bundle manifest system.

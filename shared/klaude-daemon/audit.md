---
description: Audit entrypoint for the shared klaude-daemon runtime, request contract, and telemetry behavior
---

# Klaude Daemon Audit

Use this file with the shared `/audit` skill when auditing the daemon/runtime layer.

## Scope

Audit these layers in order:

1. request contract
2. runtime execution semantics
3. reflection and response metadata
4. discovery and health behavior
5. telemetry, timing, and usage capture

## Structural

Primary references:
- [src/types.ts](./src/types.ts)
- [src/config.ts](./src/config.ts)
- [src/agent-profile.ts](./src/agent-profile.ts)
- [src/runtime.ts](./src/runtime.ts)
- [src/index.ts](./src/index.ts)
- [src/protocol.ts](./src/protocol.ts)

Structural questions:
- Are `home_dir` and `working_dir` semantics separate and consistent?
- Are agent contracts enforced centrally where required?
- Is response metadata preserved rather than overwritten?
- Are reflection events and response payloads using coherent schemas?
- Does the daemon fail fast on missing required request fields?

## Runtime

Primary references:
- [src/protocol.test.ts](./src/protocol.test.ts)
- [src/runtime-error-format.test.ts](./src/runtime-error-format.test.ts)
- [src/runtime-openclaude-resolution.test.ts](./src/runtime-openclaude-resolution.test.ts)
- [src/runtime-alfred-contract.test.ts](./src/runtime-alfred-contract.test.ts)
- [src/config.test.ts](./src/config.test.ts)

Runtime questions:
- Does a live request preserve the right cwd and runtime home semantics?
- Are timing and usage fields returned end to end?
- Are reflection and error paths captured correctly?
- Does the daemon surface backend failures with enough detail to debug?

Telemetry contract:
- Shared daemon telemetry should stay runtime-oriented and joinable by `request_id`.
- Canonical shape:
  - `executor`: daemon-selected agent/provider/model identity
  - `times`: `gateway_received_at`, `daemon_started_at`, `daemon_completed_at`
  - `metrics`: derived queue/elapsed/cpu/memory/token/cost measurements
- Agent-specific context such as repository, commit, analysis id, bundles, and validation should remain agent-owned metadata linked through `request_id`, not daemon-owned telemetry fields.

## Fix Layer Guidance

When issues are found, prefer fixing them in:
- request contract
- runtime adapter behavior
- response/metadata schema
- tests

Avoid patching agent prompts to compensate for daemon contract bugs.

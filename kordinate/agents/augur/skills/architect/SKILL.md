---
name: architect
description: >
  Produce architecture.yaml — components, flows, state, events, dependencies, failure modes.
  Use when asked to understand architecture, audit a codebase, onboard to a project, or before
  cross-cutting changes.
argument-hint: "<project>"
context: fork
curated: true
scope: global
---

Produce `architecture.yaml` — a structured map of a project's architecture that downstream skills (`/assess-debt`) and future viewpoint generators consume.

## Arguments

`$ARGUMENTS` — Required: `<project>`. Directory must exist at `~/<project>/`, `~/repos/<project>/`, or `~/test-repos/<project>/`.

## Steps

1. **Locate and scan project** — resolve the project directory (call it `$ROOT` for the remaining steps). Check paths in order: `~/<project>/`, `~/repos/<project>/`, `~/test-repos/<project>/`; if `$ARGUMENTS` is an absolute path, use it directly. If not found, report which paths were checked and exit. If found but empty or has no source files, produce a minimal `architecture.yaml` with just `project`, `purpose: "Empty or scaffold"`, and empty `components`. Detect the stack: **languages** from package manifests (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.); **frameworks** from dependency lists in those manifests (e.g., `fastapi` in `pyproject.toml` dependencies means FastAPI); **runtime** from Dockerfile CMD/ENTRYPOINT, Procfile, `__main__.py`, or main entry point (long-lived server, CLI invocation, serverless, etc.). For mixed/unusual stacks, document what you find honestly. **Monorepo**: if the root contains multiple packages/services (e.g., `packages/`, `services/`, `apps/`), treat each as a top-level component and note the monorepo structure in `purpose`. **No clear entry point**: rely on package manifests, Dockerfiles, and high-fan-in modules to infer the main paths.

2. **Gather sources** — glob `$ROOT` for source files matching the include patterns in [extractors.md](extractors.md), skipping excluded directories and files. Read matches into context. Cap at 100KB per file. For large projects (>500 files after filtering), follow the priority order in extractors.md: entry points and manifests first, then boundaries and interfaces, then business logic, stopping when context is full.

3. **Gather existing analysis** — read from `$ROOT/.kord/agents/augur/memory/` if available: `patterns.md`, `dependencies.md`, `api-review.md`, `debt-assessment.md`. Read the abstraction index (`~/.kord/agents/augur/memory/abstractions.md`) and use its canonical names for component `abstraction` and `patterns` fields. For `concept` fields on `state` and `external_dependencies`, use the infrastructure terms listed in [schema.md](schema.md) (e.g., `embedded-olap`, `message-broker`) -- these are NOT from abstractions.md. Consult specific `~/.kord/agents/augur/memory/concepts/<name>/pattern.md` files only when you suspect a match -- do not read the full catalog. Consistent naming matters because downstream skills match on these terms. If nothing exists, file contents alone suffice.

4. **Identify components, capabilities, and relationships** — target 5-10 top-level components (acceptable range: 4-12). See [guidance.md](guidance.md) for filtering criteria and what to extract per component. Use `children` to nest sub-components rather than inflating the top-level count. Group components into capabilities: business-level things the system can do, linked to the actors who use them. Map relationships between components grounded in actual code (imports, calls, message passing). Shared utility imports are incidental coupling, not architectural relationships.

5. **Map actors, flows, and events** — identify external actors (users, services, cron, data sources). Trace 2-4 critical data flows showing how data moves from trigger to final state; link each flow to the actor(s) that trigger it. For CRUD/REST projects, request-response cycles are valid flows. For CLI tools, command invocation through to output/side-effect is a flow. Map events (producer, consumers, data carried). Omit `events` entirely if the project has none.

6. **Catalog state and dependencies** — for each data store: concept, technology, what it stores, purpose, persistence. For each external dependency: concept, technology, which components use it, criticality, resilience patterns. Use concept catalog terms (`embedded-olap` not "DuckDB database").

7. **Identify failure modes** — for each external dependency and stateful component, trace cascading failures: what breaks, which components are affected, user impact, detection, recovery, severity. For detection: look for existing metrics, health checks, log patterns, or error handlers in the code; if none exist, write `"none"` (this itself is a finding). For recovery: document automatic recovery (retries, reconnects) found in code, or `"none"` if manual intervention is required. Think through chains: if A depends on B depends on external C, then C failing cascades through B to A.

8. **Gemini review** (background) — before writing the final YAML, kick off a peer review. Feed the draft architecture and project source to Gemini:
   ```bash
   gemini -m gemini-2.5-pro -o json -p "Review this architecture.yaml against the source code. Flag: missing components that exist in code but not in the YAML, incorrect dependency edges, failure modes that were missed, flows that skip important steps, and any component descriptions that misrepresent what the code does. Be specific." @$ROOT/ < /tmp/architecture-draft.yaml > /tmp/gemini-review-arch.json &
   ```
   Continue to step 9 immediately. The `@$ROOT/` syntax feeds the full codebase to Gemini's context window for cross-referencing.

9. **Write and report** — assemble findings into [schema.md](schema.md) format. Set `version: "1"` and `generated` to today's date. If the Gemini review from step 8 is available, incorporate valid critiques: add missing components, fix incorrect edges, add missed failure modes. Ignore critiques about style or naming — focus on factual errors. Write to `$ROOT/.kord/agents/augur/memory/architecture.yaml` (create directory if needed). If a pre-commit hook prevents the write, ask scribe to write it instead. Report: purpose, capabilities, component names, flow count, dependency count, failure modes with severity, whether Gemini review was incorporated, file path written.

## Example Report

```
## Architecture: stoik

**Purpose**: Stream processing — Kafka to DuckDB with FlightSQL/HTTP serving.
**Capabilities** (3): Stream ingestion, Batch storage, Query serving
**Components** (7): Kafka Consumer, In-Memory Buffer, Consume Loop, DuckDB Store, FlightSQL Server, HTTP API, Entity Cache
**Flows** (2): Kafka-to-DuckDB ingestion, Query serving
**External** (2): Kafka Broker (critical), Schema Registry (important)
**Failures** (3): Kafka down (critical), DuckDB lock contention (medium), Snapshot module missing (high)

Written to: ~/stoik/.kord/agents/augur/memory/architecture.yaml
```

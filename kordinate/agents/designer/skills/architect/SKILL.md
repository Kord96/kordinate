---
name: architect
description: Produce a unified architectural understanding of a project as architecture.yaml — components, flows, state, events, dependencies, failure modes.
curated: true
scope: global
---

Produce a structured architectural understanding of a project.

## Arguments

`$ARGUMENTS` — Required: `<project>` (e.g., `logbd`, `stoik`, `sous-storefront`). The project directory must exist at `~/<project>/`, `~/repos/<project>/`, or `~/test-repos/<project>/`.

## Steps

1. Parse project name from `$ARGUMENTS`. Locate the project directory. If not found, report and exit.

2. **Detect stack** — check for `package.json` (JS/TS), `pyproject.toml`/`requirements.txt`/`setup.py` (Python), `go.mod` (Go), `Cargo.toml` (Rust), or combinations. Note the primary language and framework.

3. **Gather file contents** — collect source files for analysis. See [extractors.md](extractors.md) for include/exclude patterns. For each file, read its contents. Cap at 100KB per file. If the project is too large (>500 files after filtering), prioritize: entry points, hub modules, config files, manifests, README.

4. **Gather existing analysis** — read from `<project>/.claude/agent-memory/designer/` if available:
   - `patterns.md` (from `/detect-patterns`)
   - `dependencies.md` (from `/map-dependencies`)
   - `api-review.md` (from `/review-api`)
   - `debt-assessment.md` (from `/assess-debt`)

   Also check `<project>/.claude/agent-memory/sauron/scan.md`.

   If none exist, proceed without — file contents are sufficient.

5. **Identify core abstractions** — using the file contents and any existing analysis, identify the 5-10 most architecturally significant abstractions in the project. For each, provide:
   - A concise name (human-readable, not a module path)
   - What it does (one sentence)
   - Which source files implement it
   - What patterns it uses (if detected)

   Filtering heuristics:
   - Utilities/logging/config modules have high fan-in but are NOT core abstractions — skip them
   - Entry points (servers, CLI, main) ARE core abstractions — they're where actors interact
   - Data stores and external integrations ARE core — they define the system's boundaries
   - Prefer business-domain abstractions over infrastructure plumbing

6. **Map relationships** — for each pair of abstractions, determine if a significant relationship exists:
   - What flows between them (data, events, calls)
   - Direction (A→B, B→A, bidirectional)
   - Label the relationship in a few words (e.g., "publishes entities", "queries graph", "enriches via DNS")

   Only include relationships backed by actual code (imports, function calls, message passing). Exclude trivial relationships (shared utility imports).

7. **Identify actors** — who/what interacts with the system from outside:
   - Users (via API, CLI, UI)
   - Other services (via HTTP, gRPC, message broker)
   - Scheduled jobs (cron, timers)
   - Data sources (files, NFS, external APIs)

8. **Map data flows** — trace the critical paths through the system. A data flow is a sequence of steps showing how data moves from trigger to final state. Focus on:
   - The primary ingestion/processing pipeline
   - The query/serving path
   - Any async/event-driven chains

9. **Catalog state** — for each data store detected, classify:
   - Technology (use generic concept: relational database, document store, embedded OLAP, cache, object store, message broker, filesystem — plus the specific implementation)
   - What it stores
   - Purpose: source-of-truth, cache, derived, staging
   - Persistence: persistent or ephemeral

10. **Map events** — for each event/topic/signal found:
    - Producer component
    - Consumer component(s)
    - What data it carries
    - Rough frequency if determinable

11. **Catalog external dependencies** — for each external call:
    - What it is (generic concept + implementation)
    - Which component uses it
    - Purpose
    - Criticality (critical/important/optional)
    - Whether resilience patterns exist (retry, circuit breaker, timeout, fallback)

12. **Identify failure modes** — for each external dependency and stateful component:
    - What breaks
    - Which components are affected
    - What users/system experience
    - Whether detection/mitigation exists
    - Severity

13. **Write architecture.yaml** — assemble all findings into the schema defined in [schema.md](schema.md). Write to `<project>/.claude/agent-memory/designer/architecture.yaml`.

    Create the directory if it doesn't exist. Delegate the write to scribe if the guard-md hook blocks you.

14. **Report** — summarize: purpose, component count, flow count, external dependency count, failure modes identified, and where the file was written.

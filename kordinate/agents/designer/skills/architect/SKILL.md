---
name: architect
description: >
  Produce architecture.yaml v2 — components, flows, state, events, dependencies, failure modes,
  detected concepts, API surface, and debt assessment. One coherent pass over the codebase.
  Use when asked to understand architecture, audit a codebase, onboard to a project, or before
  cross-cutting changes.
argument-hint: "<project> [--reverse]"
context: fork
curated: true
scope: global
---

Produce `architecture.yaml` — a complete architectural understanding of a project in one pass. Version 2 integrates concept detection, dependency mapping, API review, and debt assessment into a single coherent artifact that downstream skills (`/illustrate-architecture`) and viewpoint generators consume.

## Arguments

`$ARGUMENTS` — Required: `<project>`. Optional: `[--reverse]` to scan sibling projects for inbound dependency references. Directory must exist at `~/<project>/`, `~/repos/<project>/`, or `~/test-repos/<project>/`.

## Steps

1. **Locate, scan, and gather sources** — resolve the project directory (call it `$ROOT`). Check paths in order: `~/<project>/`, `~/repos/<project>/`, `~/test-repos/<project>/`; if `$ARGUMENTS` is an absolute path, use it directly. If not found, report which paths were checked and exit. If found but empty or has no source files, produce a minimal `architecture.yaml` with just `project`, `purpose: "Empty or scaffold"`, and empty sections. Detect the stack: **languages** from package manifests (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.); **frameworks** from dependency lists (also using [frameworks.md](frameworks.md) for web framework detection); **runtime** from Dockerfile CMD/ENTRYPOINT, Procfile, or main entry point. Glob `$ROOT` for source files per [extractors.md](extractors.md). Read the concept catalogs: abstractions index (`~/.kord/agents/designer/memory/abstractions.md`), concepts index, anti-patterns index. For `concept` fields on `state` and `external_dependencies`, use the infrastructure terms listed in [schema.md](schema.md).

2. **Detect concepts** — with the source files in context, run the concept catalog scan inline. See [detection.md](detection.md) for the full procedure: Pass 1 (batch grep per category), Pass 2 (ast-grep/semgrep rules), Pass 3 (manual signature verification), Pass 3.5 (diagnostic question evaluation). Assess confidence per concept. Identify gaps (external calls without resilience, stack-implied patterns, catalog cross-references). Hold the results — detected patterns, anti-patterns, and gaps feed into steps 5-7.

3. **Map dependencies** — inline dependency analysis per [dep-analysis.md](dep-analysis.md). Discover internal modules and trace imports. Detect external services from client library usage and ORM schemas. Scan infrastructure manifests (k8s, Terraform, Pulumi). Discover inter-service config references. Flag circular dependencies and hub modules. If `--reverse`, scan sibling projects for inbound references. Hold the results — module graph, external services, infrastructure, and risks feed into steps 5-6.

4. **Review API surface** — inline API review per [api-review.md](api-review.md). Detect web framework(s) using [frameworks.md](frameworks.md). Discover all route/endpoint definitions with auth and validation columns. Run the REST hygiene checklist (7 concerns). Assess gateway pattern and hexagonal architecture compliance. Handle non-REST styles (GraphQL, gRPC, WebSocket, SSE). Hold the results — endpoint inventory and findings feed into steps 5 and 7.

5. **Identify components, capabilities, and relationships** — using all intermediate state from steps 2-4, identify 5-10 top-level components per [guidance.md](guidance.md). Annotate each component with: detected patterns (from step 2), dependency info (from step 3), and API endpoints (from step 4). Use `children` to nest sub-components. Group components into capabilities linked to actors. Map relationships grounded in actual code. Shared utility imports are incidental coupling, not architectural relationships.

6. **Map actors, flows, events, state, and external dependencies** — identify external actors (users, services, cron, data sources). Trace 2-4 critical data flows. Map events (omit if none). Catalog state stores with concept vocabulary from [dep-analysis.md](dep-analysis.md). Catalog external dependencies with criticality and resilience assessment informed by concept detection from step 2.

7. **Failure modes and debt assessment** — for each external dependency and stateful component, trace cascading failures: what breaks, cascade, user impact, detection, recovery, severity. For detection signals: look for existing metrics, health checks, log patterns in code; write `"none"` if absent. Then run the debt assessment inline per [debt.md](debt.md): load anti-patterns from detected concept files, scan for violations, calculate score and grade (A-F with hard floor rule), categorize, prioritize 3-7 recommendations. Failure modes and debt share a natural boundary — a missing resilience pattern is both a failure mode and a debt item.

8. **Gemini review** (background) — feed the draft architecture.yaml and project source to Gemini:
   ```bash
   gemini -m gemini-2.5-pro -o json -p "Review this architecture.yaml v2 against the source code. Flag: missing components, incorrect dependency edges, missed failure modes, concept detection false positives, severity misclassifications in debt, API findings that were missed. Be specific." @$ROOT/ < /tmp/architecture-draft.yaml > /tmp/gemini-review-arch.json &
   ```
   Continue to step 9 immediately.

9. **Write architecture.yaml** — assemble all findings into [schema.md](schema.md) v2 format. Set `version: "2"` and `generated` to today's date. Incorporate valid Gemini critiques if available: add missing components, fix incorrect edges, add missed failure modes, adjust debt severities. Ignore critiques about style or naming. Write to `$ROOT/.kord/agents/designer/memory/architecture.yaml` (create directory if needed). If a pre-commit hook prevents the write, ask scribe to write it instead.

10. **Report** — summarize:
    ```
    ## Architecture: <project>

    **Purpose**: <one sentence>
    **Components** (N): <names>
    **Flows** (N): <names>
    **Concepts**: N patterns, N anti-patterns, N gaps
    **API**: N endpoints, N critical / N recommended / N minor findings
    **Debt**: Score N — Grade X. <interpretation>
    **External** (N): <names with criticality>
    **Failures** (N): <names with severity>
    **Top recommendations**: 1. ... 2. ... 3. ...

    Written to: <path>
    ```

---
name: design
description: >
  Design a new project: pattern recommendation from concept catalog, design atlas
  with stories/journeys for visual review, monitoring/deployment/test specs for
  agent handoff, and scaffold generation. Supports flag-driven modes for
  workstation orchestration.
argument-hint: "<project-name> [--patterns 'p1,p2,...'] [--approve] [--scaffold]"
context: inherit
---

Design a new project. Each invocation does one focused task based on flags.
The workstation Claude orchestrates the conversation with the human and calls
this skill repeatedly as the design progresses.

## Modes

| Flag | What it does | Input | Output |
|------|-------------|-------|--------|
| (none) | Recommend patterns | Requirements in prompt | Pattern recommendations |
| `--patterns "p1,p2,..."` | Generate design atlas | Approved pattern list | design-atlas.json + stories + journeys |
| `--approve` | Generate agent specs | Existing design atlas | monitoring/deployment/test specs |
| `--scaffold` | Generate code + repo | Approved design + specs | GitHub repo with stubs |

## Shared References

These files are shared with /analyze — read them when producing output:
- [../../schemas/atlas-schema.md](../../schemas/atlas-schema.md) — atlas JSON structure
- [../../schemas/schema.md](../../schemas/schema.md) — field-level details
- [../../schemas/story-schema.md](../../schemas/story-schema.md) — story/journey YAML format
- [../../schemas/composition-guide.md](../../schemas/composition-guide.md) — how to build story trees
- [../../schemas/writing-guide.md](../../schemas/writing-guide.md) — prose style
- [../../schemas/augur-output-contract.md](../../schemas/augur-output-contract.md) — downstream consumer contract

---

## Mode: Recommend Patterns (default)

Invoked: `/design orders` with requirements in the prompt.

### Step 1 — Read context

1. **Infra atlas** — `$AGENT_PROJECT_DIR/memory/global/infra-atlas.json`
   - Available services in dev, new_workload_contract
   - If missing, respond: "Need infra atlas. Ask charon to run /survey first."

2. **Concept indexes** — `memory/global/concepts.md` and `memory/global/anti-patterns.md`
   - Note the categories and entry counts

### Step 2 — Understand requirements

The prompt contains requirements from the human (relayed by the workstation Claude).
Extract:
- Purpose — what the service does
- Inputs/outputs — what data enters and leaves
- Scale — single instance or horizontally scaled
- Constraints — language, framework, timeline

### Step 3 — Select patterns top-down

Work through the concept catalog by abstraction level. At each level, browse
the relevant **categories** in `concepts.md` — don't hardcode pattern names.
Read concept summaries from the index to find fits. Only read full `concept.md`
files for the strongest candidates.

**Level 1 — Architecture** (categories: `architecture`, `structural`)
Pick 1-2 patterns that define the overall structure. These constrain everything below.

**Level 2 — Domain model** (categories: `data`, `storage`)
Based on Level 1, what data patterns fit? Event sourcing, aggregates, repositories?

**Level 3 — Communication** (categories: `integration`, `messaging`, `api`)
How data enters and leaves. Cross-reference with infra atlas: what's available in dev?

**Level 4 — Resilience** (categories: `resilience`, `error-handling`)
For each external dependency from Level 3, which resilience patterns apply?
This level is mostly derived — present as a package, not individual questions.

**Level 5 — Data storage** (categories: `storage`, `data`)
Based on Levels 2 and 3, what storage approach? Check infra atlas for availability.

**Level 6 — Cross-cutting** (categories: `security`, `lifecycle`, `distributed`)
Auth, feature flags, tracing, graceful shutdown.

### Step 4 — Report recommendations

For each recommended pattern, note:
- Which concept catalog entry it maps to
- Whether it has `monitoring.md`, `testing.md`, `deployment.md`
- One-sentence rationale

```
## Pattern Recommendations: <project>

Based on: <1-sentence requirements summary>
Infrastructure: <available services from infra atlas>

### Architecture
- **hexagonal** — [reason]. Has: monitoring ✓, testing ✓, deployment ✓

### Communication
- **consumer-group** — [reason]. Has: testing ✓
- **webhook** — [reason]. Has: monitoring ✓, testing ✓, deployment ✓

### Resilience
- **circuit-breaker** — [reason]. Has: monitoring ✓, testing ✓, deployment ✓
- **retry** — [reason]. Has: testing ✓

### Data
- **event-sourcing** — [reason]. Has: monitoring ✓, testing ✓, deployment ✓

### Cross-cutting
- **distributed-tracing** — [reason]. Has: monitoring ✓

New infrastructure needed: <list> or "none — all available in dev"

To proceed: ask the workstation to call `/design <name> --patterns "hexagonal,consumer-group,circuit-breaker,retry,event-sourcing,distributed-tracing"`
```

---

## Mode: Generate Design Atlas (`--patterns`)

Invoked: `/design orders --patterns "hexagonal,consumer-group,circuit-breaker,retry,event-sourcing"`

### Step 1 — Load patterns

For each pattern in the comma-separated list:
1. Read `memory/global/concepts/<pattern>/concept.md`
2. Note availability of `monitoring.md`, `testing.md`, `deployment.md`

### Step 2 — Read infra atlas

Read `$AGENT_PROJECT_DIR/memory/global/infra-atlas.json` for:
- Service endpoints (for external_dependencies in atlas)
- new_workload_contract (for compliance)

### Step 3 — Produce design atlas

Generate `$MEM/design-atlas.json` following [../../schemas/atlas-schema.md](../../schemas/atlas-schema.md) v4 format:

- **components** — proposed modules based on the architecture pattern
- **detected_patterns** — all selected patterns, `confidence: 1.0`, `source: "design"`
- **flows** — designed data flows based on communication patterns
- **external_dependencies** — with endpoints from infra atlas
- **failure_modes** — anticipated failures from resilience patterns. For each failure mode,
  populate `detection` with structured fields: `signals` (from the pattern's monitoring.md
  Key Metrics), `concern` (abstract category), `source_pattern` (concept name). These
  are portable — sauron maps them to Prometheus queries and vitals evaluations
- **domain_model** — from the data patterns
- **debt** — empty (score: 0, grade: A)
- **metadata.analysis_mode** — `"design"`
- **metadata.status** — `"draft"`
- **metadata.patterns_with_monitoring** — patterns that have monitoring.md
- **metadata.patterns_with_tests** — patterns that have testing.md
- **metadata.patterns_with_deployment** — patterns that have deployment.md
- **metadata.new_infrastructure** — services not in infra atlas

### Step 4 — Compose stories and journeys

Follow [../../schemas/composition-guide.md](../../schemas/composition-guide.md).

For a design atlas, stories explain the PROPOSED architecture:
- Root stories per component group — what it does and why
- Child stories for key flows — how data moves through the design
- Child stories for design decisions — why this pattern was chosen (use rationale blocks)
- Getting-started journey — the reading order for someone onboarding to this new project

Write to `$MEM/stories/` and `$MEM/journeys/`.

### Step 5 — Report

```
## Design Atlas: <project>

Components (N): <names>
Patterns (N): <grouped by level>
Flows (N): <names>
Stories: N root, N child
Journeys: N

Written to: $MEM/design-atlas.json, $MEM/stories/, $MEM/journeys/

Review the design. Then:
- To approve: `/design <name> --approve`
- To change patterns: `/design <name> --patterns "new,list"`
```

---

## Mode: Approve (`--approve`)

Invoked: `/design orders --approve`

### Step 1 — Read design atlas

Read `$MEM/design-atlas.json`. Verify `metadata.status` is `"draft"`.

### Step 2 — Generate monitoring spec

For each pattern in `metadata.patterns_with_monitoring`:
1. Read `memory/global/concepts/<pattern>/monitoring.md`
2. Extract metrics, alerts, dashboard guidance

Write `$MEM/monitoring-spec.yaml`:
```yaml
version: "1"
project: <name>
source: design-atlas.json
contract:  # from infra-atlas new_workload_contract.observability
metrics:
  - name: <metric>
    type: counter|gauge|histogram
    labels: [<labels>]
    pattern: <source pattern>
alerts:
  - name: <alert>
    condition: <from monitoring.md>
    severity: critical|warning
    pattern: <source pattern>
  - name: VitalsMissing
    condition: absent(vitals_process{app="<name>"}) for 5m
    severity: critical
    pattern: vitals-meta
dashboards:
  - name: <dashboard>
    panels: [<metric references>]
vitals:
  # Standalone deployment — evaluates app health by querying Prometheus
  deployment: standalone
  port: 9131
  prometheus_url: "http://prometheus.master.svc.cluster.local:9191"
  loki_url: "http://loki.master.svc.cluster.local:3100"
  evaluations:
    - section: process
      description: "Is the main process alive?"
    - section: deps
      description: "Are external dependencies reachable?"
    # Additional sections derived from selected patterns:
    # e.g., circuit-breaker → vitals_deps check for circuit state
    # e.g., consumer-group → vitals_ingestion check for consumer lag
```

### Step 3 — Generate deployment spec

For each pattern in `metadata.patterns_with_deployment`:
1. Read `memory/global/concepts/<pattern>/deployment.md`
2. Extract rollout concerns and pre-deploy checklist

Write `$MEM/deployment-spec.yaml`:
```yaml
version: "1"
project: <name>
source: design-atlas.json
contract:  # from infra-atlas new_workload_contract
rollout_concerns:
  - pattern: <pattern>
    concern: <from deployment.md>
    pre_deploy: <checklist item>
new_infrastructure:  # from metadata.new_infrastructure
```

### Step 4 — Generate test spec

For each pattern in `metadata.patterns_with_tests`:
1. Read `memory/global/concepts/<pattern>/testing.md`
2. Extract test cases by category

Write `$MEM/test-spec.yaml`:
```yaml
version: "1"
project: <name>
source: design-atlas.json
suites:
  - pattern: <pattern>
    unit: [<descriptions>]
    integration: [<descriptions>]
    failure_injection: [<descriptions>]
```

### Step 5 — Lock

Update `design-atlas.json`: `metadata.status` → `"approved"`.

Report specs generated with counts.

---

## Mode: Scaffold (`--scaffold`)

Invoked: `/design orders --scaffold`

### Step 1 — Verify

Read `$MEM/design-atlas.json` (`metadata.status` must be `"approved"`).
Read all three spec files.

### Step 2 — Generate project

```
<name>/
  README.md                purpose, architecture, patterns, getting started
  Dockerfile               multi-stage build for app, satisfies new_workload_contract
  kustomize/
    base/
      deployment.yaml      app deployment — from deployment-spec + contract
      service.yaml         ClusterIP service for app
      vitals.yaml          vitals deployment — standalone health evaluator
      kustomization.yaml
  src/                     code stubs per component
  tests/                   test stubs from test-spec
  vitals/
    Dockerfile             vitals container image
    vitals.py              health evaluation script (queries Prometheus/Loki)
    config.yaml            evaluation sections from monitoring-spec.vitals
  monitoring/
    dashboards/            Grafana JSON from monitoring-spec
    alerts.yaml            Prometheus rules from monitoring-spec (includes VitalsMissing)
```

**App deployment** (`kustomize/base/deployment.yaml`):
- App container with /metrics, app label, prometheus annotations
- Resource limits from deployment-spec contract
- Readiness/liveness probes at /health

**Vitals deployment** (`kustomize/base/vitals.yaml`):
- Standalone pod (separate from app) — one per app per namespace
- Queries Prometheus for app metrics, evaluates health rules
- Exposes health gauges on :9131 with prometheus.io/scrape annotation
- Env vars: PROMETHEUS_URL, LOKI_URL, APP_NAME
- Evaluation sections from monitoring-spec.yaml vitals.evaluations

**Vitals script** (`vitals/vitals.py`):
- Stub that implements the evaluation loop: query → evaluate → expose gauge
- Sections configured via config.yaml (generated from monitoring-spec)
- Each section produces a `vitals_<section>{check}` gauge (0=FAIL, 1=WARNING, 2=OK)
- Always includes: `vitals_process` (is app alive) and `vitals_deps` (are deps reachable)

Stubs implement pattern interfaces with TODO placeholders.

### Step 3 — Create GitHub repo

```bash
gh repo create <owner>/<name> --private --description "<purpose>"
```

Push initial scaffold.

### Step 4 — Deploy

Delegate to charon via the memory endpoint or report the delegation command:
```bash
curl -s http://job-router.kord.svc.cluster.local:3100/api/delegate \
  -d '{"agent":"charon","prompt":"Deploy <name> to dev","project":"<name>","repo":"<url>"}'
```

### Step 5 — Report

```
## Scaffold: <name>

Repo: <url>
Components: N stubs
Tests: N stubs
Manifests: kustomize ready

For sauron: monitoring-spec at $MEM/monitoring-spec.yaml
For charon: deployment-spec at $MEM/deployment-spec.yaml
```

---
name: design
description: >
  Design a new project: interactive discussion with human, pattern selection from
  concept catalog, design atlas for visual review, then scaffold generation with
  monitoring/deployment/test specs for other agents. Use when starting a new service,
  library, or system component.
argument-hint: "<project-name> [--approve] [--scaffold]"
context: inherit
---

Design a new project through an interactive process: understand requirements, select
patterns, produce a visual design atlas for human review, then generate scaffold code
and agent handoff specs.

## Arguments

`$ARGUMENTS` — Required: `<project-name>`. Optional:
- `--approve` — skip design phase, approve existing design and generate scaffold
- `--scaffold` — generate scaffold only (design-atlas.json must exist)

## Phases

The skill has three phases. Each can be invoked independently:

| Phase | Trigger | Output |
|-------|---------|--------|
| **Design** | `/design <name>` | `design-atlas.json` + stories |
| **Approve** | `/design <name> --approve` | Locks design, generates specs |
| **Scaffold** | `/design <name> --scaffold` | GitHub repo with code + manifests |

A typical flow runs all three, with human review between Design and Approve.

---

## Phase 1 — Design

Interactive discussion with the human to produce a design atlas.

### Step 1 — Understand requirements

Ask the human what this project does. Gather:
- **Purpose** — what problem does it solve?
- **Inputs/outputs** — what data comes in, what goes out?
- **External dependencies** — does it need a database, message queue, external API?
- **Scale expectations** — single instance or horizontally scaled?
- **Constraints** — language preference, framework requirements, timeline?

Don't ask all at once. Start with purpose and inputs/outputs, infer the rest, confirm.

### Step 2 — Read infrastructure context

Read the infra atlas for cluster awareness:
```bash
cat $AGENT_PROJECT_DIR/memory/global/infra-atlas.json
```

Key sections to extract:
- `environments.dev.services` — what's already available (Kafka, Postgres, etc.)
- `new_workload_contract` — requirements the project must satisfy
- `platform.kafka.topics` — existing topic layout
- `networking` — how services communicate

If infra-atlas.json doesn't exist, ask charon to run `/survey` first.

### Step 3 — Select patterns

Based on requirements + available infrastructure, select architectural patterns from the concept catalog.

For each candidate pattern:
1. Read `memory/global/concepts/<pattern>/concept.md` — verify it fits
2. Check if it has `monitoring.md`, `testing.md`, `deployment.md` — note what's available

Group patterns by concern:
- **Structural** — how the code is organized (hexagonal, CQRS, microkernel)
- **Communication** — how it talks to other services (consumer-group, webhook, API gateway)
- **Resilience** — how it handles failure (circuit-breaker, retry, dead-letter-queue)
- **Data** — how it stores/processes data (event-sourcing, cache-aside, saga)
- **Security** — how it authenticates/authorizes (API key, JWT, OAuth)

Present pattern choices to the human with one-sentence rationale for each. Let them add, remove, or substitute.

### Step 4 — Produce design atlas

Generate `design-atlas.json` in the same schema as the analyze skill's `atlas.json` (v4), but for a system that doesn't exist yet:

- **components** — proposed modules/services with descriptions
- **patterns** — selected patterns with confidence=1.0 (chosen, not detected)
- **flows** — designed data flows between components
- **dependencies** — both internal (between components) and external (Kafka, Postgres)
- **failure_modes** — anticipated failures based on selected patterns' deployment.md
- **debt** — empty (no debt in a new design)
- **domain_model** — the core data shape
- **metadata.analysis_mode** — `"design"` (not full/incremental/skip)
- **metadata.status** — `"draft"` (not yet approved)

Also generate stories using the same story schema as analyze — root stories per component group, child stories for key flows and design decisions. Include rationale blocks explaining why each pattern was chosen.

Write to `$MEM/design-atlas.json` and `$MEM/stories/`.

### Step 5 — Present for review

Report the design to the human:

```
## Design: <project-name>

**Purpose**: <one sentence>
**Components** (N): <names>
**Patterns** (N): <names with rationale>
**Flows** (N): <names>
**External dependencies**: <list with endpoints from infra-atlas>
**New infrastructure needed**: <anything not in infra-atlas> or "none"

### Review

The design atlas is at: $MEM/design-atlas.json
View it at: <docs-site-url>/projects/<name> (if docs site is configured)

Review the components, flows, and pattern choices. Then:
- To approve and generate specs: `/design <name> --approve`
- To modify: tell me what to change
```

---

## Phase 2 — Approve

Lock the design and generate handoff specs for other agents.

### Step 1 — Read the design atlas

Read `$MEM/design-atlas.json`. Verify `metadata.status` is `"draft"`.

### Step 2 — Generate monitoring spec

For each selected pattern that has a `monitoring.md` file:
1. Read `memory/global/concepts/<pattern>/monitoring.md`
2. Extract metrics, alerts, and dashboard guidance

Combine into `$MEM/monitoring-spec.yaml`:

```yaml
version: "1"
project: <name>
generated_from: design-atlas.json
metrics:
  - name: <metric_name>
    type: counter|gauge|histogram
    labels: [<labels>]
    source_pattern: <pattern-name>
    description: <from monitoring.md>
alerts:
  - name: <alert_name>
    condition: <from monitoring.md>
    severity: critical|warning
    source_pattern: <pattern-name>
dashboards:
  - name: <dashboard_name>
    panels: [<metric references>]
```

### Step 3 — Generate deployment spec

For each selected pattern that has a `deployment.md` file:
1. Read `memory/global/concepts/<pattern>/deployment.md`
2. Extract rollout implications and pre-deploy checklist items

Combine with `new_workload_contract` from infra-atlas into `$MEM/deployment-spec.yaml`:

```yaml
version: "1"
project: <name>
generated_from: design-atlas.json
contract:
  # from infra-atlas new_workload_contract
  health: { readiness: "GET /health", liveness: "GET /health" }
  metrics: { endpoint: "/metrics", format: "prometheus" }
  logging: { output: "stdout", format: "json" }
  labels: { app: <name> }
rollout_concerns:
  - pattern: <pattern-name>
    concern: <from deployment.md>
    pre_deploy_check: <from deployment.md>
resources:
  requests: { cpu: "100m", memory: "256Mi" }
  limits: { memory: "1Gi" }
```

### Step 4 — Generate test spec

For each selected pattern that has a `testing.md` file:
1. Read `memory/global/concepts/<pattern>/testing.md`
2. Extract test categories (unit, integration, failure injection)

Combine into `$MEM/test-spec.yaml`:

```yaml
version: "1"
project: <name>
generated_from: design-atlas.json
test_suites:
  - name: <pattern-name>
    unit_tests:
      - description: <from testing.md>
    integration_tests:
      - description: <from testing.md>
    failure_injection:
      - description: <from testing.md>
```

### Step 5 — Lock design

Update `design-atlas.json`: set `metadata.status` to `"approved"`.

Report:
```
## Design Approved: <project-name>

Specs generated:
  monitoring-spec.yaml — N metrics, N alerts
  deployment-spec.yaml — N rollout concerns, contract from infra-atlas
  test-spec.yaml — N test suites

Next: `/design <name> --scaffold` to generate code and create repo.
```

---

## Phase 3 — Scaffold

Generate actual code and create a GitHub repo.

### Step 1 — Read approved design

Read `$MEM/design-atlas.json`. Verify `metadata.status` is `"approved"`.
Read `$MEM/monitoring-spec.yaml`, `deployment-spec.yaml`, `test-spec.yaml`.

### Step 2 — Generate project structure

Based on the design atlas components and patterns, generate:

```
<project-name>/
  README.md                 — purpose, architecture overview, getting started
  Dockerfile                — multi-stage build, matches infra-atlas contract
  kustomize/
    base/
      deployment.yaml       — from deployment-spec + new_workload_contract
      service.yaml
      kustomization.yaml
  src/                      — source code stubs per component
    <component>/
      __init__.py (or index.ts, main.go — based on language choice)
  tests/                    — test stubs from test-spec
    test_<pattern>.py
  monitoring/
    dashboards/             — Grafana dashboard JSON stubs from monitoring-spec
    alerts.yaml             — Prometheus alert rules from monitoring-spec
  .github/
    workflows/              — CI stub (build + test)
```

The source stubs implement interfaces and patterns from the design but leave business logic as TODOs. Each stub references the pattern it implements.

### Step 3 — Create GitHub repo

```bash
gh repo create <owner>/<project-name> --private --description "<purpose>"
cd /tmp/<project-name>
git init && git add -A && git commit -m "Initial scaffold from augur /design"
git remote add origin <repo-url>
git push -u origin main
```

### Step 4 — Delegate deployment

Produce a job for charon:
```bash
curl -s http://job-router.kord.svc.cluster.local:3100/api/delegate \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "charon",
    "prompt": "Deploy <project-name> to dev namespace",
    "project": "<project-name>",
    "repo": "<repo-url>"
  }'
```

### Step 5 — Report

```
## Scaffold: <project-name>

**Repo**: <github-url>
**Components**: N source stubs
**Tests**: N test stubs
**Manifests**: kustomize base ready
**Monitoring**: N dashboard stubs, N alert rules

Deployed to dev: <charon result>

### Next steps for the developer
1. Clone the repo: `git clone <url>`
2. Implement TODOs in src/ (business logic)
3. Run tests locally: `<test command>`
4. Push → tell charon to redeploy

### For sauron
monitoring-spec.yaml is ready at: $MEM/monitoring-spec.yaml
Run: delegate to sauron "Implement monitoring for <name>"

### For charon (future deploys)
deployment-spec.yaml with rollout concerns at: $MEM/deployment-spec.yaml
```

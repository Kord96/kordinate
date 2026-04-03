---
name: design
description: >
  Design a new project: structured top-down discussion with human, pattern selection
  from concept catalog by abstraction level, design atlas for visual review, then
  scaffold generation with monitoring/deployment/test specs for other agents.
argument-hint: "<project-name> [--approve] [--scaffold]"
context: inherit
---

Design a new project through a structured, top-down process. Decisions flow from
architecture style down to implementation patterns. Each level constrains the next.
The concept catalog (265 patterns, 80 monitoring guides, 160 testing guides, 58
deployment guides) informs every choice.

## Arguments

`$ARGUMENTS` — Required: `<project-name>`. Optional:
- `--approve` — approve existing design, generate agent handoff specs
- `--scaffold` — generate code scaffold and create GitHub repo

## Phases

| Phase | Trigger | Output |
|-------|---------|--------|
| **Design** | `/design <name>` | `design-atlas.json` + stories |
| **Approve** | `/design <name> --approve` | monitoring/deployment/test specs |
| **Scaffold** | `/design <name> --scaffold` | GitHub repo with stubs + manifests |

---

## Phase 1 — Design

Structured discussion with the human, working top-down through six decision levels.
Each level narrows the options for the next. Present choices with rationale, confirm
with the human before moving on.

### Step 1 — Read context

Before any questions, silently read:

1. **Infra atlas** — `$AGENT_PROJECT_DIR/memory/global/infra-atlas.json`
   - What services exist in dev (Kafka, Postgres, etc.)
   - The `new_workload_contract` (metrics, logging, health, packaging requirements)
   - If missing, ask charon to run `/survey` first

2. **Concept indexes** — `memory/global/concepts.md` and `memory/global/anti-patterns.md`
   - Know the full catalog before advising

### Step 2 — Understand purpose

Ask the human ONE focused question:

> "What does this service do? Describe the core job in 1-2 sentences."

From their answer, infer:
- Is it a service, library, CLI tool, or pipeline?
- Does it process events, serve APIs, transform data, or orchestrate work?
- What enters and what leaves?

Summarize your understanding and confirm before proceeding.

### Step 3 — Decision levels

Work through each level in order. At each level, present your recommendation with
rationale, then confirm. Don't dump all levels at once — one level per exchange.

---

#### Level 1: Architecture style (constrains everything)

Based on the purpose, recommend ONE primary architecture style:

| If the service... | Recommend | Concept |
|-------------------|-----------|---------|
| Has a clear domain with complex business rules | Hexagonal / Clean Architecture | hexagonal |
| Reacts to events from other services | Event-driven architecture | event-driven |
| Exposes a CRUD API with simple logic | Layered / MVC | layered |
| Orchestrates multiple services | Orchestrator / Saga coordinator | saga |
| Is a reusable library | Module / Package structure | (no concept) |
| Processes data in batches | Pipeline / ETL | batch-processing |

**Ask**: "I recommend [style] because [reason]. Does this fit, or do you see it differently?"

---

#### Level 2: Domain model (what's the core data shape?)

Based on the architecture style, recommend the domain model approach:

| If level 1 is... | Options | Key question for human |
|-------------------|---------|----------------------|
| Hexagonal | Aggregate + entities, or simple repository | "Is the data model complex enough for aggregates, or is a flat repository sufficient?" |
| Event-driven | Event sourcing vs state-based | "Should we reconstruct state from events, or just store current state?" |
| Layered | Active record vs repository | "Simple data-object mapping, or explicit repository layer?" |
| Pipeline | Stream transforms vs batch | "Continuous stream processing or batch windows?" |

Read `memory/global/concepts/<chosen>/concept.md` to inform the recommendation.

---

#### Level 3: Communication (how data enters and leaves)

Based on the purpose and available infrastructure from infra-atlas:

**Inbound** — how data arrives:
- REST API (`api-gateway`, `rest-api`)
- Kafka consumer (`consumer-group`) — available at `kafka-kafka-bootstrap.dev.svc.cluster.local:9092`
- gRPC (`grpc`)
- Webhook receiver (`webhook`)
- Scheduled/cron (`batch-processing`)

**Outbound** — how results leave:
- Kafka producer
- API calls to other services
- Database writes
- Webhook dispatch

For each external service the project calls, note it — this feeds Level 4.

**Ask**: "This service receives [X] via [method] and produces [Y] via [method]. I see [service Z] is available in dev from the infra atlas. Sound right?"

---

#### Level 4: Resilience (derived from Level 3)

For each external dependency identified in Level 3, recommend resilience patterns.
This level is mostly automated — don't ask the human for each one, just present the package:

| External dependency type | Implied patterns |
|--------------------------|-----------------|
| HTTP API call | circuit-breaker, retry, timeout |
| Database | connection-pool, retry |
| Kafka consumer | dead-letter-queue, idempotent-consumer |
| Kafka producer | retry, outbox (if exactly-once needed) |
| Cache | cache-aside, fallback-on-miss |
| External webhook | retry, circuit-breaker |

For each recommended pattern, read its `concept.md` briefly to verify fit.

**Present** (don't ask per-pattern): "For resilience, I'm including: [list with one-line reasons]. Any you'd remove or add?"

---

#### Level 5: Data storage (derived from Levels 2 and 3)

Based on the domain model and communication patterns:

| If... | Storage recommendation |
|-------|----------------------|
| Event sourcing | Event store (Kafka topics or dedicated store) + snapshots |
| Simple CRUD | PostgreSQL with repository pattern |
| High-read, low-write | PostgreSQL + Redis cache-aside |
| Stream processing | Kafka state stores or DuckDB |
| Config/metadata only | ConfigMap or environment variables |

Check infra-atlas: is the recommended storage already available in dev?
If not, note it as "new infrastructure needed — charon will provision."

**Ask**: "For storage I recommend [X]. [It's already available in dev / We'll need charon to set up X]. Good?"

---

#### Level 6: Cross-cutting (always asked)

Quick decisions on standard concerns:

| Concern | Question | Default |
|---------|----------|---------|
| Auth | "Does this service need authentication? If so: API key, JWT, or OAuth?" | None for internal services |
| Feature flags | "Need feature flags for gradual rollout?" | No |
| Distributed tracing | "Part of a multi-service flow that needs tracing?" | Yes if >1 service interaction |

---

### Step 4 — Compile pattern set

After all levels, compile the final pattern list. For each selected pattern:

1. Read `memory/global/concepts/<pattern>/concept.md` — extract the summary
2. Check for `monitoring.md` → flag for monitoring spec
3. Check for `testing.md` → flag for test spec
4. Check for `deployment.md` → flag for deployment spec

Present the complete list:

```
## Selected Patterns

| # | Pattern | Level | Has Monitoring | Has Tests | Has Deploy |
|---|---------|-------|----------------|-----------|------------|
| 1 | hexagonal | architecture | ✓ | ✓ | ✓ |
| 2 | consumer-group | communication | — | ✓ | — |
| 3 | circuit-breaker | resilience | ✓ | ✓ | ✓ |
| ... |
```

### Step 5 — Produce design atlas

Generate `design-atlas.json` in atlas v4 schema:

- **components** — proposed modules based on architecture style
- **detected_patterns** — all selected patterns with `confidence: 1.0`, `source: "design"`
- **flows** — designed data flows from Level 3 decisions
- **external_dependencies** — from Level 3, with endpoints from infra-atlas
- **failure_modes** — from Level 4 resilience patterns + deployment.md files
- **domain_model** — from Level 2
- **debt** — empty (score: 0, grade: A)
- **metadata.analysis_mode** — `"design"`
- **metadata.status** — `"draft"`
- **metadata.patterns_with_monitoring** — list of patterns that have monitoring.md
- **metadata.patterns_with_tests** — list of patterns that have testing.md
- **metadata.patterns_with_deployment** — list of patterns that have deployment.md
- **metadata.new_infrastructure** — list of services not in infra-atlas that charon needs to provision

Also generate stories — same schema as /analyze output:
- Root stories per component group
- Child stories for key flows and design decisions
- Rationale blocks explaining why each pattern was chosen, citing concept.md

Write to `$MEM/design-atlas.json` and `$MEM/stories/`.

### Step 6 — Present for review

```
## Design: <project-name>

**Purpose**: <one sentence>
**Architecture**: <level 1 choice>
**Components** (N): <names>
**Patterns** (N): <names grouped by level>
**Flows** (N): <names>
**External deps**: <list with endpoints from infra-atlas>
**New infrastructure needed**: <list for charon> or "none"

Design atlas: $MEM/design-atlas.json
Stories: $MEM/stories/

Review, then:
- To approve: `/design <name> --approve`
- To change: tell me what to modify
```

---

## Phase 2 — Approve

Lock the design and generate agent handoff specs.

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
contract:
  # from infra-atlas new_workload_contract.observability
  endpoint: /metrics
  format: prometheus
  logging: { output: stdout, format: json, fields: [level, component, event, timestamp] }
metrics:
  - name: <metric>
    type: counter|gauge|histogram
    labels: [<labels>]
    pattern: <source pattern>
    description: <from monitoring.md>
alerts:
  - name: <alert>
    condition: <from monitoring.md>
    severity: critical|warning
    pattern: <source pattern>
dashboards:
  - name: <dashboard>
    panels: [<metric references>]
```

### Step 3 — Generate deployment spec

For each pattern in `metadata.patterns_with_deployment`:
1. Read `memory/global/concepts/<pattern>/deployment.md`
2. Extract rollout implications and pre-deploy checklist

Write `$MEM/deployment-spec.yaml`:
```yaml
version: "1"
project: <name>
source: design-atlas.json
contract:
  # from infra-atlas new_workload_contract
  health: { readiness: "GET /health", liveness: "GET /health" }
  labels: { app: <name> }
  image: localhost:30500/<name>:latest
  manifests: kustomize
rollout_concerns:
  - pattern: <pattern>
    concern: <from deployment.md>
    pre_deploy: <checklist item>
new_infrastructure:
  # from metadata.new_infrastructure
  - service: <name>
    type: <postgres|redis|etc>
    action: "charon to provision"
```

### Step 4 — Generate test spec

For each pattern in `metadata.patterns_with_tests`:
1. Read `memory/global/concepts/<pattern>/testing.md`
2. Extract test categories and specific test cases

Write `$MEM/test-spec.yaml`:
```yaml
version: "1"
project: <name>
source: design-atlas.json
suites:
  - pattern: <pattern>
    unit:
      - <test description from testing.md>
    integration:
      - <test description>
    failure_injection:
      - <test description>
```

### Step 5 — Lock

Update `design-atlas.json`: `metadata.status` → `"approved"`.

```
## Approved: <project-name>

Specs:
  monitoring-spec.yaml — N metrics, N alerts → sauron
  deployment-spec.yaml — N rollout concerns → charon
  test-spec.yaml — N test suites → developer

Next: `/design <name> --scaffold`
```

---

## Phase 3 — Scaffold

Generate code and create the repo.

### Step 1 — Verify

Read `$MEM/design-atlas.json` (`metadata.status` must be `"approved"`).
Read all three spec files.

### Step 2 — Generate project

Based on the design atlas, generate:

```
<name>/
  README.md              purpose, architecture, patterns, getting started
  Dockerfile             multi-stage, satisfies new_workload_contract
  kustomize/
    base/
      deployment.yaml    from deployment-spec + contract
      service.yaml
      kustomization.yaml
  src/                   code stubs per component
  tests/                 test stubs from test-spec
  monitoring/
    dashboards/          Grafana JSON from monitoring-spec
    alerts.yaml          Prometheus rules from monitoring-spec
```

Source stubs implement the selected patterns' interfaces with TODO placeholders
for business logic. Each file references which pattern it implements.

### Step 3 — Create repo

```bash
gh repo create <owner>/<name> --private --description "<purpose>"
```

Push initial scaffold.

### Step 4 — Deploy

Delegate to charon:
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

Next steps:
  Developer: clone, implement TODOs, push
  Sauron: delegate "implement monitoring for <name>" with monitoring-spec
  Charon: redeploy after code changes via /roll
```

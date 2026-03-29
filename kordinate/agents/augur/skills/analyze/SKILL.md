---
name: analyze
description: >
  Full project analysis: atlas.json (structural inventory with detected concepts, dependencies,
  API surface, and debt) + stories (scoped narrative compositions about architectural concerns).
  One coherent pass. Use when asked to understand architecture, audit a codebase, onboard to a
  project, or before cross-cutting changes. Use --detect-only for just the atlas.
argument-hint: "<project> [--reverse] [--detect-only]"
context: fork
curated: true
scope: global
---

Produce `atlas.json` and stories — a complete architectural understanding of a project in one continuous pass. Phase 1 runs all detection methodologies. Phase 2 composes findings into stories. Both phases share context so detection informs composition directly.

## Arguments

`$ARGUMENTS` — Required: `<project>`. Optional: `[--reverse]` to scan sibling projects for inbound dependency references; `[--detect-only]` to produce only atlas.json (skip story composition). Directory must exist at `~/<project>/`, `~/repos/<project>/`, `~/test-repos/<project>/`, or as an absolute path.

---

## Phase 1 — Detect

Run all detection methodologies in one pass. Output: atlas.json.

### Step 1 — Locate, scan, and gather sources

Resolve the project directory (call it `$ROOT`). Check paths in order: `~/<project>/`, `~/repos/<project>/`, `~/test-repos/<project>/`; if `$ARGUMENTS` is an absolute path, use it directly. If not found, report which paths were checked and exit.

If found but empty or has no source files, produce a minimal atlas.json with just `project`, `purpose: "Empty or scaffold"`, and empty sections.

Detect the stack: **languages** from package manifests; **frameworks** from dependency lists + [frameworks.md](frameworks.md); **runtime** from Dockerfile/Procfile/entry point. Glob `$ROOT` for source files per [extractors.md](extractors.md). Read the concept catalogs: abstractions index, concepts index, anti-patterns index. For `concept` fields on `state` and `external_dependencies`, use the infrastructure terms listed in [schema.md](schema.md).

### Step 2 — Detect concepts

Run the concept catalog scan inline per [detection.md](detection.md): Pass 1 (batch grep per category), Pass 2 (ast-grep/semgrep rules), Pass 3 (manual signature verification), Pass 3.5 (diagnostic question evaluation). Assess confidence per concept. Identify gaps (external calls without resilience, stack-implied patterns, catalog cross-references). Hold results — they feed into steps 5-7.

### Step 3 — Map dependencies

Inline dependency analysis per [dep-analysis.md](dep-analysis.md). Discover internal modules, trace imports, detect external services from client libraries and ORM schemas, scan infrastructure manifests, discover inter-service config references, flag circular dependencies and hub modules. If `--reverse`, scan sibling projects for inbound references. Hold results.

### Step 4 — Review API surface

Inline API review per [api-review.md](api-review.md). Detect web framework(s) using [frameworks.md](frameworks.md). Discover all route/endpoint definitions with auth and validation columns. Run the REST hygiene checklist (7 concerns). Assess gateway pattern and hexagonal architecture compliance. Handle non-REST styles (GraphQL, gRPC, WebSocket, SSE). Hold results.

### Step 5 — Identify components and groups

Using all intermediate state from steps 2-4, identify **5-10 top-level components** per [guidance.md](guidance.md). Annotate each component with: detected patterns (step 2), dependency info (step 3), and API endpoints (step 4). Use `children` to nest sub-components.

**Assign components to 3-5 groups.** Groups are structural clusters — runtime boundaries (Server, Browser, External), not code modules. This is a hard constraint. If you have >5 groups, merge the two most closely related. If <3, the project may be too small for grouping. Small projects (<15 nodes) aim for 3 groups. Synthetic `external` and `actors` groups count toward the limit. See [guidance.md](guidance.md) for group assignment rules.

Map relationships grounded in actual code. Shared utility imports are incidental coupling, not architectural relationships.

### Step 6 — Map actors, flows, events, state, and external dependencies

Identify external actors (users, services, cron, data sources). Trace **2-4 critical data flows** — not every code path. Map events (omit if none). Catalog state stores with concept vocabulary from [dep-analysis.md](dep-analysis.md), including `readers` and `writers` arrays. Catalog external dependencies with criticality and resilience assessment informed by concept detection from step 2.

### Step 7 — Failure modes and debt assessment

For each external dependency and stateful component, trace cascading failures: what breaks, cascade, user impact, detection, recovery, severity. For detection signals: look for existing metrics, health checks, log patterns in code; write `"none"` if absent.

Then run debt assessment inline per [debt.md](debt.md): load anti-patterns from detected concept files, scan for violations, calculate score and grade (A-F with hard floor rule), categorize, prioritize 3-7 recommendations. Failure modes and debt share a natural boundary — a missing resilience pattern is both a failure mode and a debt item.

### Step 8 — Gemini review (background)

Feed the draft atlas and project source to Gemini:
```bash
gemini -m gemini-2.5-pro -o json -p "Review this atlas.json against the source code. Flag: missing components, incorrect dependency edges, missed failure modes, concept detection false positives, severity misclassifications in debt, API findings that were missed, group coherence (are the 3-5 groups natural?). Be specific." @$ROOT/ < /tmp/atlas-draft.json > /tmp/gemini-review-atlas.json &
```
Continue to step 9 immediately.

### Step 9 — Write atlas.json

Assemble all findings into [schema.md](schema.md) v3 format. Set `version: "3"` and `generated` to today's date. Incorporate valid Gemini critiques if available. Write to `$ROOT/.kord/agents/augur/memory/atlas.json` (create directory if needed).

If `--detect-only`: skip Phase 2, go directly to step 14 (Report).

---

## Phase 2 — Compose Stories

With all Phase 1 findings in context, compose stories per [story-schema.md](story-schema.md). Each story is a scoped analytical unit about one architectural concern.

### Step 10 — Compose stories

Work through each story type:

**a. Structure stories** (one per group, 3-5 total): For each group, write a structure story explaining how the group's components are organized, their relationships, and why this grouping exists. Pull from: component descriptions, dependency edges, detected patterns, group membership.

**b. Flow stories** (one per critical data flow, 2-4 total): For each flow in atlas `data_flows`, trace the path from trigger to terminal state. Pull from: flow steps, component descriptions, technology annotations, API findings on endpoints in the path.

**c. Data stories** (one per significant state cluster): For each entry in atlas `state` (or cluster of related entries sharing readers/writers), explain where truth lives, what reads and writes it, and the consistency model. Pull from: state entries, reader/writer references, persistence model, related debt findings.

**d. Resilience stories** (one per critical failure cluster): For related failure modes (sharing a component or cascade path), explain what breaks, the cascade, detection, and recovery. Pull from: failure modes, external dependency resilience, detected resilience patterns and gaps, debt findings in the Resilience category.

**e. Highlight stories** (optional): For findings that stand out — exemplary patterns, unusual choices, critical cross-cutting gaps — write a highlight story. These are for findings that don't fit neatly into structure/flow/data/resilience.

Stories are **short orienting sections**, not essays. Each narrative is 1-2 paragraphs that orient the reader and point to the structural evidence (nodes, edges, steps, observations). The detail lives in the structure, not the prose. Follow [story-schema.md](story-schema.md) for length targets and formatting.

### Step 11 — Selective re-read (Detect-Compose-Refine)

Review each draft story. If a narrative makes a claim about code behavior that was not directly observed in Phase 1 (e.g., a flow story describes error handling but that path wasn't traced), re-read the specific source file(s) to verify or correct the claim.

Do not re-scan broadly — only the specific files that an ungrounded claim references. This keeps the refinement targeted.

### Step 12 — Evaluate stories

For each story, compute:

- **Groundedness**: count claims (every sentence asserting code behavior). For each, verify it maps to (a) a detection finding in the atlas and (b) an atlas node ID. `groundedness = grounded / total`. Target: >= 0.85. If below, revise ungrounded claims.
- **Coverage** (across all stories): percentage of critical atlas nodes (components + external deps with criticality=critical + state with purpose=source-of-truth) referenced in at least one story. Target: >= 0.80. If below, add highlight stories for uncovered critical components.

Record scores in each story's `evaluation` section.

### Step 13 — Compose journeys

Group stories into 2-4 journeys per [story-schema.md](story-schema.md). Each journey is an ordered reading path for a specific audience:

- **Architecture overview** (always): all structure stories → 1-2 key flows. For new team members.
- **Backend onboarding** (if applicable): server structure → request flow → persistence → resilience.
- **Frontend onboarding** (if applicable): client structure → rendering flow → state management.
- **Resilience review** (if failure modes exist): all resilience stories → gap highlights.

Keep journeys to 3-8 stories each. The first story should always be a structure story.

### Step 14 — Write stories and journeys

Write stories to `$ROOT/.kord/agents/augur/memory/stories/<type>-<id>.yaml`. Write journeys to `$ROOT/.kord/agents/augur/memory/journeys/<id>.yaml`. Create directories if needed. Update `metadata.story_ids` in atlas.json.

---

## Step 15 — Report

```
## Analysis: <project>

**Purpose**: <one sentence>
**Components** (N): <names>
**Groups** (N): <names>
**Flows** (N): <names>
**Concepts**: N patterns, N anti-patterns, N gaps
**API**: N endpoints, N critical / N recommended / N minor findings
**Debt**: Score N — Grade X. <interpretation>
**External** (N): <names with criticality>
**Failures** (N): <names with severity>
**Stories** (N): N structure, N flow, N data, N resilience, N highlight
**Journeys** (N): <names>
**Groundedness**: <min>-<max> across stories
**Coverage**: <percentage> of critical components
**Top recommendations**: 1. ... 2. ... 3. ...

Written to:
  atlas: <path>
  stories: <path> (N files)
  journeys: <path> (N files)
```

If `--detect-only`, omit the Stories/Groundedness/Coverage lines and the stories path.

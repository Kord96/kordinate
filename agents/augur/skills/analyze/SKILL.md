---
name: analyze
description: >
  Full project analysis: facts/ (normalized extracted observations), atlas.json (structural
  inventory with detected concepts, dependencies, API surface, and debt) + stories (scoped
  narrative compositions about architectural concerns). One coherent pass. Use when asked to
  understand architecture, audit a codebase, onboard to a project, or before cross-cutting
  changes. Use --detect-only for just facts + atlas.
argument-hint: "<project> [--reverse] [--detect-only]"
context: inherit
---

Produce `facts/`, `atlas.json`, and stories — a complete architectural understanding of a project in one continuous pass. Phase 1 runs deterministic extraction and concept inference. Phase 2 composes findings into stories. Both phases share context so extraction informs composition directly.

Supports three analysis modes: **full** (first run or major changes), **incremental** (update existing atlas based on what changed), and **skip** (nothing changed). The mode is determined automatically.

## Arguments

`$ARGUMENTS` — Required: `<project>`. Optional: `[--reverse]` to scan sibling projects for inbound dependency references; `[--detect-only]` to produce only atlas.json (skip story composition); `[--full]` to force full analysis (ignore previous results). Directory must exist at the path provided in `[Memory] Project code:`, or at `~/<project>/`, `~/repos/<project>/`, `~/test-repos/<project>/`, `/kord/repos/<project>/`, or as an absolute path.

**Memory paths:** The runner injects `[Memory]` context with each job. Use the `Project:` path for reading/writing project memory (facts, atlas, stories). If no project memory path is provided, fall back to `$AGENT_PROJECT_DIR/memory/projects/<project>/`. Output is written via the `/memory-update` endpoint for insights, but `facts/`, atlas.json, and stories are written directly to the project memory path (they are structured output, not curated memory).

---

## Step 0 — Determine Analysis Mode

Before reading any code, decide whether to run a full analysis or an incremental update.

### 0.1 — Locate and check previous analysis

Resolve the project directory (`$ROOT`) and the project memory directory (`$MEM` — from the runner's `[Memory] Project:` path, or `$AGENT_PROJECT_DIR/memory/projects/<project>/`). Check for existing output at `$MEM/atlas.json` and `$MEM/facts/index.json`.

If `--full` was passed, or no previous atlas exists: **mode = FULL**. Skip to Phase 1.

### 0.2 — Compute the diff (deterministic)

Read `metadata.analyzed_at_sha` from the existing atlas. Compare against current HEAD:

```bash
PREV_SHA=$(jq -r '.metadata.analyzed_at_sha // empty' $MEM/atlas.json)
CURRENT_SHA=$(git -C $ROOT rev-parse HEAD)
```

If `$PREV_SHA` is empty or doesn't exist in git history: **mode = FULL**.
If `$PREV_SHA == $CURRENT_SHA`: **mode = SKIP** — nothing changed. Report "Atlas is current at SHA $CURRENT_SHA. No changes." and **exit immediately**. Do NOT read any source files, do NOT verify references, do NOT refine the atlas. Just report and stop.

Otherwise, get the diff:

```bash
git -C $ROOT diff --stat $PREV_SHA..HEAD
git -C $ROOT diff --name-only $PREV_SHA..HEAD > /tmp/changed-files.txt
```

### 0.3 — Map changes to components (deterministic)

Cross-reference changed files against the existing atlas's `components[].modules[]` arrays:

For each changed file, find which component(s) it belongs to. Classify:

| Category | Detection | Files |
|----------|-----------|-------|
| **Mapped** | File matches a component's `modules[]` | Component is affected |
| **Unmapped** | File doesn't match any component | Potential new component |
| **Peripheral** | Only docs, tests, config, CI files changed | Low architectural impact |
| **Dependency** | Package manifests changed (package.json, go.mod, etc.) | Re-run dependency detection |
| **Schema** | Migration or schema files changed | Re-analyze state section |
| **Deleted** | File removed | Check if component still resolves |

Build the **affected set**: all directly changed components + their dependents (walk `depends_on` edges one level).

### 0.4 — Decide mode

| Condition | Mode | What happens |
|-----------|------|-------------|
| 0 files changed | **SKIP** | Report "atlas is current", exit |
| Only peripheral files | **SKIP** | Or **PATCH** if devex/CI section needs updating |
| Unmapped files exist (potential new components) | **FULL** | Can't incrementally add components — topology might change |
| Affected set >= 50% of components | **FULL** | Too much changed, incremental isn't cheaper |
| Affected set < 50% of components | **INCREMENTAL** | Update only what changed |

Report the decision: "Mode: INCREMENTAL — 3 of 8 components affected (api-client, auth-service, config-loader). 12 files changed since abc123."

---

## Phase 1 — Understand the Codebase

### FULL mode

Delete previous output. Read the entire codebase and build a holistic understanding from scratch.

### INCREMENTAL mode

Read the existing atlas and facts. Then read **only** the changed files and the files belonging to affected components. The existing atlas provides context for unchanged components, and existing facts provide reusable normalized evidence — don't re-analyze them.

**What to re-run for affected components:**
- Re-run fact extractors for affected domains and changed files only
- Re-scan changed files with AST rules and signatures where facts need refresh
- Re-evaluate concept detection only for concepts found in affected components or derived from changed facts
- Re-check depends_on edges for affected components (imports may have changed)
- Re-trace flows that pass through affected components
- Re-assess debt for affected components only
- Keep unchanged components, flows, state, and failure modes as-is

**What to always re-check even in incremental:**
- Facts whose source files moved or were deleted
- `grounded_in` references on affected components (files may have moved)
- External dependency resilience if dependency code changed
- API surface if route handler files changed

---

### Step 1 — Locate and gather

Resolve the project directory (`$ROOT`). If not found, report and exit. If empty, produce minimal atlas.json.

Detect the stack (languages, frameworks via `memory/catalog/frameworks/index.md`, runtime). In **INCREMENTAL** mode, only glob changed files + affected component files per [concerns/source-gathering.md](concerns/source-gathering.md). In **FULL** mode, glob everything. Load the semantic index layer from `memory/indexes/` and use the detector execution plan from `bundles/detectors/execution-plan.json` as the deterministic detection entrypoint:

```text
framework detection -> fact extraction -> concept inference -> atlas synthesis
```

### Step 2 — Read and analyze

Read the source code. As you build your understanding, cover all concerns below. They inform each other — don't treat them as separate passes. Read each reference doc **when you reach that concern**, not upfront.

**Completeness checklist:**

- **Facts** — Framework-first deterministic extraction, then fact normalization: framework bundles → fact extractor bundles → per-domain normalized outputs. Facts are the stable interface of the lower layer. Write them to `$MEM/facts/` following `schemas/facts-schema.md`.
- **Patterns and concepts** — Framework-first semantic inference over facts: prioritized concept bundles → signatures/policies → diagnostic questions. Assess confidence and identify gaps. Use semantic catalogs in `memory/catalog/` for interpretation, and prefer bundled detector execution from `bundles/detectors/` so `/analyze` follows one consistent evidence pipeline. Questions belong after facts and before concept confirmation. When starting this: read [concerns/detection.md](concerns/detection.md).
- **Dependencies** — Internal modules, imports, external services, infra manifests, inter-service config. Flag circular deps and hub modules. If `--reverse`, scan siblings. When starting this: read [concerns/dependency-analysis.md](concerns/dependency-analysis.md).
- **API surface** — Framework detection, route discovery, 7 REST hygiene concerns, gateway/hexagonal compliance. Non-REST styles. Frameworks are stack context, not concepts; use them to choose framework-native expectations and then map architectural concepts separately. When starting this: read [concerns/api-review.md](concerns/api-review.md) and `memory/catalog/frameworks/index.md`.
- **Components** — 5-10 top-level, nested via children. Annotate with patterns, deps, endpoints. Assign to 3-5 groups. When starting this: read [concerns/source-gathering.md](concerns/source-gathering.md).
- **Actors and flows** — External actors. 2-4 critical data flows. Events (omit if none). When writing atlas: read [schema.md](schema.md).
- **Domain model** — Identify the project's core data shape by examining schemas, models, and data stores. Use `category: domain-model` concepts from the catalog for detection signals. Most projects have one primary model (e.g., property-graph, ledger, catalog). Record it as `domain_model` in the atlas.
- **State** — Stores with concept vocabulary, readers/writers, persistence model.
- **Failure modes** — ALL possible failures for every external dep and stateful component, both covered and uncovered. For each failure linked to a detected pattern, use concept semantics — especially review checklists, anti-patterns, and signatures — plus detector-side policy/signature guidance where relevant. Uncovered failures get empty signals — debt references them.
- **Debt** — Anti-patterns from detected concepts, violations, score/grade (A-F, hard floor rule), 3-7 prioritized recommendations. When scoring: read [concerns/debt.md](concerns/debt.md).
- **Stories** — When composing stories: read [../../schemas/story-schema.md](../../schemas/story-schema.md) and [../../schemas/writing-guide.md](../../schemas/writing-guide.md).

### Step 3 — Write facts

Write normalized fact artifacts to `$MEM/facts/` following [../../schemas/facts-schema.md](../../schemas/facts-schema.md) v1 format.

Required first-pass domains:
- `frameworks`
- `routes`
- `models`
- `external-clients`
- `import-graph`

Preferred domains when evidence exists:
- `middleware`
- `config`
- `jobs`
- `events`

Each fact must include:
- detector provenance
- framework context
- source files
- confidence

### Step 4 — Write atlas.json

Assemble into [../../schemas/atlas-schema.md](../../schemas/atlas-schema.md) v4 format. Set `version: "4"`, `generated` to today, and `metadata.analyzed_at_sha` to the current git HEAD SHA. Set `metadata.analysis_mode` to the mode determined in Step 0. In **INCREMENTAL** mode, set `metadata.affected_components` to the list of components that were re-analyzed. Write to `$MEM/atlas.json`.

If `--detect-only`: skip Phase 2, go to Report.

---

## Phase 2 — Compose

With all Phase 1 findings in context, compose stories and journeys following [../../schemas/composition-guide.md](../../schemas/composition-guide.md). Read [../../schemas/story-schema.md](../../schemas/story-schema.md) for the YAML format.

### Step 6 — Refine (Detect-Compose-Refine)

Review each story. If a summary makes a claim not directly observed in Phase 1, re-read the specific source file(s) to verify or correct it. Only re-read files that an ungrounded claim references.

### Step 7 — Validate

Delegate to warden to validate your output. **You need a completion token to finish.**

Call warden via kord with your output directory. Warden runs the validator and returns either errors or a completion token.

If warden returns errors: read them, fix the output files, call warden again. Repeat until warden returns a **completion token**. Record it.

### Step 8 — Evaluate

With validated output, run quality checks:

1. **Groundedness**: for each observation with `grounded_in` references, re-read the cited source files and verify the claim holds. The code is ground truth, not the atlas. Target: >= 0.85.

2. **Coverage**: critical atlas nodes in at least one story / total critical nodes. Target: >= 0.80.

3. If groundedness is low, fix claims. If coverage is low, add stories. Always revalidate after changes.

---

## Step 9 — Report

```
## Analysis: <project>

**Mode**: full | incremental (N of M components) | skip
**Purpose**: <one sentence>
**Components** (N): <names>
**Groups** (N): <names>
**Flows** (N): <names>
**Concepts**: N patterns, N anti-patterns, N gaps
**API**: N endpoints, N critical / N recommended / N minor findings
**Debt**: Score N — Grade X. <interpretation>
**External** (N): <names with criticality>
**Failures** (N): <names with severity>
**Facts**: N total across <domain list>
**Stories**: N root, N child
**Journeys** (N): <titles> (if any)
**Groundedness**: <min>-<max> across stories
**Coverage**: <percentage> of critical components
**Validation token**: <token from warden>
**Top recommendations**: 1. ... 2. ... 3. ...

Written to:
  facts: <path> (domain files)
  atlas: <path>
  stories: <path> (N files)
  journeys: <path> (N files, if any)
```

If `--detect-only`, omit Stories/Journeys/Groundedness/Coverage/Validation lines.

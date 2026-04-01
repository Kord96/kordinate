---
name: analyze
description: >
  Full project analysis: atlas.json (structural inventory with detected concepts, dependencies,
  API surface, and debt) + stories (scoped narrative compositions about architectural concerns).
  One coherent pass. Use when asked to understand architecture, audit a codebase, onboard to a
  project, or before cross-cutting changes. Use --detect-only for just the atlas.
argument-hint: "<project> [--reverse] [--detect-only]"
context: inherit
---

Produce `atlas.json` and stories — a complete architectural understanding of a project in one continuous pass. Phase 1 runs all detection methodologies. Phase 2 composes findings into stories. Both phases share context so detection informs composition directly.

## Arguments

`$ARGUMENTS` — Required: `<project>`. Optional: `[--reverse]` to scan sibling projects for inbound dependency references; `[--detect-only]` to produce only atlas.json (skip story composition). Directory must exist at `~/<project>/`, `~/repos/<project>/`, `~/test-repos/<project>/`, or as an absolute path.

---

## Phase 1 — Understand the Codebase

Read the codebase and build a holistic understanding. This is one coherent thought — as you discover patterns, you're already forming opinions about components; as you trace dependencies, you're already seeing failure modes. The checklist below ensures completeness, not a sequential mental pass.

### Step 1 — Locate and gather

Resolve the project directory (`$ROOT`). Check: `~/<project>/`, `~/repos/<project>/`, `~/test-repos/<project>/`, or absolute path. If not found, report and exit. If empty, produce minimal atlas.json.

**Clean previous output.** Delete `$ROOT/.kord/agents/augur/memory/` if it exists — start fresh. Do NOT read old atlas.json or stories from a previous run. Analyze the code, not previous analysis.

Detect the stack (languages, frameworks via [frameworks.md](frameworks.md), runtime). Glob source files per [source-gathering.md](source-gathering.md). Load concept catalogs (abstractions, concepts, anti-patterns indexes).

### Step 2 — Read and analyze

Read the source code. As you build your understanding, cover all concerns below. They inform each other — don't treat them as separate passes. Read each reference doc **when you reach that concern**, not upfront.

**Completeness checklist:**

- **Patterns and concepts** — 4-pass catalog scan: batch grep → AST/semgrep → signatures → diagnostic questions. Assess confidence. Identify gaps. When starting this: read [detection.md](detection.md).
- **Dependencies** — Internal modules, imports, external services, infra manifests, inter-service config. Flag circular deps and hub modules. If `--reverse`, scan siblings. When starting this: read [dep-analysis.md](dep-analysis.md).
- **API surface** — Framework detection, route discovery, 7 REST hygiene concerns, gateway/hexagonal compliance. Non-REST styles. When starting this: read [api-review.md](api-review.md) and [frameworks.md](frameworks.md).
- **Components** — 5-10 top-level, nested via children. Annotate with patterns, deps, endpoints. Assign to 3-5 groups. When starting this: read [source-gathering.md](source-gathering.md).
- **Actors and flows** — External actors. Trace 2-6 critical flows across all five types (data, control, event, state, resource). Not every project will have all five — trace what exists. Events (omit if none). When writing atlas: read [atlas-atlas-schema.md](atlas-atlas-schema.md).
- **Domain model and bounded contexts** — Identify the project's core data shape by examining schemas, models, and data stores. Use `category: domain-model` concepts from the catalog for detection signals. Most projects have one primary model (e.g., property-graph, ledger, catalog). Map bounded contexts: where does the same entity name mean different things across modules? Extract ubiquitous language for ambiguous or domain-specific terms.
- **State** — Stores with concept vocabulary, readers/writers, persistence model. Assess schema evolution strategy (migrations directory, versioning tool). Identify concurrency handling (locking strategy, conflict resolution). Record `schema_evolution` and `concurrency` on each state entry.
- **Observability** — Logging structure (JSON vs plain, correlation IDs, library). Metrics exposure (endpoint, format, key metrics). Tracing (provider, propagation). Flag gaps — missing correlation IDs, no metrics endpoint, no error tracking. Record in `observability` section.
- **Security** — Authentication methods and default-deny posture. Authorization model (RBAC, ABAC, ACL). Secrets management strategy — scan for hardcoded credentials, `.env` files committed, environment variable injection. Map threat surface: every external entry point with its auth and validation status. Record in `security` section.
- **Developer experience** — Testing strategy: locate test directories, identify frameworks, assess unit/integration/e2e coverage. Linting and formatting: find config files (`.eslintrc`, `pyproject.toml`, `.prettierrc`), check for pre-commit hooks. Documentation: README quality, ADRs, API docs (OpenAPI/proto), inline comment density. Record in `developer_experience` section.
- **Infrastructure** — CI/CD pipelines: find workflow files (`.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`), map triggers and stages. IaC: find Terraform, CloudFormation, Helm, Kustomize files, inventory managed resources. Record in `module_graph.ci_cd` and `module_graph.iac`.
- **Failure modes** — Cascading failures for every external dep and stateful component. Detection signals, recovery steps. `"none"` if absent.
- **Debt** — Anti-patterns from detected concepts, violations, score/grade (A-F, hard floor rule), 3-7 prioritized recommendations. When scoring: read [debt.md](debt.md).
- **Stories** — When composing stories: read [story-atlas-schema.md](story-atlas-schema.md) and [writing-guide.md](writing-guide.md).

### Step 3 — Gemini atlas review

Write the draft atlas to `/tmp/atlas-draft.json`, then launch Gemini to audit it while you continue composing. Use `run_in_background`:
```bash
gemini -m gemini-2.5-pro -o json -p "You are AUDITING this atlas for ERRORS. Your job is to find mistakes, not confirm quality. For each component: verify the listed files exist, check the description matches actual code, verify depends_on edges by checking imports. For each detected pattern: find evidence that CONTRADICTS the detection — false positives are your target. For each grounded_in reference: does the cited file:line actually support the claim? For each failure mode: is the severity correct or exaggerated? For each flow: verify the type matches the step fields used (data flows use data/transform, control flows use condition/gate, etc.). For observability/security/developer_experience: verify grounded_in files actually contain the claimed tooling. For bounded contexts: verify entity definitions actually differ across the listed modules. Constraints: 3-5 groups (hard), 5-10 components (4-12 acceptable), 2-6 flows. Report EVERY error with specific file paths." @$ROOT/ < /tmp/atlas-draft.json > /tmp/gemini-review-atlas.json
```
Continue to Step 4 while Gemini runs — you will be notified when it completes.

### Step 4 — Write atlas.json

Assemble into [atlas-atlas-schema.md](atlas-atlas-schema.md) v4 format. Set `version: "4"` and `generated` to today.

**Before writing the final atlas.json**, check if the Gemini atlas review (Step 3) has completed. If it has, read `/tmp/gemini-review-atlas.json` and incorporate valid critiques — fix any confirmed errors (wrong file paths, false pattern detections, incorrect severity). Discard critiques that are wrong or subjective. If Gemini hasn't finished yet, wait for the notification before writing.

Write to `$ROOT/.kord/agents/augur/memory/atlas.json`.

If `--detect-only`: skip Phase 2, go to Report.

---

## Phase 2 — Compose

With all Phase 1 findings in context, compose stories and journeys together as one coherent thought per [story-atlas-schema.md](story-atlas-schema.md).

### Step 5 — Compose the story tree

Build a tree of stories that mirrors the atlas structure. Top-down per [story-atlas-schema.md](story-atlas-schema.md):

**1. Root stories (3-5, one per atlas group).** For each group, write a root story that orients the reader: what components this group contains, how they relate, why this grouping exists. Root summaries are 2 paragraphs max, ~50-80 words. Set `parent: null`, list `children`.

**2. Child stories (2-5 per root).** For each root, identify the concerns worth zooming into — a key flow, a data store, a failure mode, a design decision. Write a child story for each. Child summaries are 3 paragraphs max, ~80-120 words. Set `parent: "<root-id>"`. Children can reference atlas nodes from outside the parent's group when the concern crosses boundaries.

**3. Journeys (3-5 total).** Always create `getting-started.yaml` (number: 1) — a teaching-order journey for someone new to the codebase, pulling stories from all groups. Then create 2-4 additional journeys (numbered 2+) for different audiences or cross-cutting concerns. Minimum 3 journeys — every project has at least 3 distinct perspectives worth walking through. 3-8 stories per journey.

**Every journey must have:**
- `number` — getting-started is 1, others are 2, 3, etc.
- `overview` — 2-3 sentences framing the journey for its audience. This is the chapter 0 that appears before the first story. Getting-started's overview is the project overview. Other journeys frame their specific concern (e.g., "The system has 6 external dependencies. Here's what happens when each one fails.")
- Each story must identify its `anchor` — the one file:line a new developer should open first.
- `bridges` connecting each adjacent pair of stories — `from`/`to` with a one sentence question. Required for getting-started, recommended for others.

Each story is assembled from building blocks:
- **summary** (required) — short paragraphs, depth-dependent length
- **structures** — nested components + typed edges
- **flows** — ordered steps, typed
- **observations** — evidence-backed findings
- **rationale** — design decisions, trade-offs, alternatives

All prose follows [writing-guide.md](writing-guide.md). For failure flows: include trigger, severity, detection, recovery. For data structures: use `reads`/`writes` edge types.

**Typical output:** 3-5 root stories, 8-20 child stories, 0-3 journeys.

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

3. **Gemini story review** — review against the **codebase**. Run with `run_in_background`:
   ```bash
   gemini -m gemini-2.5-pro -o json -p "You are AUDITING these stories for ERRORS against the source code. The code is ground truth, not the atlas. For each bold-ref component name: verify it matches an actual module. For each claim about behavior: find the code that proves or disproves it. For each observation: read the grounded_in file and check the claim holds. Find: fabricated claims not in the code, missing critical concerns, wrong causality, exaggerated severity. Root summaries must be 50-80 words, child 80-120. Report EVERY error." @$ROOT/ @$ROOT/.kord/agents/augur/memory/stories/ @$ROOT/.kord/agents/augur/memory/atlas.json > /tmp/gemini-review-stories.json
   ```

**Wait for the Gemini story review to complete** before proceeding to the report. Read `/tmp/gemini-review-stories.json` and fix any confirmed errors in stories (fabricated claims, wrong file references, incorrect causality). If changes are made, **call warden again** for a fresh token.

If groundedness is low, fix claims. If coverage is low, add stories. Always revalidate after changes.

---

## Step 9 — Report

```
## Analysis: <project>

**Purpose**: <one sentence>
**Components** (N): <names>
**Groups** (N): <names>
**Flows** (N): N data, N control, N event, N state, N resource
**Bounded Contexts** (N): <names>
**Concepts**: N patterns, N anti-patterns, N gaps
**API**: N endpoints, N critical / N recommended / N minor findings
**Observability**: logging (<format>), metrics (<format>), tracing (<provider>). Gaps: <list or none>
**Security**: auth (<methods>), secrets (<strategy>), threat surface (<N entry points>)
**DevEx**: testing (<frameworks>), linting (<tools>), docs (<coverage>)
**Debt**: Score N — Grade X. <interpretation>
**External** (N): <names with criticality>
**Failures** (N): <names with severity>
**Stories**: N root, N child
**Journeys** (N): <titles> (if any)
**Groundedness**: <min>-<max> across stories
**Coverage**: <percentage> of critical components
**Validation token**: <token from warden>
**Top recommendations**: 1. ... 2. ... 3. ...

Written to:
  atlas: <path>
  stories: <path> (N files)
  journeys: <path> (N files, if any)
```

If `--detect-only`, omit Stories/Journeys/Groundedness/Coverage/Validation lines.

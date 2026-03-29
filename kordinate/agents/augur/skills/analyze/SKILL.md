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

## Phase 1 — Understand the Codebase

Read the codebase and build a holistic understanding. This is one coherent thought — as you discover patterns, you're already forming opinions about components; as you trace dependencies, you're already seeing failure modes. The checklist below ensures completeness, not a sequential mental pass.

### Step 1 — Locate and gather

Resolve the project directory (`$ROOT`). Check: `~/<project>/`, `~/repos/<project>/`, `~/test-repos/<project>/`, or absolute path. If not found, report and exit. If empty, produce minimal atlas.json.

Detect the stack (languages, frameworks via [frameworks.md](frameworks.md), runtime). Glob source files per [source-gathering.md](source-gathering.md). Load concept catalogs (abstractions, concepts, anti-patterns indexes).

### Step 2 — Read and analyze

Read the source code. As you build your understanding, make sure you cover all of these concerns. They inform each other — don't treat them as separate passes.

**Completeness checklist:**

| Concern | Methodology | Reference |
|---------|-------------|-----------|
| **Patterns and concepts** | 4-pass catalog scan: batch grep → AST/semgrep → signatures → diagnostic questions. Assess confidence. Identify gaps. | [detection.md](detection.md) |
| **Dependencies** | Internal modules, imports, external services, infra manifests, inter-service config. Flag circular deps and hub modules. If `--reverse`, scan siblings. | [dep-analysis.md](dep-analysis.md) |
| **API surface** | Framework detection, route discovery, 7 REST hygiene concerns, gateway/hexagonal compliance. Non-REST styles. | [api-review.md](api-review.md), [frameworks.md](frameworks.md) |
| **Components** | 5-10 top-level, nested via children. Annotate with patterns, deps, endpoints. Assign to 3-5 groups. | [source-gathering.md](source-gathering.md) |
| **Actors and flows** | External actors. 2-4 critical data flows. Events (omit if none). | [schema.md](schema.md) |
| **State** | Stores with concept vocabulary, readers/writers, persistence model. | [dep-analysis.md](dep-analysis.md) |
| **Failure modes** | Cascading failures for every external dep and stateful component. Detection signals, recovery steps. `"none"` if absent. | [schema.md](schema.md) |
| **Debt** | Anti-patterns from detected concepts, violations, score/grade (A-F, hard floor rule), 3-7 prioritized recommendations. | [debt.md](debt.md) |

### Step 3 — Gemini review (background)

Feed the draft atlas, source code, and our constraints to Gemini:
```bash
gemini -m gemini-2.5-pro -o json -p "Review this atlas.json against the source code. Our constraints: MUST have 3-5 groups (hard limit), 5-10 components (4-12 acceptable), 2-4 critical flows. Every entry needs grounded_in file references. Flag: missing components, incorrect edges, missed failure modes, false positives, severity misclassifications, API findings missed, groups that should merge or split to hit 3-5. Be specific — cite file paths." @$ROOT/ < /tmp/atlas-draft.json > /tmp/gemini-review-atlas.json &
```
Continue immediately.

### Step 4 — Write atlas.json

Assemble into [schema.md](schema.md) v3 format. Set `version: "3"` and `generated` to today. Incorporate valid Gemini critiques if available. Write to `$ROOT/.kord/agents/augur/memory/atlas.json`.

If `--detect-only`: skip Phase 2, go to Report.

---

## Phase 2 — Compose

With all Phase 1 findings in context, compose stories and journeys together as one coherent thought per [story-schema.md](story-schema.md).

### Step 5 — Compose stories and journeys

Think about the codebase as a whole. What are the important things to understand? Who needs to understand them? Let the journeys guide which stories to tell.

Start with the **overview journey** (always required). As you identify each architectural concern worth explaining, write the story AND place it in the appropriate journey(s) simultaneously. If composing a journey reveals a gap between two stories, write a bridging story right there.

**Teaching order**: within each journey, sequence stories from most foundational to most dependent. Each story should build on what the previous established. Ask "what does the reader need to understand before this story makes sense?" and order accordingly.

Each story is assembled from building blocks per [story-schema.md](story-schema.md):
- **summary** (required) — 1-2 short paragraphs, ~50-80 words
- **structures** — nested components + typed edges (component topology, data lineage, infrastructure, or any type augur sees fit)
- **flows** — ordered steps, typed (request paths, failure cascades, data pipelines, or any type augur sees fit)
- **observations** — evidence-backed findings, attachable to specific structure nodes or flow steps
- **rationale** — design decisions, trade-offs, alternatives considered

Stories are **short orienting sections**. The summary orients the reader; the structures and flows carry the detail; observations point to evidence. All prose follows [writing-guide.md](writing-guide.md): state facts about code, not facts about the document.

For failure flows: include trigger, severity, detection, recovery. `detection: ["none"]` or `recovery: ["none"]` should generate a gap observation automatically.

For data structures: use `reads`/`writes` edge types and inherit `purpose`/`persistence` from atlas nodes.

**Typical output:** 8-15 stories across 2-4 journeys. Each story has a summary and 1-3 building blocks.

### Step 6 — Refine (Detect-Compose-Refine)

Review each story. If a summary makes a claim not directly observed in Phase 1, re-read the specific source file(s) to verify or correct it. Only re-read files that an ungrounded claim references.

### Step 7 — Evaluate

Three mechanical checks, then a Gemini review:

1. **Schema validation** (run the script):
   ```bash
   python $SKILL_DIR/scripts/validate_atlas.py $ROOT/.kord/agents/augur/memory/atlas.json
   ```
   The script checks: required fields, kebab-case IDs, unique IDs, all cross-references resolve, 3-5 groups, 5-10 components, `grounded_in` non-empty. Fix any errors before proceeding.

2. **Groundedness verification**: for each observation and story claim with `grounded_in` references, re-read the cited source files and verify the claim holds at those locations. This catches hallucinations at the source — not "does the atlas agree?" (circular) but "does the code agree?" (ground truth). Target: >= 0.85.

3. **Coverage**: critical atlas nodes in at least one story / total critical nodes. Target: >= 0.80.

4. **Gemini story review** (background):
   ```bash
   gemini -m gemini-2.5-pro -o json -p "Review these architectural stories against the atlas and our writing rules. Rules: summaries must be 50-80 words max, state facts about code not facts about the document, every **bold ref** must match an atlas node ID, no meta-text like 'this story covers...' Story building blocks: summary (required), structures, flows, observations, rationale. Journeys: 3-8 stories each, ordered from foundational to dependent. Check: do stories cover important concerns? Teaching order sensible? Summaries factual and specific? Any critical components missing from all stories?" @$ROOT/.kord/agents/augur/memory/stories/ < $ROOT/.kord/agents/augur/memory/atlas.json > /tmp/gemini-review-stories.json &
   ```
   Incorporate valid critiques before writing final output. Ignore opinions that contradict our constraints.

If groundedness is low, fix the claims at the source. If schema is invalid, fix the structure. If coverage is low, add stories for uncovered components.

### Step 8 — Write

Write stories to `$ROOT/.kord/agents/augur/memory/stories/<id>.yaml`. Write journeys to `$ROOT/.kord/agents/augur/memory/journeys/<id>.yaml`. Create directories if needed. Update `metadata.story_ids` in atlas.json.

---

## Step 9 — Report

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
**Stories** (N): <titles>
**Journeys** (N): <titles>
**Groundedness**: <min>-<max> across stories
**Coverage**: <percentage> of critical components
**Top recommendations**: 1. ... 2. ... 3. ...

Written to:
  atlas: <path>
  stories: <path> (N files)
  journeys: <path> (N files)
```

If `--detect-only`, omit the Stories/Journeys/Groundedness/Coverage lines.

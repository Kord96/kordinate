# Story Schema

Level 3 resource for the analyze skill. Referenced from Phase 2 (compose). Defines story tree, building block, and journey formats.

## Design Principle

Stories nest like components. A **root story** gives the high-level view of a group (3-5 roots, mirroring atlas groups). **Child stories** zoom into specific concerns within that group. The story tree IS the primary navigation — drill down from root to children.

**Journeys** are secondary — thin cross-cutting paths through the tree for specific audiences (resilience review, onboarding). They're just ordered lists of story IDs pulled from anywhere in the tree.

## Building Blocks

Every story is assembled from these blocks. Only `summary` is required.

| Block | Purpose | Multiple per story? |
|-------|---------|-------------------|
| **summary** | Short paragraphs orienting the reader | No |
| **structure** | Nested components + typed edges | Yes |
| **flow** | Ordered steps through components, typed | Yes |
| **observations** | Evidence-backed findings, attachable to nodes and steps | One list |
| **rationale** | Design decisions, trade-offs, alternatives | Yes |

### Why these blocks

- **Structure** covers component topology, data store lineage, infrastructure layout, security boundaries — anything that's "things and their relationships."
- **Flow** covers request paths, data pipelines, failure cascades, deployment sequences, event chains — anything that's "things happening in order."
- **Rationale** captures the "why" — decisions, trade-offs, alternatives considered.
- **Observations** are findings that attach to the story, to specific structure nodes, or to specific flow steps.

## Story Schema

```yaml
# ── Identity ──────────────────────────────────────────────────────

id: "<kebab-case>"                        # unique across all stories
title: "<Human Readable Title>"
teaches: "<one sentence — what the reader learns>"
tags: ["<freeform>"]                     # for filtering and indexing

# ── Anchor ───────────────────────────────────────────────────────

anchor:                                  # optional — the single most important code location
  file: "<relative path>"               # relative to project root
  line: <number>                         # starting line
  description: "<one sentence — what the reader sees here>"

# ── Tree ──────────────────────────────────────────────────────────

parent: "<story-id>"                     # null for root stories
children: ["<story-id>"]                 # ordered — this is the drill-down sequence

# ── Summary (required) ────────────────────────────────────────────

summary: |
  <paragraphs — length varies by depth, see Verbosity Rules>
  <**bold refs** resolve to atlas node IDs>

# ── Structures (0+) ──────────────────────────────────────────────

structures:
  - id: "<kebab-case>"
    title: "<Human Readable>"
    type: "<freeform — see suggested types below>"
    nodes:
      - id: "<atlas-node-id>"
        children: ["<atlas-node-id>"]
        observation_ids: ["<obs-id>"]
    edges:
      - from: "<node-id>"
        to: "<node-id>"
        label: "<short>"
        type: "<freeform: depends_on, reads, writes, contains, calls, publishes, subscribes, ...>"

# ── Flows (0+) ────────────────────────────────────────────────────

flows:
  - id: "<kebab-case>"
    title: "<Human Readable>"
    type: "<freeform — see suggested types below>"
    trigger: "<what starts this flow>"
    severity: "<critical|high|medium|low>"
    detection: ["<signal or 'none'>"]
    recovery: ["<step or 'none'>"]
    steps:
      - node: "<atlas-node-id>"
        action: "<what it does>"
        effect: "<what happens to it>"
        to: "<atlas-node-id>"
        technology: "<protocol>"
        observation_ids: ["<obs-id>"]

# ── Observations (0+) ─────────────────────────────────────────────

observations:
  - id: "<obs-id>"
    finding: "<one sentence>"
    confidence: "<high|medium|low>"
    component: "<atlas-node-id>"
    evidence:
      file: "<path relative to project root>"
      lines: [14, 28]
      snippet: "<code>"
    tags: ["<freeform>"]
    detection_method: "<grep|ast-grep|semgrep|questions|manual>"
    recommendation: "<what to do>"
    related: ["<obs-id>"]
    grounded_in: ["<file:line>"]

# ── Rationale (0+) ────────────────────────────────────────────────

rationale:
  - id: "<kebab-case>"
    decision: "<what was decided>"
    context: "<why this decision was needed>"
    trade_offs: "<gained vs given up>"
    alternatives: ["<rejected alternative and why>"]

# ── Evaluation ────────────────────────────────────────────────────

evaluation:
  groundedness: 0.92
  coverage: 0.85
  claim_count: 15
  ungrounded_claims: []
```

## Story Tree

Stories form a tree mirroring the atlas group/component hierarchy.

### Constraints

| Rule | Value |
|------|-------|
| Root stories | 3-5 (one per atlas group) |
| Max depth | 2 (root → child, no deeper) |
| Children per root | 2-5 |
| Cross-group references | Allowed — a child can reference atlas nodes outside its parent's group |

### Root stories (depth 0)

One per atlas group. The root story gives the high-level view of the group: what components it contains, how they relate, why this grouping exists. Its `structures` block shows the group's components. Its `children` list the drill-down stories.

Root stories have `parent: null`.

### Child stories (depth 1)

Zoom into one concern within the parent's group. A child story focuses on a subset of the parent's nodes — a specific flow, a data store, a failure mode, a design decision. It can reference nodes from outside the parent's group when the concern crosses boundaries (e.g., a failure cascade that propagates from the API group to the data group).

Child stories have `parent: "<root-story-id>"`.

### Scoping rules

- A child story should reference **fewer nodes** than its parent — it's zooming in, not expanding
- A child's structures/flows don't need to be a strict subset of the parent's — they can pull in nodes from other groups when the concern requires it
- If a concern spans multiple groups equally (no primary group), attach it to the most relevant root and use `tags` to help journeys find it

## Verbosity Rules

Summary length scales with depth and grounding scope. The deeper and more focused, the more room to explain. But always cap at 3 paragraphs.

| Depth | Max paragraphs | Word target | Role |
|-------|---------------|-------------|------|
| 0 (root) | 2 | 50-80 words | Orient: what is this group, what's in it, why it exists |
| 1 (child) | 3 | 80-120 words | Explain: one specific concern, with evidence |

**Grounding influence**: a story grounded in 1-2 files can say what it needs in 1 paragraph. A story grounded in 10+ files may need all 3. But never exceed the max — the structures, flows, and observations carry the detail.

All prose follows [writing-guide.md](writing-guide.md).

## Suggested Types

Types are freeform strings. Augur invents new ones as needed.

**Structure types:**
- `component topology` — how components are organized and depend on each other
- `data lineage` — stores, readers, writers, persistence model
- `infrastructure` — deployment, k8s resources, cloud services
- `security boundary` — auth zones, trust boundaries, permission model
- `module graph` — internal code organization, import relationships

**Flow types:**
- `request path` — user/API request through the system
- `data pipeline` — data transformation or ETL sequence
- `failure cascade` — what breaks when a component fails
- `event chain` — async event propagation
- `deployment sequence` — how code gets to production
- `config resolution` — how configuration is loaded and resolved

Scribe uses the type to choose rendering strategy. Unknown types fall back to generic rendering.

## Failure Flow Conventions

When a flow has cascade semantics, include `trigger`, `severity`, `detection`, `recovery`. Use `effect` on steps instead of `action`. `detection: ["none"]` or `recovery: ["none"]` should auto-generate a gap observation.

## Data Structure Conventions

When a structure has data lineage semantics, use `reads`/`writes` edge types. Inherit `purpose`/`persistence` from atlas nodes.

## Observation Attachment

Observations defined once in the story's `observations` list. Attach at three levels:
1. **Story-wide** — exists in the list (default)
2. **Structure node** — via `observation_ids` on a node
3. **Flow step** — via `observation_ids` on a step

---

## Journey Schema

A journey is a **thin cross-cutting path** through the story tree. It pulls stories from anywhere in the tree into a specific reading order for a specific audience.

Journeys are secondary navigation. The story tree is primary.

```yaml
id: "<kebab-case>"
title: "<Human Readable Title>"
description: "<one sentence — what the reader achieves>"
audience: ["<role>"]
stories:
  - "<story-id>"                          # can be root or child, from any group
  - "<story-id>"
bridges:                                   # edges connecting adjacent stories
  - from: "<story-id>"
    to: "<story-id>"
    text: "<one sentence — question pulling the reader forward>"
```

### Bridges

Bridges are edges between adjacent stories in the journey. They create curiosity for what comes next.

- `from` and `to` must both exist in the `stories` list
- `from` and `to` must be adjacent in the stories order
- `text` is one sentence — typically a question the next story answers
- N stories → N-1 bridges (every adjacent pair connected)
- Bridges are **required** for `getting-started` journeys, optional for others

### Journey design rules

- **3-8 stories** per journey
- Stories can come from **any level** of the tree (root or child)
- **Teaching order**: foundational to dependent
- Journeys exist for **cross-cutting concerns** that don't fit one branch of the tree (resilience review, onboarding path)
- For concerns that DO fit one branch, just navigate the tree — no journey needed

### When to create a journey

- **Do create**: when a concern spans multiple root groups (resilience across API + data + external)
- **Do create**: when a specific audience needs a curated path (frontend onboarding)
- **Don't create**: for navigating within one group (that's what the tree is for)
- **Don't create**: for an "overview" (the root stories ARE the overview)

## File Layout

```
<project>/.kord/agents/augur/memory/
  atlas.json
  stories/
    <id>.yaml              # both roots and children in the same directory
  journeys/
    <id>.yaml              # only created when cross-cutting paths are needed
```

Story filenames use the story `id`. Parent/child relationships are inside the files, not in the directory structure.

# Story Schema

Level 3 resource for the analyze skill. Referenced from Phase 2 (compose). Defines story, journey, and building block formats.

## Design Principle

A story is a **short scoped section** about one architectural concern. Its value is in scoping (which components, which path, which decision) and referencing (atlas nodes, observations, other stories). Think README section, not essay.

Stories and journeys are composed together — the journey structure informs which stories to tell.

## Building Blocks

Every story is assembled from these blocks. Only `summary` is required.

| Block | Purpose | Multiple per story? |
|-------|---------|-------------------|
| **summary** | 1-2 short paragraphs orienting the reader | No |
| **structure** | Nested components + typed edges | Yes |
| **flow** | Ordered steps through components, typed | Yes |
| **observations** | Evidence-backed findings, attachable to nodes and steps | One list |
| **rationale** | Design decisions, trade-offs, alternatives | Yes |

### Why these blocks

- **Structure** covers component topology, data store lineage, infrastructure layout, security boundaries — anything that's "things and their relationships." What was previously `data` is a structure with `type: "data lineage"` and edges typed `reads`/`writes`.
- **Flow** covers request paths, data pipelines, failure cascades, deployment sequences, event chains — anything that's "things happening in order." What was previously `resilience` is a flow with `type: "failure cascade"` and extra metadata (trigger, severity, detection, recovery).
- **Rationale** captures the "why" — decisions, trade-offs, alternatives considered. This was previously missing entirely.
- **Observations** are findings that attach to the story, to specific structure nodes, or to specific flow steps.

## Story Schema

```yaml
# ── Identity ──────────────────────────────────────────────────────

id: "<kebab-case>"                        # unique across all stories
title: "<Human Readable Title>"
teaches: "<one sentence — what the reader learns>"
tags: ["<freeform>"]                     # for filtering and indexing

# ── Summary (required) ────────────────────────────────────────────

summary: |
  <1-2 short paragraphs, ~50-80 words total>
  <orient the reader: what is this about, why does it matter>
  <**bold refs** resolve to atlas node IDs>

# ── Structures (0+) ──────────────────────────────────────────────

structures:
  - id: "<kebab-case>"
    title: "<Human Readable>"
    type: "<freeform — see suggested types below>"
    nodes:
      - id: "<atlas-node-id>"            # reference, not definition
        children: ["<atlas-node-id>"]    # subset of atlas children relevant to this story
        observation_ids: ["<obs-id>"]    # findings on this node
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
    # Extra metadata — include what's relevant to the flow type:
    trigger: "<what starts this flow>"              # optional
    severity: "<critical|high|medium|low>"          # optional, for failure flows
    detection: ["<signal or 'none'>"]               # optional, for failure flows
    recovery: ["<step or 'none'>"]                  # optional, for failure flows
    steps:
      - node: "<atlas-node-id>"
        action: "<what it does>"                    # for request/data flows
        effect: "<what happens to it>"              # for failure cascades
        to: "<atlas-node-id>"                       # optional, next node
        technology: "<protocol>"                    # optional
        observation_ids: ["<obs-id>"]               # findings on this step

# ── Observations (0+) ─────────────────────────────────────────────

observations:
  - id: "<obs-id>"
    finding: "<one sentence>"
    confidence: "<high|medium|low>"
    component: "<atlas-node-id>"
    evidence:
      file: "<path relative to project root>"
      lines: [14, 28]                   # optional
      snippet: "<code>"                  # optional
    tags: ["<freeform>"]
    detection_method: "<grep|ast-grep|semgrep|questions|manual>"
    recommendation: "<what to do>"       # optional
    related: ["<obs-id>"]               # links to related observations

# ── Rationale (0+) ────────────────────────────────────────────────

rationale:
  - id: "<kebab-case>"
    decision: "<what was decided>"
    context: "<why this decision was needed>"
    trade_offs: "<what was gained and what was given up>"
    alternatives: ["<rejected alternative and why>"]

# ── Evaluation ────────────────────────────────────────────────────

evaluation:
  groundedness: 0.92
  coverage: 0.85
  claim_count: 15
  ungrounded_claims: []
```

## Suggested Types

Types are freeform strings. Augur can invent new ones. These are common starting points:

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

Scribe uses the type to choose rendering strategy (sequence diagram vs cascade timeline vs topology graph). Unknown types fall back to generic rendering.

## Failure Flow Conventions

When a flow has cascade semantics (failure propagation), include:
- `trigger` — what starts the failure
- `severity` — how bad it is
- `detection` — what signals exist. `["none"]` means no detection — this itself becomes an observation
- `recovery` — what to do. `["none"]` means no recovery — also becomes an observation
- Use `effect` on steps instead of `action` (what happens to the component, not what it does)

Absence of detection/recovery is a finding. If `detection: ["none"]`, augur should auto-generate a gap observation.

## Data Structure Conventions

When a structure has data lineage semantics, use:
- `reads` and `writes` edge types instead of generic `depends_on`
- Node annotations from atlas: `purpose` (source-of-truth, cache, derived, staging), `persistence` (persistent, ephemeral)
- These are inherited from the atlas node, not redefined in the story

## Narrative Constraints

Summaries are the only prose. Keep them short.

- **~50-80 words** total per summary
- **Scenario-driven** — trace real journeys, name concrete actors
- **Lead with action** — start with what happens, not setup
- **Decision anchors** — explain WHY when mentioning patterns
- Every `**bold ref**` must resolve to an atlas node ID
- Em dashes (—) not hyphens

## Observation Attachment

Observations are defined once in the story's `observations` list. They attach at three levels:
1. **Story-wide** — the observation exists in the list (default)
2. **Structure node** — referenced via `observation_ids` on a node
3. **Flow step** — referenced via `observation_ids` on a step

This avoids duplication while preserving context (which node or step this finding applies to).

---

## Journey Schema

A journey is an ordered reading path through stories. Stories and journeys are composed together — the journey informs which stories to tell.

```yaml
id: "<kebab-case>"
title: "<Human Readable Title>"
description: "<one sentence — what the reader achieves>"
audience: ["<role>"]
stories:
  - "<story-id>"                         # ordered sequence
  - "<story-id>"
```

### Journey design rules

- **3-8 stories** per journey. Shorter is better.
- Stories can belong to **multiple journeys**.
- The first story should orient the reader (typically shows the high-level structure).
- Journeys for different audiences can share stories but sequence them differently.

### Suggested journeys

| Journey | Audience | Typical content |
|---------|----------|----------------|
| **overview** | New team member | High-level structure → key flows → notable decisions |
| **backend onboarding** | Backend developer | Server structure → request path → persistence → failure modes |
| **frontend onboarding** | Frontend developer | Client structure → rendering flow → state management |
| **resilience review** | SRE, on-call | Failure cascades → gap observations → recovery procedures |
| **API consumer** | External integrator | API structure → key request paths → auth/rate-limit observations |

Augur can create journeys beyond this list based on what the codebase warrants.

## File Layout

```
<project>/.kord/agents/augur/memory/
  atlas.json
  stories/
    <id>.yaml
  journeys/
    <id>.yaml
```

Story filenames use the story `id`, not `type-id`. The type is inside the file.

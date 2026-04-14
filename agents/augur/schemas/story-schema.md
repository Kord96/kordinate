# Story Schema

Canonical contract for `stories/*.yaml`.

Stories are the primary navigation layer over the atlas. Root stories mirror top-level components. Child stories zoom into a specific concern within that component subtree or a cross-cutting concern anchored there.

## Prose Rules

Apply these rules to story summaries, findings, and rationale:

- state facts about the system, not facts about the document
- name concrete components, dependencies, and flows
- keep summaries concise and grounded
- use `**bold**` component references only when they resolve to real atlas ids
- prefer active phrasing and direct relationships
- avoid filler such as "this story covers" or "the following section"

## Story Schema

```yaml
id: "<kebab-case>"
title: "<Human Readable Title>"
teaches: "<one sentence — what the reader learns>"
tags: ["<freeform>"]

anchor:
  file: "<relative path>"
  line: <number>
  description: "<one sentence — where to start reading>"

parent: "<story-id or null>"
children: ["<story-id>"]

summary: |
  <paragraphs — concise and grounded>
  <**bold refs** resolve to atlas node IDs>

structures:
  - id: "<kebab-case>"
    title: "<Human Readable>"
    type: "<freeform>"
    nodes:
      - id: "<atlas-node-id>"
        children: ["<atlas-node-id>"]
        observation_ids: ["<obs-id>"]
    edges:
      - from: "<node-id>"
        to: "<node-id>"
        label: "<short>"
        type: "<depends_on | reads | writes | contains | calls | publishes | subscribes | ...>"

flows:
  - id: "<kebab-case>"
    title: "<Human Readable>"
    type: "<freeform>"
    trigger: "<what starts this flow>"
    severity: "<critical|high|medium|low>"
    detection: ["<signal or 'none'>"]
    recovery: ["<step or 'none'>"]
    steps:
      - node: "<atlas-node-id>"
        action: "<what it does>"
        effect: "<what happens>"
        to: "<atlas-node-id>"
        technology: "<protocol>"
        observation_ids: ["<obs-id>"]

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

rationale:
  - id: "<kebab-case>"
    decision: "<what was decided>"
    context: "<why this decision was needed>"
    trade_offs: "<gained vs given up>"
    alternatives: ["<rejected alternative and why>"]

evaluation:
  groundedness: 0.92
  coverage: 0.85
  claim_count: 15
  ungrounded_claims: []
```

## Story Tree

Stories form a tree that mirrors the component hierarchy.

### Constraints

| Rule | Value |
|------|-------|
| Root stories | 3-5 (one per top-level component) |
| Max depth | 2 |
| Children per root | 2-5 |
| Cross-boundary references | Allowed when the concern crosses component boundaries |

### Root stories

One per top-level component. A root story gives the high-level view of that component subtree: what it owns, how it relates to adjacent top-level components, and which major flows or state it anchors.

Root stories have `parent: null`.

### Child stories

Zoom into one concern within the parent component subtree: a critical flow, state boundary, failure mode, or design decision. A child story may reference nodes outside the parent subtree when the concern genuinely crosses boundaries.

Child stories have `parent: "<root-story-id>"`.

### Scoping rules

- a child story should focus on fewer nodes than its parent
- a child story may include nodes outside the parent subtree when needed to explain a real interaction
- if a concern spans multiple top-level components equally, attach it to the most relevant root and use `tags` to aid narrative assembly

## Verbosity Rules

Summary length scales with depth and grounding scope. Cap at 3 paragraphs.

| Depth | Max paragraphs | Word target | Role |
|-------|---------------|-------------|------|
| 0 (root) | 2 | 50-80 words | Orient: what this top-level component owns and why it matters |
| 1 (child) | 3 | 80-120 words | Explain: one specific concern with evidence |

## Suggested Types

Types are freeform strings.

**Structure types:**
- `component topology`
- `data lineage`
- `infrastructure`
- `security boundary`
- `module graph`

**Flow types:**
- `request path`
- `data pipeline`
- `failure cascade`
- `event chain`
- `deployment sequence`
- `config resolution`

## Attachment Rules

Observations are defined once in the story `observations` list and may attach at three levels:
1. story-wide
2. structure node via `observation_ids`
3. flow step via `observation_ids`

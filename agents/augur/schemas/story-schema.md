# Story Schema

Canonical contract for `stories/*.yaml`.

Stories are the primary navigation layer over the atlas. Root stories mirror top-level components. Child stories zoom into a specific concern within that component subtree or a cross-cutting concern anchored there.

## Prose Rules

Apply these rules to story summaries, findings, and rationale:

- state facts about the system, not facts about the document
- name concrete components, dependencies, and flows
- keep summaries concise and grounded
- prefer exact mechanism names from code when they exist, such as hook names, lifecycle stage names, parser names, registry names, or option names
- prefer one mechanism per sentence unless the code clearly binds multiple mechanisms into one stage
- use `**bold**` atlas references only when they resolve to real atlas ids such as components, state entries, dependencies, flows, events, concepts, or tensions
- prefer active phrasing and direct relationships
- avoid filler such as "this story covers" or "the following section"

## Core Rules

- every structure node id must already exist in `atlas.json`
- every flow step `node` and `to` reference must already exist in `atlas.json`
- do not invent pseudo-nodes such as `detectors`, `scripts`, `http-server`, `kafka-consumer`, `llm-runtime`, or `fact-store` unless they are real atlas ids
- do not turn filenames or helper modules into structure nodes; if `fact_extractor_support.py` or a similar file matters, cite it in `anchor`, `evidence`, or `grounded_in` instead of inventing a node id from the filename
- describe internal subparts through observations, findings, and prose when they are not modeled as atlas nodes
- bold references in `summary` must resolve to real atlas ids; do not bold filenames, fact artifacts, or schema names
- root story ids should normally match the top-level component ids they explain
- child story ids should stay story-specific, but `parent` must always reference a real story id
- before you cite a repo file in `anchor`, `evidence.file`, or `grounded_in`, confirm the path actually exists in the repo or analysis run; do not guess filenames such as `agents/augur/agent.yaml`
- use the canonical path rules from `augur-output-contract.md`
- treat stories as resolved teaching structure, not as arbitrary file-group summaries
- when `facts/component-seeds.json` and `facts/story-seeds.json` are present, use them to challenge root choice and child-story decomposition before writing
- when `facts/narrative-seeds.json` is present, keep story scope and teaching value strong enough that narratives can select stories by explanatory value rather than by root coverage alone

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
  <**bold refs** resolve to atlas IDs>

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
| Root stories | usually 3-5, matching top-level components when that shape is natural |
| Max depth | 2 |
| Children per root | 2-5 |
| Cross-boundary references | Allowed when the concern crosses component boundaries |

### Root stories

One per top-level component. A root story gives the high-level view of that component subtree: what it owns, how it relates to adjacent top-level components, and which major flows or state it anchors.

Root stories have `parent: null`.
Prefer root story ids that exactly match the corresponding top-level component ids.

### Child stories

Zoom into one concern within the parent component subtree: a critical flow, state boundary, failure mode, or design decision. A child story may reference nodes outside the parent subtree when the concern genuinely crosses boundaries.

Child stories have `parent: "<root-story-id>"`.

### Scoping rules

- a child story should focus on fewer nodes than its parent
- a child story may include nodes outside the parent subtree when needed to explain a real interaction
- if a concern spans multiple top-level components equally, attach it to the most relevant root and use `tags` to aid narrative assembly
- avoid roots with exactly one child unless that child clearly adds distinct explanatory value; otherwise merge it back or create another real concern-focused child

## Concern Selection

Prefer child stories that explain one distinct concern class:
- a major request, control, or event flow
- a state or configuration boundary
- an external dependency or integration boundary
- an important failure path or operations surface
- a major design decision or trade-off

Avoid child stories that merely rename a directory, restate the root summary, or split the parent by arbitrary file groups.
Avoid child stories that exist only to satisfy count heuristics. A child should teach one distinct concern the parent cannot explain as clearly on its own.

## Grounding Style

- observations and summaries should sound like the code they cite, not like generic architectural paraphrases
- when grounded code exposes concrete identifiers, prefer those identifiers or their exact stage names over abstract substitutes
- when `facts/symbols-seed.json` is available for the cited file, prefer exact identifiers from that inventory over nearby paraphrases
- if multiple `grounded_in` lines support one observation, keep the finding focused enough that the same mechanism is visible across those lines
- if one claim requires several unrelated mechanisms to explain, split it into multiple observations
- when a story still reads like a local code inventory after grounding, it is usually the wrong story boundary

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

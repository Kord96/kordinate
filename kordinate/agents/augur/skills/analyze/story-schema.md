# Story Schema

Level 3 resource for the analyze skill. Referenced from Phase 2 (story composition). Defines the output format for story YAML files.

## Story Types

| Type | Centers on | Count | Required dimensions |
|------|-----------|-------|-------------------|
| **structure** | Component group and its internal organization | 3-5 (one per group) | structure |
| **flow** | Data/request path through components | 2-4 (one per critical flow) | flows |
| **data** | State store cluster and its readers/writers | 0+ | data |
| **resilience** | Failure mode and its cascade | 0+ | resilience |
| **highlight** | Notable pattern, decision, or finding | 0+ | highlights |

All other dimensions are optional enrichments on any story type.

## Schema

```yaml
# ── Identity ──────────────────────────────────────────────────────

type: structure | flow | data | resilience | highlight
id: "<kebab-case>"                        # unique across all stories
title: "<Human Readable Title>"
teaches: "<one sentence — what the reader learns>"
group: "<atlas-group-id>"                 # which structural group this centers on
audience: ["<role>"]                      # optional: new-developer, frontend, backend, devops
prerequisites: ["<story-id>"]            # optional: stories that should be read first

# ── Dimensions (include what's relevant) ──────────────────────────

structure:
  nodes: ["<atlas-node-id>"]             # scoped subset of atlas — only this story's cast
  edges:
    - source: "<node-id>"
      target: "<node-id>"
      label: "<short description>"
  narrative: |
    <prose — 3-5 paragraphs, ~200 words>
    <**bold refs** must resolve to atlas node IDs>
  narrative_map:
    - text: "<paragraph text>"
      refs: ["<node-id>"]               # which nodes this paragraph describes

flows:
  - id: "<flow-id>"                      # matches atlas data_flows[].id
    name: "<Human Readable Name>"
    steps:
      - from: "<node-id>"
        to: "<node-id>"
        action: "<verb phrase>"
        technology: "<protocol>"         # optional
    narrative: |
      <prose — 3-5 paragraphs, ~100-150 words>
    narrative_map:
      - text: "<paragraph text>"
        steps: [1, 2]                    # 1-based step indices this paragraph covers

data:
  stores:
    - id: "<state-id>"                   # matches atlas state[].id
      name: "<Human Readable Name>"
      purpose: "source-of-truth | cache | derived | staging"
      readers: ["<node-id>"]
      writers: ["<node-id>"]
  narrative: |
    <prose — 2-3 paragraphs, ~80-120 words>
  narrative_map:
    - text: "<paragraph text>"
      refs: ["<node-id>"]

resilience:
  failures:
    - id: "<failure-id>"                 # matches atlas failure_modes[].id
      trigger: "<what goes wrong>"
      severity: critical | high | medium | low
      cascade:
        - component: "<node-id>"
          effect: "<what happens>"
      detection: ["<signal or 'none'>"]
      recovery: ["<step or 'none'>"]
  narrative: |
    <prose — 3-4 paragraphs, ~100-150 words>
  narrative_map:
    - text: "<paragraph text>"
      refs: ["<node-id>"]
      cascade_steps: [1, 2]              # optional: which cascade steps

observations:
  - id: "<obs-id>"
    type: pattern-match | anti-pattern | gap | api-finding | debt | structural | dependency
    confidence: high | medium | low
    component: "<node-id>"
    evidence:
      file: "<path relative to project root>"
      lines: [14, 28]                   # optional
      snippet: "<code snippet>"          # optional
    finding: "<one sentence>"
    tags: ["<freeform>"]
    detection_method: grep | ast-grep | semgrep | questions | manual
    recommendation: "<what to do>"       # optional, for gaps and debt
    related: ["<obs-id>"]               # links to related observations

highlights:
  - "<key takeaway sentence>"

# ── Self-Assessment ───────────────────────────────────────────────

evaluation:
  groundedness: 0.92                     # claims traced to atlas / total claims
  coverage: 0.85                         # critical nodes referenced / total critical nodes
  claim_count: 15
  ungrounded_claims: []                  # any claims that could not be traced
```

## Narrative Constraints

Narratives follow [narrative-style.md](../../scribe/skills/document/narrative-style.md) principles. Key rules:

**Voice:**
- Scenario-driven — trace real journeys, name concrete actors/actions
- Lead with action — start paragraphs with what happens, not setup
- Decision anchors — explain WHY when mentioning patterns/choices

**Formatting:**
- 2-3 sentences per paragraph, separated by `\n\n`
- Em dashes (—) not double hyphens (--)
- Periods to end sentences, not semicolons

**References:**
- Every `**bold text**` must match an atlas `nodes[].id` or `nodes[].name`
- These render as clickable links in the UI — don't bold non-component text
- Cross-reference other dimensions: flow narratives mention failure modes, failure narratives reference flows they disrupt, state narratives reference flows that read/write

**Length targets:**
- Structure narrative: 3-5 paragraphs (~200 words)
- Flow narrative: 3-5 paragraphs (~100-150 words)
- Data narrative: 2-3 paragraphs (~80-120 words)
- Resilience narrative: 3-4 paragraphs (~100-150 words)

## narrative_map Contract

Every narrative must have a companion `narrative_map`. Rules:

1. Every paragraph in the narrative appears in exactly one `narrative_map` entry
2. Every `refs[]` value must exist in the story's `structure.nodes` or in the atlas
3. Every `steps[]` index must be a valid step in the flow (1-based)
4. Every `cascade_steps[]` index must be a valid cascade entry (1-based)

This enables cross-highlighting: hover paragraph → highlight graph nodes/flow steps.

## Observation Types

| Type | Source methodology | Example |
|------|-------------------|---------|
| `pattern-match` | 4-pass concept detection | "Circuit breaker wraps DummyJSON calls via pybreaker" |
| `anti-pattern` | Concept catalog anti-patterns | "God object in utils.py — 78% of codebase imports it" |
| `gap` | Gap identification (3 checks) | "No rate limiting on public-facing endpoints" |
| `api-finding` | REST hygiene + gateway/hexagonal | "POST used for read-only operation on /users/search" |
| `debt` | Debt scoring | "Hardcoded API URL in 3 files — RECOMMENDED severity" |
| `structural` | Dependency analysis | "Hub module imported by 78% of codebase" |
| `dependency` | Dependency tracing | "Undeclared external dependency on Redis via env var" |

## Evaluation Criteria

**Groundedness** — for each sentence that asserts something about code behavior:
- Can it be traced to a specific detection finding in the atlas? (concepts, api_surface, debt, module_graph)
- Does it reference a valid atlas node ID?
- `groundedness = grounded_claims / total_claims`
- Target: >= 0.85. Below this, revise ungrounded claims.

**Coverage** — across all stories for a project:
- What percentage of "critical" atlas nodes appear in at least one story?
- Critical = components + external_dependencies with criticality=critical + state with purpose=source-of-truth
- `coverage = referenced_critical_nodes / total_critical_nodes`
- Target: >= 0.80. Below this, add highlight stories for uncovered components.

## File Naming

Stories are written to `<project>/.kord/agents/augur/memory/stories/`:

```
<type>-<id>.yaml
```

Examples:
- `structure-api-layer.yaml`
- `flow-ssr-prefetch.yaml`
- `data-query-cache.yaml`
- `resilience-external-api-down.yaml`
- `highlight-zero-waterfall.yaml`

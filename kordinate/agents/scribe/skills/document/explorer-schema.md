# Input Schema: Atlas + Stories + Journeys

Level 3 resource for the document skill. Defines the formats Scribe consumes from Augur's `/analyze` output.

For the full output contract, see `augur-output-contract.md` in Augur's analyze skill.

## atlas.json

Full structural inventory. Scribe uses this for the atlas page, resolving node references, coverage tracking, and node metadata in detail panels.

See [augur-output-contract.md] for the complete atlas schema. Key sections:

- `components[]` — nodes with id, name, type, group, modules, patterns, children
- `flows[]` — typed flows (data, control, event, state, resource) with type-specific step fields
- `state[]` — stores with readers/writers, schema_evolution, concurrency
- `external_dependencies[]` — with criticality and resilience
- `failure_modes[]` — with cascade, detection, recovery
- `concepts` — detected patterns, anti-patterns, gaps
- `observability` — logging, metrics, tracing configuration
- `security` — authentication, authorization, secrets management, threat surface
- `developer_experience` — testing strategy, linting, documentation
- `debt` — score, grade, violations, recommendations

### Node type styling

| Type | Color | Shape |
|------|-------|-------|
| `service` | Blue (#3B82F6) | Rounded rectangle |
| `library` | Slate (#64748B) | Rounded rectangle |
| `worker` | Indigo (#6366F1) | Rounded rectangle |
| `api` | Green (#22C55E) | Rounded rectangle |
| `frontend` | Purple (#A855F7) | Rounded rectangle |
| `store` | Amber (#F59E0B) | Cylinder |
| `gateway` | Rose (#F43F5E) | Hexagon |
| `broker` | Orange (#F97316) | Hexagon |
| `external` | Red (#EF4444) | Octagon |
| `actor` | Teal (#14B8A6) | Ellipse |

---

## Story YAML

Stories are short scoped sections. Each is assembled from building blocks.

### Building blocks

| Block | Purpose | Required? | Multiple? |
|-------|---------|-----------|-----------|
| `summary` | 1-2 paragraphs orienting the reader (~50-80 words) | Yes | No |
| `structures` | Components + typed edges | No | Yes |
| `flows` | Ordered steps through components, typed | No | Yes |
| `observations` | Evidence-backed findings | No | One list |
| `rationale` | Design decisions, trade-offs | No | Yes |

### Schema

```yaml
id: "<kebab-case>"
title: "<Human Readable Title>"
teaches: "<one sentence>"
tags: ["<freeform>"]

summary: |
  <1-2 paragraphs, ~50-80 words, **bold refs** resolve to atlas nodes>

structures:
  - id: "<kebab>"
    title: "<Human Readable>"
    type: "<freeform: component topology, data lineage, infrastructure, security boundary, module graph, ...>"
    nodes:
      - id: "<atlas-node-id>"
        children: ["<atlas-node-id>"]
        observation_ids: ["<obs-id>"]
    edges:
      - from: "<node-id>"
        to: "<node-id>"
        label: "<short>"
        type: "<freeform: depends_on, reads, writes, contains, calls, publishes, subscribes, ...>"

flows:
  - id: "<kebab>"
    title: "<Human Readable>"
    type: "<flow category: data, control, event, state, resource>"
    trigger: "<optional>"
    severity: "<optional, for failure flows>"
    detection: ["<optional>"]
    recovery: ["<optional>"]
    steps:
      - node: "<atlas-node-id>"
        action: "<what it does>"
        effect: "<what happens to it>"
        to: "<atlas-node-id>"
        technology: "<protocol>"
        observation_ids: ["<obs-id>"]

observations:
  - id: "<obs-id>"
    finding: "<one sentence>"
    confidence: "<high|medium|low>"
    component: "<atlas-node-id>"
    evidence:
      file: "<path>"
      lines: [14, 28]
      snippet: "<code>"
    tags: ["<freeform>"]
    detection_method: "<grep|ast-grep|semgrep|questions|manual>"
    recommendation: "<optional>"
    related: ["<obs-id>"]

rationale:
  - id: "<kebab>"
    decision: "<what was decided>"
    context: "<why needed>"
    trade_offs: "<gained vs given up>"
    alternatives: ["<rejected and why>"]

evaluation:
  groundedness: 0.92
  coverage: 0.85
  claim_count: 15
  ungrounded_claims: []
```

### How types guide rendering

**Structure types → graph style:**

| Type | Scribe renders as |
|------|------------------|
| `component topology` | Dagre or cose-bilkent graph |
| `data lineage` | Graph with colored read/write edges |
| `infrastructure` | Graph with k8s-style grouping |
| `security boundary` | Graph with zone shading |
| `module graph` | Compact dependency list or dagre |
| _(unknown)_ | Dagre graph |

**Flow types → diagram style:**

| Type | Scribe renders as |
|------|------------------|
| `data` | Mermaid sequence diagram (data movement, transforms) |
| `control` | Mermaid sequence diagram with decision nodes (gates, branches) |
| `event` | Mermaid sequence diagram with async markers (pub/sub, delivery) |
| `state` | State transition diagram or timeline card (from_state → to_state) |
| `resource` | Lifecycle diagram (acquire → use → release) |

### Observation attachment

Observations are defined once in the story's `observations` list. They attach at three levels:
1. **Story-wide** — exists in the list (default)
2. **Structure node** — via `observation_ids` on a node
3. **Flow step** — via `observation_ids` on a step

Scribe renders attached observations inline near the node/step. Unattached ones appear at the end of the story section.

---

## Journey YAML

An ordered reading path through stories.

```yaml
id: "<kebab>"
title: "<Human Readable>"
description: "<one sentence>"
audience: ["<role>"]
stories:
  - "<story-id>"
  - "<story-id>"
```

Journeys render as **single pages** with stories as sequential sections. The default journey becomes the project index page.

### Guarantees from Augur

| Guarantee | Value |
|-----------|-------|
| Stories per journey | 3-8 |
| Summary length | ~50-80 words |
| Building blocks per story | 1-3 typical |
| All node refs | resolve to atlas |
| All observation_ids | resolve to defined observations |

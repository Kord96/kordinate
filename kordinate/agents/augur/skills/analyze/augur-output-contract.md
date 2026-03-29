# Augur Output Contract

What augur produces and what downstream consumers (scribe, improve loop) can depend on.

This document is the stable interface. Internal methodology may change; these outputs won't break without a version bump.

## Output Layout

After running `/analyze <project>`, augur writes to:

```
<project>/.kord/agents/augur/memory/
  atlas.json            # structural inventory — complete, scoreable
  stories/
    structure-*.yaml    # one per top-level group (3-5 files)
    flow-*.yaml         # one per critical data flow (2-4 files)
    data-*.yaml         # one per state cluster (0+ files)
    resilience-*.yaml   # one per failure mode cluster (0+ files)
    highlight-*.yaml    # notable findings (0+ files)
```

`--detect-only` produces only `atlas.json` (no stories).

---

## atlas.json

Full structural inventory of the codebase. JSON format. Every field that exists in the current `architecture.yaml` v2 is preserved — this is an evolution, not a replacement.

### Top-level shape

```json
{
  "version": "3",
  "generated": "YYYY-MM-DD",
  "project": "<name>",
  "purpose": "<one sentence>",

  "stack": {
    "languages": ["Python", "TypeScript"],
    "frameworks": [{"name": "FastAPI", "concepts": ["dependency-injection"]}],
    "runtime": "<description>"
  },

  "groups": [
    {
      "id": "<kebab-case>",
      "name": "<Human Label>",
      "description": "<what this group represents>",
      "components": ["<component-id>"]
    }
  ],

  "actors": [
    {"id": "<kebab>", "type": "user|service|cron|cli|data-source|external", "description": "..."}
  ],

  "components": [
    {
      "id": "<kebab>",
      "name": "<Human Name>",
      "description": "<one sentence>",
      "type": "service|library|worker|api|frontend|cli|scheduler|store|gateway|broker",
      "group": "<group-id>",
      "modules": ["<path>"],
      "depends_on": ["<component-id>"],
      "abstraction": ["<abstraction-name>"],
      "patterns": ["<pattern-name>"],
      "children": []
    }
  ],

  "data_flows": [
    {
      "id": "<kebab>",
      "name": "<Human Name>",
      "description": "<what this flow accomplishes>",
      "trigger": "<what starts it>",
      "actors": ["<actor-id>"],
      "steps": [
        {"component": "<id>", "action": "<verb>", "data": "<what moves>", "to": "<id>", "technology": "HTTP|gRPC|Kafka|..."}
      ]
    }
  ],

  "state": [
    {
      "id": "<kebab>",
      "concept": "relational-db|document-store|embedded-olap|cache|object-store|message-broker|filesystem|in-memory",
      "technology": "<specific tool>",
      "component": "<component-id>",
      "stores": "<what data>",
      "purpose": "source-of-truth|cache|derived|staging",
      "persistence": "persistent|ephemeral",
      "readers": ["<component-id>"],
      "writers": ["<component-id>"]
    }
  ],

  "events": [
    {"id": "<kebab>", "type": "topic|signal|webhook|cron|pubsub", "name": "...", "producer": "<id>", "consumers": ["<id>"], "data": "..."}
  ],

  "external_dependencies": [
    {
      "id": "<kebab>",
      "name": "<Human Name>",
      "concept": "http-api|message-broker|database|cache|object-store|dns|smtp|nfs|grpc|auth-provider|cdn",
      "technology": "<specific>",
      "components": ["<component-id>"],
      "purpose": "<why needed>",
      "criticality": "critical|important|optional",
      "resilience": {"timeout": true, "retry": false, "circuit_breaker": false, "fallback": null}
    }
  ],

  "failure_modes": [
    {
      "id": "<kebab>",
      "trigger": "<what goes wrong>",
      "severity": "critical|high|medium|low",
      "impact": "<user-visible effect>",
      "cascade": [{"component": "<id>", "effect": "<what happens>"}],
      "detection": ["<signal or 'none'>"],
      "recovery": ["<step or 'none'>"]
    }
  ],

  "concepts": {
    "detected_patterns": [
      {"id": "<name>", "category": "<cat>", "confidence": "high|medium|low", "components": ["<id>"], "evidence": {"files": ["<path>"], "method": "grep|ast-grep|semgrep|questions|manual", "note": "..."}}
    ],
    "detected_anti_patterns": [],
    "gaps": [
      {"id": "<name>", "relevance": "<why expected>", "recommendation": "<what to do>"}
    ],
    "scan_metadata": {
      "catalog_size": {"patterns": 155, "anti_patterns": 77},
      "tools_used": ["grep", "ast-grep", "semgrep"],
      "categories_scanned": ["<category>"]
    }
  },

  "module_graph": {
    "modules": [{"id": "<path>", "imports": ["<path>"], "imported_by": ["<path>"], "role": "hub|shared|leaf|standard"}],
    "circular_dependencies": [{"cycle": ["<mod>", "<mod>"]}],
    "hub_modules": ["<path>"],
    "infrastructure": [{"resource": "<name>", "kind": "<type>", "source": "<namespace>", "notes": "..."}],
    "risks": {
      "hardcoded_endpoints": ["<file:line>"],
      "missing_resilience": [{"file": "<path>", "service_type": "<type>", "missing": ["timeout"]}],
      "unversioned_deps": ["<desc>"]
    }
  },

  "api_surface": {
    "style": "REST|GraphQL|gRPC|WebSocket|SSE|mixed",
    "frameworks": [{"name": "<framework>", "version": "<ver>"}],
    "endpoints": [
      {"method": "GET|POST|PUT|DELETE|PATCH", "path": "</route>", "handler": "<func>", "file": "<path:line>", "auth": "yes|no|gateway|inherited", "validation": "yes|no|partial"}
    ],
    "findings": {
      "critical": [{"description": "...", "files": ["<path:line>"], "count": 1}],
      "recommended": [],
      "minor": []
    },
    "compliance": {
      "gateway": {"status": "compliant|partial|non-compliant", "notes": "..."},
      "hexagonal": {"status": "compliant|partial|non-compliant", "notes": "..."}
    }
  },

  "debt": {
    "score": 15,
    "grade": "C",
    "grade_capped": true,
    "interpretation": "<one sentence>",
    "by_category": [{"category": "Structural|Data|Integration|Resilience|Lifecycle", "points": 5, "violations": 2}],
    "violations": [
      {"severity": "CRITICAL|RECOMMENDED|MINOR", "category": "...", "pattern": "...", "anti_pattern": "...", "components": ["<id>"], "files": ["<path>"], "detail": "...", "points": 5}
    ],
    "recommendations": [
      {"priority": 1, "title": "...", "severity": "...", "category": "...", "files": ["<path>"], "description": "...", "fixes": ["<anti-pattern-id>"]}
    ]
  },

  "metadata": {
    "story_ids": ["structure-api-layer", "flow-ssr-prefetch"],
    "evaluation": {
      "detection_scores": {
        "patterns": {"precision": 0.88, "recall": 0.74, "f1": 0.80},
        "api": {"precision": 1.00, "recall": 0.60, "f1": 0.75},
        "dependencies": {"precision": 0.90, "recall": 0.82, "f1": 0.86},
        "debt": {"precision": 0.85, "recall": 0.60, "f1": 0.70}
      }
    }
  }
}
```

### Constraints scribe can depend on

| Constraint | Value | Hard? |
|-----------|-------|-------|
| Top-level groups | 3-5 | Yes |
| Components | 5-10 (4-12 acceptable) | Guideline |
| Critical data flows | 2-4 | Guideline |
| Failure modes | covers every external dep + stateful component | Yes |
| Component IDs | kebab-case, unique | Yes |
| All cross-references | resolve to existing IDs | Yes |
| Omit empty sections | events, reverse_deps, api_surface when N/A | Yes |

### What changed from architecture.yaml v2

| Change | Old | New |
|--------|-----|-----|
| Format | YAML | JSON |
| Version | "2" | "3" |
| Capabilities | `capabilities` array | `groups` array (simpler, structural-only) |
| Component grouping | via capabilities | `group` field on each component |
| Story link | N/A | `metadata.story_ids` |
| Evaluation | N/A | `metadata.evaluation` |

Everything else is identical. The detection sections (concepts, module_graph, api_surface, debt) are unchanged.

---

## Story Format

Each story is a YAML file in `stories/`. A story is a scoped analytical unit about one architectural concern.

### Story types

| Type | Centers on | Count per project |
|------|-----------|-------------------|
| **structure** | A component group and its internal organization | 3-5 (one per group) |
| **flow** | A data/request path through components | 2-4 (one per critical flow) |
| **data** | A state store cluster and its readers/writers | 0+ (one per significant state) |
| **resilience** | A failure mode and its cascade | 0+ (one per critical failure cluster) |
| **highlight** | A notable pattern, decision, or finding | 0+ (optional) |

### Story shape

```yaml
type: structure | flow | data | resilience | highlight
id: "<kebab-case>"
title: "<Human Readable Title>"
teaches: "<one sentence — what the reader learns>"
group: "<atlas-group-id>"

structure:
  nodes: ["<atlas-node-id>"]
  edges:
    - { source: "<node-id>", target: "<node-id>", label: "<short>" }
  narrative: "<prose — bold **component-refs** resolve to atlas node IDs>"
  narrative_map:
    - { text: "<paragraph text>", refs: ["<node-id>"] }

flows:
  - id: "<flow-id>"
    name: "<Human Name>"
    steps:
      - { from: "<node-id>", to: "<node-id>", action: "<verb phrase>" }
    narrative: "<prose>"
    narrative_map:
      - { text: "<paragraph>", steps: [1, 2] }

data:
  stores:
    - { id: "<state-id>", name: "<name>", purpose: "<purpose>",
        readers: ["<node-id>"], writers: ["<node-id>"] }
  narrative: "<prose>"

resilience:
  failures:
    - { id: "<failure-id>", trigger: "<what>", severity: "critical|high|medium|low",
        cascade: [{ component: "<node-id>", effect: "<what happens>" }],
        detection: ["<signal>"], recovery: ["<step>"] }
  narrative: "<prose>"

observations:
  - { id: "<obs-id>", type: "pattern-match|anti-pattern|gap|api-finding|debt|structural",
      confidence: "high|medium|low", component: "<node-id>",
      evidence: { file: "<path>", lines: [14, 28], snippet: "<code>" },
      finding: "<one sentence>", tags: ["<tag>"],
      detection_method: "grep|ast-grep|semgrep|questions|manual",
      related: ["<obs-id>"] }

highlights:
  - "<key takeaway sentence>"

evaluation:
  groundedness: 0.92
  coverage: 0.85
  claim_count: 15
  ungrounded_claims: []
```

### Dimensions are optional

Not every story needs all dimensions. A structure story might only have `structure` + `observations` + `highlights`. A flow story needs `flows` but might skip `data`.

Required per story type:

| Type | Required dimensions |
|------|-------------------|
| structure | structure |
| flow | flows |
| data | data |
| resilience | resilience |
| highlight | highlights |

All other dimensions are optional enrichments.

### Narrative constraints

- **Scenario-driven**: trace real journeys, name concrete actors/actions
- **Lead with action**: start paragraphs with what happens, not setup
- **Decision anchors**: explain WHY when mentioning patterns/choices
- **2-3 sentences per paragraph**, separated by `\n\n`
- **Every `**bold ref**`** must resolve to an atlas node ID
- **Em dashes** (—) not hyphens
- **Length targets**: 100-200 words per narrative section

### narrative_map contract

Every narrative has a companion `narrative_map` array. Each entry maps a paragraph to the structural elements it describes:

- **Structure narratives**: `refs: ["<node-id>"]`
- **Flow narratives**: `steps: [1, 2, 3]` (1-based step indices)
- **Data narratives**: `refs: ["<node-id>"]`
- **Resilience narratives**: `refs: ["<node-id>"]` and/or `cascade_steps: [1, 2]`

This enables cross-highlighting in the UI: hover paragraph → highlight graph nodes/steps.

---

## Evaluation Scores

Each story carries self-assessment scores. These are computed by augur during story composition.

| Score | Definition | Target |
|-------|-----------|--------|
| **Groundedness** | % of claims traceable to an atlas detection finding + node ID | >= 0.85 |
| **Coverage** | % of critical atlas nodes referenced by at least one story (across all stories) | >= 0.80 |

"Critical" nodes = components + external deps with criticality=critical + state with purpose=source-of-truth.

---

## What Scribe Can Depend On

1. **atlas.json always exists** after `/analyze` completes
2. **stories/ directory exists** (may be empty if `--detect-only`)
3. **All IDs are kebab-case and unique** within their section
4. **All cross-references resolve** — node IDs in stories exist in atlas, observation component refs exist in atlas
5. **3-5 groups** — hard constraint, always met
6. **narrative_map covers every paragraph** in every narrative
7. **Bold refs in narratives match atlas node IDs** — no unresolvable references
8. **Observation evidence includes file paths** — real paths relative to project root

## What May Change (Not Stable)

- Number of stories per type (depends on project complexity)
- Specific observation types (may add new types)
- Detection methodology internals (pass ordering, confidence thresholds)
- Evaluation score thresholds (may adjust as we calibrate)
- Additional metadata fields in atlas.json

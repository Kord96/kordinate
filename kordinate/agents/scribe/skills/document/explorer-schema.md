# Input Schema: Atlas + Stories

Level 3 resource for the document skill. Defines the formats Scribe consumes from Augur's `/analyze` output.

For the full output contract and guarantees, see `augur-output-contract.md` in Augur's analyze skill.

## atlas.json

The structural inventory of the entire codebase. Scribe uses this for:
- The atlas page (full interactive graph)
- Resolving node references from stories
- Coverage tracking (which nodes have stories)
- Node metadata in detail panels (patterns, debt, endpoints, resilience)

### Top-level shape

```json
{
  "version": "3",
  "generated": "YYYY-MM-DD",
  "project": "<name>",
  "purpose": "<one sentence>",

  "stack": {
    "languages": ["<lang>"],
    "frameworks": [{"name": "<framework>", "concepts": ["<concept>"]}],
    "runtime": "<description>"
  },

  "groups": [
    {"id": "<kebab>", "name": "<Human Label>", "description": "...", "components": ["<component-id>"]}
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
      "description": "<what it accomplishes>",
      "trigger": "<what starts it>",
      "actors": ["<actor-id>"],
      "steps": [
        {"component": "<id>", "action": "<verb>", "data": "<what moves>", "to": "<id>", "technology": "<protocol>"}
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
      {"id": "<name>", "category": "<cat>", "confidence": "high|medium|low", "components": ["<id>"], "evidence": {"files": ["<path>"], "method": "...", "note": "..."}}
    ],
    "detected_anti_patterns": [],
    "gaps": [{"id": "<name>", "relevance": "...", "recommendation": "..."}]
  },

  "debt": {
    "score": 15,
    "grade": "C",
    "interpretation": "<one sentence>",
    "violations": [
      {"severity": "CRITICAL|RECOMMENDED|MINOR", "category": "...", "anti_pattern": "...", "components": ["<id>"], "files": ["<path>"], "detail": "...", "points": 5}
    ],
    "recommendations": [
      {"priority": 1, "title": "...", "severity": "...", "description": "...", "files": ["<path>"]}
    ]
  },

  "metadata": {
    "story_ids": ["structure-api-layer", "flow-ssr-prefetch"]
  }
}
```

### Node type styling

| Type | Color | Shape | Used for |
|------|-------|-------|----------|
| `service` | Blue (#3B82F6) | Rounded rectangle | Backend services, API servers |
| `library` | Slate (#64748B) | Rounded rectangle | Shared libraries, utilities |
| `worker` | Indigo (#6366F1) | Rounded rectangle | Background workers, consumers |
| `api` | Green (#22C55E) | Rounded rectangle | API endpoints, route handlers |
| `frontend` | Purple (#A855F7) | Rounded rectangle | UI components, pages |
| `cli` | Slate (#64748B) | Diamond | CLI tools, scripts |
| `store` | Amber (#F59E0B) | Cylinder | Data stores, caches |
| `gateway` | Rose (#F43F5E) | Hexagon | API gateways, load balancers |
| `broker` | Orange (#F97316) | Hexagon | Message brokers, event buses |
| `external` | Red (#EF4444) | Octagon | External dependencies |
| `actor` | Teal (#14B8A6) | Ellipse | Users, external services, cron |

### Guarantees from Augur

| Guarantee | Value |
|-----------|-------|
| Top-level groups | 3-5 (hard) |
| Components | 5-10, acceptable 4-12 |
| Critical data flows | 2-4 |
| All cross-references | resolve to existing IDs |
| Empty sections | omitted, not null |

---

## Story YAML

Each story is a scoped analytical unit. Stories carry no visualization hints — Scribe decides how to render each dimension.

### Shape

```yaml
type: structure | flow | data | resilience | highlight
id: "<kebab-case>"
title: "<Human Readable Title>"
teaches: "<one sentence>"
group: "<atlas-group-id>"
audience: ["<role>"]                      # optional
prerequisites: ["<story-id>"]            # optional

structure:                                # required for all stories
  nodes: ["<atlas-node-id>"]
  edges:
    - { source: "<node-id>", target: "<node-id>", label: "<short>" }
  narrative: "<prose with **bold node refs**>"
  narrative_map:
    - { text: "<paragraph>", refs: ["<node-id>"] }

flows:                                    # optional
  - id: "<flow-id>"
    name: "<Human Name>"
    steps:
      - { from: "<node-id>", to: "<node-id>", action: "<verb>", technology: "<protocol>" }
    narrative: "<prose>"
    narrative_map:
      - { text: "<paragraph>", steps: [1, 2] }

data:                                     # optional
  stores:
    - { id: "<state-id>", name: "<name>", purpose: "<purpose>",
        readers: ["<node-id>"], writers: ["<node-id>"] }
  narrative: "<prose>"
  narrative_map:
    - { text: "<paragraph>", refs: ["<node-id>"] }

resilience:                               # optional
  failures:
    - { id: "<failure-id>", trigger: "<what>", severity: "critical|high|medium|low",
        cascade: [{ component: "<node-id>", effect: "<what>" }],
        detection: ["<signal>"], recovery: ["<step>"] }
  narrative: "<prose>"
  narrative_map:
    - { text: "<paragraph>", refs: ["<node-id>"], cascade_steps: [1, 2] }

observations:                             # optional
  - id: "<obs-id>"
    type: pattern-match | anti-pattern | gap | api-finding | debt | structural | dependency
    confidence: high | medium | low
    component: "<node-id>"
    evidence:
      file: "<path>"
      lines: [14, 28]                    # optional
      snippet: "<code>"                   # optional
    finding: "<one sentence>"
    tags: ["<freeform>"]
    detection_method: grep | ast-grep | semgrep | questions | manual
    recommendation: "<what to do>"        # optional
    related: ["<obs-id>"]

highlights:                               # optional
  - "<key takeaway sentence>"

evaluation:
  groundedness: 0.92
  coverage: 0.85
  claim_count: 15
  ungrounded_claims: []
```

### Story types and required dimensions

| Type | Required | Typical extras |
|------|----------|---------------|
| `structure` | structure | observations, highlights |
| `flow` | flows | structure, data, observations |
| `data` | data | structure, observations |
| `resilience` | resilience | structure, flows, observations |
| `highlight` | highlights | structure, observations |

### narrative_map contract

Every narrative has a companion `narrative_map`. Scribe depends on these for cross-highlighting:

- Every paragraph appears in exactly one entry
- `refs[]` values exist in the story's `structure.nodes` or atlas
- `steps[]` are 1-based indices into the flow's steps array
- `cascade_steps[]` are 1-based indices into the failure's cascade array

### Observation types

| Type | Rendered as | Visual treatment |
|------|------------|-----------------|
| `pattern-match` | Evidence card | Blue/green — positive finding |
| `anti-pattern` | Warning card | Amber — concern |
| `gap` | Warning card with recommendation | Amber with action |
| `api-finding` | Evidence card | Severity-colored |
| `debt` | Warning card | Severity-colored |
| `structural` | Evidence card | Blue — neutral finding |
| `dependency` | Evidence card | Blue — neutral finding |

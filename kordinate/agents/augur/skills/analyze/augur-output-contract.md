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
  journeys/
    overview.yaml       # architecture overview (always present)
    onboard-*.yaml      # audience-specific reading paths (0+ files)
    resilience-review.yaml  # if failure modes exist (0-1 file)
```

`--detect-only` produces only `atlas.json` (no stories or journeys).

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

Each story is a YAML file in `stories/`. A story is a short scoped section about one architectural concern, assembled from building blocks.

### Building blocks

| Block | Purpose | Multiple per story? |
|-------|---------|-------------------|
| **summary** | 1-2 short paragraphs (~50-80 words) orienting the reader | No (required) |
| **structures** | Nested components + typed edges | Yes |
| **flows** | Ordered steps through components, typed | Yes |
| **observations** | Evidence-backed findings, attachable to nodes/steps | One list |
| **rationale** | Design decisions, trade-offs, alternatives | Yes |

### Story shape

```yaml
id: "<kebab-case>"
title: "<Human Readable Title>"
teaches: "<one sentence>"
tags: ["<freeform>"]

summary: "<1-2 short paragraphs, ~50-80 words. **bold refs** resolve to atlas node IDs.>"

structures:
  - id: "<kebab>"
    title: "<Human Readable>"
    type: "<freeform: component topology, data lineage, infrastructure, security boundary, ...>"
    nodes:
      - id: "<atlas-node-id>"
        children: ["<atlas-node-id>"]
        observation_ids: ["<obs-id>"]
    edges:
      - { from: "<node-id>", to: "<node-id>", label: "<short>", type: "<freeform: depends_on, reads, writes, contains, calls, ...>" }

flows:
  - id: "<kebab>"
    title: "<Human Readable>"
    type: "<freeform: request path, failure cascade, data pipeline, event chain, ...>"
    trigger: "<what starts this>"
    severity: "<critical|high|medium|low>"       # for failure flows
    detection: ["<signal or 'none'>"]            # for failure flows
    recovery: ["<step or 'none'>"]               # for failure flows
    steps:
      - { node: "<atlas-node-id>", action: "<what it does>", effect: "<what happens to it>", to: "<node-id>", technology: "<protocol>", observation_ids: ["<obs-id>"] }

observations:
  - { id: "<obs-id>", finding: "<one sentence>", confidence: "<high|medium|low>",
      component: "<atlas-node-id>",
      evidence: { file: "<path>", lines: [14, 28], snippet: "<code>" },
      tags: ["<freeform>"], detection_method: "<grep|ast-grep|semgrep|questions|manual>",
      recommendation: "<what to do>", related: ["<obs-id>"] }

rationale:
  - { id: "<kebab>", decision: "<what>", context: "<why needed>",
      trade_offs: "<gained vs given up>", alternatives: ["<rejected and why>"] }

evaluation:
  groundedness: 0.92
  coverage: 0.85
  claim_count: 15
  ungrounded_claims: []
```

### Key differences from previous schema

- **No story types** — stories are defined by their building blocks, not a type enum
- **Structures and flows are typed with freeform strings** — augur invents types as needed
- **Multiple structures and flows per story** — e.g., component topology + data lineage, or happy path + failure cascade
- **Observations attach to nodes and steps** via `observation_ids`, not just story-wide
- **Rationale block** captures the "why" — decisions, trade-offs, alternatives
- **No narrative_map** — summaries are short enough that paragraph-level mapping isn't needed

### Narrative constraints

- **~50-80 words** per summary — orienting paragraph, not essay
- **Scenario-driven**: trace real journeys, name concrete actors
- **Lead with action**: start with what happens, not setup
- Every `**bold ref**` must resolve to an atlas node ID
- Em dashes (—) not hyphens

---

## Evaluation Scores

Each story carries self-assessment scores. These are computed by augur during story composition.

| Score | Definition | Target |
|-------|-----------|--------|
| **Groundedness** | % of claims traceable to an atlas detection finding + node ID | >= 0.85 |
| **Coverage** | % of critical atlas nodes referenced by at least one story (across all stories) | >= 0.80 |

"Critical" nodes = components + external deps with criticality=critical + state with purpose=source-of-truth.

---

## Journey Format

A journey is an ordered reading path through stories for a specific audience.

```yaml
id: "<kebab-case>"
title: "<Human Readable Title>"
description: "<one sentence — what the reader achieves>"
audience: ["<role>"]
stories:
  - "<story-id>"    # ordered sequence
  - "<story-id>"
```

**Guarantees:**
- `overview` journey always exists (all structure stories + 1-2 key flows)
- Every story ID in a journey exists in `stories/`
- Journeys contain 3-8 stories
- First story is always a structure story

---

## What Scribe Can Depend On

1. **atlas.json always exists** after `/analyze` completes
2. **stories/ directory exists** (may be empty if `--detect-only`)
3. **journeys/ directory exists** with at least `overview.yaml` (empty if `--detect-only`)
4. **All IDs are kebab-case and unique** within their section
5. **All cross-references resolve** — node IDs in stories exist in atlas, story IDs in journeys exist in stories/
6. **3-5 groups** — hard constraint, always met
7. **narrative_map covers every paragraph** in every narrative
8. **Bold refs in narratives match atlas node IDs** — no unresolvable references
9. **Observation evidence includes file paths** — real paths relative to project root
10. **Journeys are ordered** — render stories in the sequence given

## What May Change (Not Stable)

- Number of stories per type (depends on project complexity)
- Number and types of journeys (depends on project)
- Specific observation types (may add new types)
- Detection methodology internals (pass ordering, confidence thresholds)
- Evaluation score thresholds (may adjust as we calibrate)
- Additional metadata fields in atlas.json

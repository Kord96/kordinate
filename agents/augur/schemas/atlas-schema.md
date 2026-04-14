# atlas.json Schema (v4)

Canonical contract for Augur semantic `atlas.json`.

Use this file as the authority for:
- required top-level fields
- allowed optional fields
- component hierarchy rules
- cross-reference rules
- prose style for atlas text

Do not invent alternate atlas shapes.

## Prose Rules

Apply these rules to atlas prose fields such as `purpose`, `description`, and `summary`:

- state facts about the system, not facts about the document
- name concrete components, stores, protocols, and files when known
- keep prose short and direct
- prefer one sentence when one sentence is enough
- avoid filler such as "this section describes" or "there is a potential issue"

## Required Top-Level Fields

Every semantic atlas must contain exactly these required top-level fields:

```json
[
  "version",
  "generated",
  "project",
  "purpose",
  "components",
  "flows",
  "state",
  "external_dependencies",
  "concepts",
  "tensions"
]
```

These fields are optional and should appear only when grounded:
- `domain_model`
- `actors`
- `events`
- `metadata`

These legacy fields must not appear:
- `groups`
- `stack`
- `debt`
- `api_surface`
- `security`
- `developer_experience`

## Core Rules

- `version` must be `"4"`.
- All `id` fields are kebab-case and unique within their section.
- `components` are the backbone of the atlas and must form a hierarchy.
- Top-level components are the components with no `parent`.
- Prefer `3-5` top-level components.
- Component hierarchy depth should stay within `3`.
- Use `parent` as the canonical hierarchy link.
- Include `children` only when you can keep it consistent with `parent`.
- `components[].depends_on` may reference only component ids.
- Outside systems must not appear in `components[].depends_on`.
  Put them in `external_dependencies` or `state`.
- `flows[].steps[].component` must reference a real component id.
- `flows[].steps[].to`, when present, must reference a real component, state, or external dependency id.
- `flows[].actors[]` must reference real actor ids when `actors` is present.
- `grounded_in` is expected on flows, state entries, and attached health failure modes.
- `tensions` are grounded architecture-level contradictions or trade-offs, not generic debt backlogs.

## Minimal Valid Shape

```json
{
  "version": "4",
  "generated": "<YYYY-MM-DD>",
  "project": "<project-name>",
  "purpose": "<one short sentence>",
  "components": [],
  "flows": [],
  "state": [],
  "external_dependencies": [],
  "concepts": {
    "detected_patterns": [],
    "detected_anti_patterns": [],
    "gaps": []
  },
  "tensions": []
}
```

## Section Schemas

### `purpose`

```json
"purpose": "<one short sentence, max 15 words>"
```

### `domain_model` (optional)

```json
"domain_model": {
  "primary": "<concept-name from catalog>",
  "description": "<one sentence>",
  "entities": ["<entity>"],
  "relationships": ["<relationship>"],
  "bounded_contexts": [
    {
      "id": "<kebab-case>",
      "name": "<Human Label>",
      "description": "<one sentence>",
      "entities": ["<entity>"],
      "modules": ["<path/to/module>"],
      "ubiquitous_language": {
        "<term>": "<definition>"
      }
    }
  ]
}
```

### `actors` (optional)

```json
"actors": [
  {
    "id": "<kebab-case>",
    "type": "user | service | cron | cli | data-source | external",
    "description": "<one sentence>"
  }
]
```

### `components`

```json
"components": [
  {
    "id": "<kebab-case>",
    "name": "<Human Readable Name>",
    "description": "<one sentence>",
    "type": "service | library | worker | api | frontend | cli | scheduler | store | gateway | broker",
    "parent": "<component-id or null>",
    "children": ["<component-id>"],
    "modules": ["<path/to/module>"],
    "depends_on": ["<component-id>"],
    "abstraction": ["<abstraction-name>"],
    "patterns": ["<pattern-name>"],
    "health": {
      "failure_modes": [
        {
          "id": "<kebab-case>",
          "trigger": "<what goes wrong>",
          "impact": "<what users or operators experience>",
          "signals": ["<metric or symptom>"],
          "gaps": ["<missing guardrail>"],
          "recovery": ["<recovery step>"],
          "severity": "critical | high | medium | low",
          "grounded_in": ["<file:line>"]
        }
      ],
      "gaps": ["<missing signal or resilience control>"]
    }
  }
]
```

Hierarchy rules:
- use `parent` for the canonical relationship
- include `children` only when you can state it consistently
- every child id in `children` must reference a real component
- top-level components should be real architecture slices, not synthetic presentation buckets

### `flows`

```json
"flows": [
  {
    "id": "<kebab-case>",
    "type": "data | control | event | state | resource",
    "name": "<Human Readable Flow Name>",
    "description": "<one sentence>",
    "trigger": "<what starts it>",
    "actors": ["<actor-id>"],
    "grounded_in": ["<file:line>"],
    "health": {
      "failure_modes": [
        {
          "id": "<kebab-case>",
          "trigger": "<what breaks this flow>",
          "impact": "<what the caller or user experiences>",
          "signals": ["<flow-level signal>"],
          "gaps": ["<missing flow instrumentation>"],
          "recovery": ["<fallback or recovery step>"],
          "severity": "critical | high | medium | low",
          "grounded_in": ["<file:line>"]
        }
      ],
      "gaps": ["<missing flow health visibility>"]
    },
    "steps": [
      {
        "component": "<component-id>",
        "action": "<verb phrase>",
        "to": "<component-id | state-id | external-dependency-id>",
        "data": "<what moves>",
        "technology": "<protocol or transport>",
        "transform": "<what changes about the data>",
        "condition": "<predicate>",
        "gate": "<auth | validation | rate-limit | feature-flag>",
        "topic": "<topic or channel>",
        "delivery": "<at-most-once | at-least-once | exactly-once>",
        "from_state": "<state before>",
        "to_state": "<state after>",
        "resource": "<connection | lock | file-handle | memory | thread>",
        "operation": "<acquire | use | release | timeout>"
      }
    ]
  }
]
```

Flow-step rules:
- every step must contain `component` and `action`
- use only the subtype fields that match the flow `type`
- do not mix unrelated subtype fields in the same step unless the code clearly does both

### `state`

```json
"state": [
  {
    "id": "<kebab-case>",
    "concept": "relational-db | document-store | embedded-olap | cache | object-store | message-broker | filesystem | in-memory",
    "technology": "<specific technology>",
    "component": "<component-id>",
    "stores": "<what data>",
    "purpose": "source-of-truth | cache | derived | staging",
    "persistence": "persistent | ephemeral",
    "readers": ["<component-id>"],
    "writers": ["<component-id>"],
    "grounded_in": ["<file:line>"]
  }
]
```

### `events` (optional)

```json
"events": [
  {
    "id": "<kebab-case>",
    "type": "topic | signal | webhook | cron | pubsub",
    "name": "<event name>",
    "producer": "<component-id>",
    "consumers": ["<component-id>"],
    "data": "<what the event carries>"
  }
]
```

### `external_dependencies`

```json
"external_dependencies": [
  {
    "id": "<kebab-case>",
    "name": "<Human Readable Name>",
    "concept": "http-api | message-broker | database | cache | object-store | dns | smtp | nfs | grpc | auth-provider | cdn",
    "technology": "<specific if known>",
    "components": ["<component-id>"],
    "purpose": "<why needed>",
    "criticality": "critical | important | optional",
    "health": {
      "failure_modes": [
        {
          "id": "<kebab-case>",
          "trigger": "<dependency degradation or outage>",
          "impact": "<what features degrade>",
          "signals": ["<signal>"],
          "gaps": ["<missing timeout/retry/circuit-breaker>"],
          "recovery": ["<fallback or operator action>"],
          "severity": "critical | high | medium | low",
          "grounded_in": ["<file:line>"]
        }
      ],
      "gaps": ["<missing protection or signal>"]
    }
  }
]
```

### `concepts`

```json
"concepts": {
  "detected_patterns": [
    {
      "id": "<pattern-name>",
      "category": "<category from index>",
      "confidence": "high | medium | low",
      "components": ["<component-id>"],
      "evidence": {
        "fact_ids": ["<fact-id>"],
        "files": ["<path>"],
        "method": "grep | ast-grep | semgrep | question | manual | inferred-from-facts",
        "detector_class": "ast | semgrep | signature | regex | manifest | question | inference",
        "note": "<one sentence>",
        "questions_asked": ["<question id>"]
      }
    }
  ],
  "detected_anti_patterns": [
    {
      "id": "<anti-pattern-name>",
      "category": "<category from index>",
      "confidence": "high | medium | low",
      "components": ["<component-id>"],
      "evidence": {
        "fact_ids": ["<fact-id>"],
        "files": ["<path>"],
        "method": "grep | ast-grep | semgrep | question | manual | inferred-from-facts",
        "detector_class": "ast | semgrep | signature | regex | manifest | question | inference",
        "note": "<one sentence>",
        "questions_asked": ["<question id>"]
      }
    }
  ],
  "gaps": [
    {
      "id": "<pattern-name>",
      "relevance": "<why it's expected>",
      "recommendation": "<what to do>"
    }
  ]
}
```

### `tensions`

```json
"tensions": [
  {
    "id": "<kebab-case>",
    "title": "<Human Readable Title>",
    "summary": "<one sentence>",
    "components": ["<component-id>"],
    "trade_off": "<what is being balanced>",
    "evidence": ["<file:line>"]
  }
]
```

Use `tensions` only for grounded architecture-level contradictions or trade-offs.
Do not turn every bug, TODO, or cleanup item into a tension.

### `metadata` (optional)

```json
"metadata": {
  "analysis_mode": "full | incremental",
  "base_sha": "<sha or empty>",
  "affected_components": ["<component-id>"],
  "story_ids": ["<story-id>"]
}
```

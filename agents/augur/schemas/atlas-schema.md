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
- prefer concrete mechanism names from code when they are available, especially for flows, stores, registries, hooks, and lifecycle stages
- prefer one mechanism per sentence unless the implementation clearly binds them together
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
- Prefer `3-5` top-level components for substantial services and platforms, but allow `2-6` when the repo shape genuinely calls for it.
- Component hierarchy depth should stay within `3`.
- Use `parent` as the canonical hierarchy link.
- Include `children` only when you can keep it consistent with `parent`.
- `components[].depends_on` may reference only component ids.
- `components[].depends_on` means runtime reliance: the component cannot perform its primary role without the target.
- Do not use `depends_on` for mere co-location, adjacency, hosting, serving, embedding, or navigational relationships.
- Prefer an acyclic dependency graph. Mutual dependencies require unusually strong evidence.
- Outside systems must not appear in `components[].depends_on`.
  Put them in `external_dependencies` or `state`.
- `flows[].steps[].component` must reference a real component id.
- `flows[].steps[].to`, when present, must reference a real component, state, or external dependency id.
- `flows[].actors[]` must reference real actor ids when `actors` is present.
- `grounded_in` is expected on flows, state entries, and attached health failure modes.
- when a state entry is grounded in a file that appears in `facts/state-seeds.json`, prefer exact structs, enums, maps, config variants, or storage selector names from that seed over abstract storage paraphrases
- `tensions` are grounded architecture-level contradictions or trade-offs, not generic debt backlogs.
- use the canonical path rules from `augur-output-contract.md` for `modules`, `grounded_in`, and concept evidence file references

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
- every entry in `components[].modules` must resolve to a real repo file or directory

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
    "concept": "database | relational-db | document-store | embedded-olap | cache | object-store | message-broker | filesystem | in-memory",
    "technology": "<specific technology>",
    "component": "<component-id>",
    "stores": "<what data>",
    "purpose": "source-of-truth | cache | derived | staging",
    "persistence": "persistent | ephemeral | mixed",
    "readers": ["<component-id>"],
    "writers": ["<component-id>"],
    "grounded_in": ["<file:line>"]
  }
]
```

State modeling rules:
- keep `concept` truthful to the broadest grounded backend class
- if backend class varies by deployment or configuration, prefer a general label such as `database` over a narrower label that is only sometimes true
- if persistence varies by backend selection, use `mixed` or explain the variability clearly in `technology`
- do not label configurable durable state as purely `ephemeral`, or configurable SQL/NoSQL state as purely `relational-db`, unless the repo truly requires one mode

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
      "summary": "<one sentence on how this pattern manifests in this repo>",
      "why_it_matters": "<one sentence on why this pattern affects the architecture here>",
      "components": ["<component-id>"],
      "flows": ["<flow-id>"],
      "state": ["<state-id>"],
      "grounded_in": ["<file:line>"],
      "evidence": {
        "fact_ids": ["<fact-id>"],
        "files": ["<path>"],
        "components": ["<component-id>"],
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
      "summary": "<one sentence on how this anti-pattern shows up here>",
      "why_it_matters": "<one sentence on the architectural risk or cost>",
      "components": ["<component-id>"],
      "flows": ["<flow-id>"],
      "state": ["<state-id>"],
      "grounded_in": ["<file:line>"],
      "evidence": {
        "fact_ids": ["<fact-id>"],
        "files": ["<path>"],
        "components": ["<component-id>"],
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
      "recommendation": "<what to do>",
      "components": ["<component-id>"],
      "grounded_in": ["<file:line>"],
      "evidence": {
        "files": ["<path>"],
        "note": "<one sentence>"
      }
    }
  ]
}
```

Concept rules:
- keep concept ids grounded in the ontology or detector vocabulary, but make `summary` and `why_it_matters` repo-specific
- concepts are cross-cutting interpretation records, not duplicate component descriptions
- every detected pattern or anti-pattern should link to at least one real component, flow, or state entry
- every detected pattern or anti-pattern should include grounded evidence through `grounded_in` or `evidence.files`
- treat every concept entry as a resolved architectural judgment, not as a raw detector suggestion
- only keep a concept when the repo code plus deterministic evidence make it materially useful to the architecture model
- if a concept remains ambiguous after semantic questions and repo inspection, prefer omitting it over emitting a generic filler pattern
- if you keep a tentative concept at all, the uncertainty itself must matter architecturally and should be stated in `summary` or `why_it_matters`
- avoid empty generic labels with no repo-specific manifestation text; explain how the concept changes the architecture here
- do not duplicate a component name as a concept unless the concept adds cross-cutting meaning beyond the component boundary
- use `gaps` only for grounded missing capabilities or policy holes that materially affect the architecture, not generic wishlist items
- concept-driven monitoring or business expectations should only appear when the concept is well grounded enough to justify them

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

### `metadata`

```json
"metadata": {
  "analysis_mode": "full | incremental",
  "base_sha": "<sha or empty>",
  "affected_components": ["<component-id>"],
  "story_ids": ["<story-id>"],
  "stack_summary": "<short stack or execution summary>",
  "languages": ["<language>"],
  "frameworks": [
    {
      "name": "<framework>",
      "language": "<language>",
      "framework_kind": "<kind>",
      "scope": "<scope>",
      "status": "accepted | tentative"
    }
  ],
  "technologies": ["<technology>"]
}
```

Metadata rules:
- include `metadata` in normal full and incremental outputs; omit it only if the run truly has no deterministic stack evidence to summarize
- `stack_summary`, `languages`, `frameworks`, and `technologies` form a compact resolved stack summary and should normally be present when deterministic facts are available
- keep `metadata.frameworks` compact and operational; it is part of a resolved stack summary, not a second architecture map
- list only frameworks that materially influence interpretation of components, flows, or concepts
- `languages` and `technologies` should summarize the stack, not enumerate every incidental library

# atlas.json Schema (v3)

Level 3 resource for the analyze skill. Referenced from step 9 (write atlas). Defines the structural inventory output format.

Version 3 evolves from architecture.yaml v2: JSON format, `groups` replace `capabilities`, adds `metadata` section. All detection sections (concepts, module_graph, api_surface, debt) are unchanged.

## Schema

```json
{
  "version": "3",
  "generated": "<YYYY-MM-DD>",
  "project": "<project-name>",

  "purpose": "<one sentence — what the system does>",

  "domain_model": {
    "primary": "<concept-name from catalog, e.g., property-graph, ledger, catalog>",
    "description": "<one sentence — what shape the core data takes>",
    "entities": ["<core entity types in the domain>"],
    "relationships": ["<how entities connect>"]
  },

  "stack": {
    "languages": ["<Python>", "<TypeScript>"],
    "frameworks": [
      {"name": "<framework>", "concepts": ["<concept-name>"]}
    ],
    "runtime": "<description of how it runs>"
  },

  // ── Structure ──────────────────────────────────────────────────

  "groups": [
    {
      "id": "<kebab-case>",
      "name": "<Human Label>",
      "description": "<what this group represents — one sentence>",
      "components": ["<component-id>"]
    }
  ],

  "actors": [
    {
      "id": "<kebab-case>",
      "type": "user | service | cron | cli | data-source | external",
      "description": "<what they do with the system>"
    }
  ],

  "components": [
    {
      "id": "<kebab-case>",
      "name": "<Human Readable Name>",
      "description": "<what it does — one sentence>",
      "type": "service | library | worker | api | frontend | cli | scheduler | store | gateway | broker",
      "group": "<group-id>",
      "modules": ["<path/to/module>"],
      "depends_on": ["<component-id>"],
      "abstraction": ["<abstraction-name>"],
      "patterns": ["<pattern-name>"],
      "deployment": {
        "namespace": "<k8s namespace>",
        "kind": "<Deployment | StatefulSet | CronJob | Pod>",
        "replicas": "<count>",
        "node": "<node name or selector>"
      },
      "children": []
    }
  ],

  // ── Behavior ───────────────────────────────────────────────────

  "data_flows": [
    {
      "id": "<kebab-case>",
      "actors": ["<actor-id>"],
      "name": "<Human Readable Flow Name>",
      "description": "<what this flow accomplishes>",
      "trigger": "<what starts it>",
      "grounded_in": ["<file:line>"],
      "steps": [
        {
          "component": "<component-id>",
          "action": "<verb phrase>",
          "data": "<what moves>",
          "to": "<component-id>",
          "technology": "<protocol or transport>"
        }
      ]
    }
  ],

  "state": [
    {
      "id": "<kebab-case>",
      "concept": "relational-db | document-store | embedded-olap | cache | object-store | message-broker | filesystem | in-memory",
      "technology": "<specific: PostgreSQL | DuckDB | Redis | etc.>",
      "component": "<component-id>",
      "stores": "<what data>",
      "purpose": "source-of-truth | cache | derived | staging",
      "persistence": "persistent | ephemeral",
      "readers": ["<component-id>"],
      "writers": ["<component-id>"],
      "grounded_in": ["<file:line>"]
    }
  ],

  "events": [
    {
      "id": "<kebab-case>",
      "type": "topic | signal | webhook | cron | pubsub",
      "name": "<topic.name or event name>",
      "producer": "<component-id>",
      "consumers": ["<component-id>"],
      "data": "<what the event carries>"
    }
  ],

  "external_dependencies": [
    {
      "id": "<kebab-case>",
      "name": "<Human Readable Name>",
      "concept": "http-api | message-broker | database | cache | object-store | dns | smtp | nfs | grpc | auth-provider | cdn",
      "technology": "<specific if known>",
      "components": ["<component-id>"],
      "purpose": "<why needed>",
      "criticality": "critical | important | optional",
      "resilience": {
        "timeout": true,
        "retry": false,
        "circuit_breaker": false,
        "fallback": "<description or null>"
      }
    }
  ],

  "failure_modes": [
    {
      "id": "<kebab-case>",
      "trigger": "<what goes wrong>",
      "cascade": [
        {"component": "<component-id>", "effect": "<what happens>"}
      ],
      "impact": "<what end users experience>",
      "detection": ["<signal — metric, log, error, or 'none'>"],
      "recovery": ["<step — automatic or manual>"],
      "severity": "critical | high | medium | low",
      "grounded_in": ["<file:line>"]
    }
  ],

  // ── Concepts ───────────────────────────────────────────────────

  "concepts": {
    "detected_patterns": [
      {
        "id": "<pattern-name>",
        "category": "<category from index>",
        "confidence": "high | medium | low",
        "components": ["<component-id>"],
        "evidence": {
          "files": ["<path>"],
          "method": "grep | ast-grep | semgrep | questions | manual",
          "note": "<one sentence>"
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
          "files": ["<path>"],
          "method": "grep | ast-grep | semgrep | questions | manual",
          "note": "<one sentence>"
        }
      }
    ],
    "gaps": [
      {
        "id": "<pattern-name>",
        "relevance": "<why it's expected>",
        "recommendation": "<what to do>"
      }
    ],
    "scan_metadata": {
      "catalog_size": {"patterns": "<N>", "anti_patterns": "<N>"},
      "tools_used": ["grep", "ast-grep", "semgrep"],
      "categories_scanned": ["<category>"]
    }
  },

  // ── Module Graph ───────────────────────────────────────────────

  "module_graph": {
    "modules": [
      {
        "id": "<module-path>",
        "imports": ["<module-path>"],
        "imported_by": ["<module-path>"],
        "role": "hub | shared | leaf | standard"
      }
    ],
    "circular_dependencies": [
      {"cycle": ["<module>", "<module>"]}
    ],
    "hub_modules": ["<module-path>"],
    "infrastructure": [
      {
        "resource": "<name>",
        "kind": "<PVC | ConfigMap | Secret | Service | StatefulSet | aws_rds_instance>",
        "source": "<namespace or Terraform module>",
        "notes": "<detail>"
      }
    ],
    "inter_service": [
      {
        "service": "<name>",
        "discovered_in": "<file>",
        "pattern": "<*_URL | depends_on | connection string>",
        "value": "<the reference>"
      }
    ],
    "reverse_dependencies": [
      {
        "project": "<sibling project name>",
        "reference_type": "import | config | k8s-manifest",
        "files": ["<path>"]
      }
    ],
    "risks": {
      "hardcoded_endpoints": ["<file:line>"],
      "missing_resilience": [
        {"file": "<path>", "service_type": "<type>", "missing": ["timeout", "retry", "circuit_breaker"]}
      ],
      "unversioned_deps": ["<description>"]
    }
  },

  // ── API Surface ────────────────────────────────────────────────

  "api_surface": {
    "style": "REST | GraphQL | gRPC | WebSocket | SSE | mixed",
    "frameworks": [
      {"name": "<framework>", "version": "<version if known>"}
    ],
    "endpoints": [
      {
        "method": "GET | POST | PUT | DELETE | PATCH",
        "path": "</route>",
        "handler": "<function name>",
        "file": "<path:line>",
        "auth": "yes | no | gateway | inherited",
        "validation": "yes | no | partial"
      }
    ],
    "findings": {
      "critical": [{"description": "<finding>", "files": ["<path:line>"], "count": "<N>"}],
      "recommended": [{"description": "<finding>", "files": ["<path:line>"], "count": "<N>"}],
      "minor": [{"description": "<finding>", "files": ["<path:line>"], "count": "<N>"}]
    },
    "compliance": {
      "gateway": {"status": "compliant | partial | non-compliant", "notes": "<explanation>"},
      "hexagonal": {"status": "compliant | partial | non-compliant", "notes": "<explanation>"},
      "external_gateway": "<Kong | AWS API Gateway | null>"
    }
  },

  // ── Debt ───────────────────────────────────────────────────────

  "debt": {
    "score": "<N>",
    "grade": "A | B | C | D | F",
    "grade_capped": true,
    "interpretation": "<one sentence>",
    "by_category": [
      {"category": "Structural | Data | Integration | Resilience | Lifecycle", "points": "<N>", "violations": "<N>"}
    ],
    "violations": [
      {
        "severity": "CRITICAL | RECOMMENDED | MINOR",
        "category": "<category>",
        "pattern": "<source pattern>",
        "anti_pattern": "<what was violated>",
        "components": ["<component-id>"],
        "files": ["<path>"],
        "detail": "<one sentence>",
        "points": "<N>"
      }
    ],
    "recommendations": [
      {
        "priority": "<1-7>",
        "title": "<short title>",
        "severity": "CRITICAL | RECOMMENDED | MINOR",
        "category": "<category>",
        "files": ["<path>"],
        "description": "<what to fix and why>",
        "fixes": ["<anti-pattern-id>"]
      }
    ]
  },

  // ── Metadata (v3) ──────────────────────────────────────────────

  "metadata": {
    "story_ids": ["<story-id>"],
    "flags": {
      "detect_only": false
    }
  }
}
```

## What Changed from v2

| Change | v2 | v3 |
|--------|-----|-----|
| Format | YAML | JSON |
| Version | `"2"` | `"3"` |
| Grouping | `capabilities` (business-level, actors + components) | `groups` (structural clusters, components only) |
| Component group ref | via capabilities | `group` field on each component |
| Story link | N/A | `metadata.story_ids` |
| State readers/writers | N/A | `readers` and `writers` arrays on state entries |
| Flags | N/A | `metadata.flags` |

All detection sections (concepts, module_graph, api_surface, debt) are structurally identical to v2.

## Conventions

- All `id` fields are kebab-case, unique within their section
- Cross-references use `id` strings, not indices
- `concept` fields use generic infrastructure terms, `technology` fields name the specific tool
- `abstraction` values come from `abstractions.md`
- Component `type: store` covers embedded data persistence. External databases appear in `external_dependencies`
- **Components should number 5-10** for most projects. >12 means not abstracting enough. <4 means over-abstracting
- **Groups must number 3-5.** This is a hard constraint. If you have more, merge related groups. If you have fewer, the project may be too small to warrant grouping.
- **Data flows trace critical paths**, not every code path. 2-4 flows typical
- **Failure modes should cover** every external dependency and every stateful component
- Components nest via `children`. Don't nest deeper than the code's natural structure
- `deployment` field enables the deployment viewpoint. Only add to components that map to a k8s workload
- `technology` on flow steps enables annotated sequence diagrams
- Omit `events` if the project has none
- Omit `module_graph.reverse_dependencies` if `--reverse` was not used
- Omit `api_surface` entirely if no endpoints were found and the project is not an API
- Omit empty severity lists in `api_surface.findings` and empty `debt.by_category` entries
- **`grounded_in`** on data_flows, state, failure_modes, and concept evidence lists the source files that justify the entry. Format: `["<file:line>"]`. These are used during evaluation to verify claims against actual code — not against other atlas entries (which would be circular)

## Group Assignment

Groups are structural clusters — not business capabilities, not deployment units. A group should contain components that share a deployment boundary, data flow path, or architectural concern.

Guidelines:
- Follow C4 Container model: top-level groups are runtime boundaries (Server, Browser, External), not code modules
- Synthetic `external` and `actors` groups count toward the 3-5 limit
- Small projects (<15 nodes) should aim for 3 groups
- If two groups have only 1-2 nodes each, they belong together
- After drafting, count groups. If >5, merge the two most closely related. Repeat until ≤5

## Minimal Skeleton

```json
{
  "version": "3",
  "generated": "YYYY-MM-DD",
  "project": "<name>",
  "purpose": "",
  "stack": {"languages": [], "frameworks": [], "runtime": ""},
  "groups": [],
  "actors": [],
  "components": [],
  "data_flows": [],
  "state": [],
  "external_dependencies": [],
  "failure_modes": [],
  "concepts": {
    "detected_patterns": [],
    "detected_anti_patterns": [],
    "gaps": [],
    "scan_metadata": {"catalog_size": {"patterns": 0, "anti_patterns": 0}, "tools_used": [], "categories_scanned": []}
  },
  "module_graph": {
    "modules": [],
    "circular_dependencies": [],
    "hub_modules": [],
    "infrastructure": [],
    "inter_service": [],
    "risks": {}
  },
  "debt": {
    "score": 0,
    "grade": "A",
    "grade_capped": false,
    "interpretation": "",
    "by_category": [],
    "violations": [],
    "recommendations": []
  },
  "metadata": {
    "story_ids": [],
    "flags": {"detect_only": false}
  }
}
```

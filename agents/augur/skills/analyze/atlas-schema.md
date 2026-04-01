# atlas.json Schema (v4)

Level 3 resource for the analyze skill. Referenced from step 9 (write atlas). Defines the structural inventory output format.

Version 4 evolves from v3: typed flows replace `data_flows`, adds `bounded_contexts` to domain model, deepens `state` with schema evolution and concurrency, adds `observability`, `security`, and `developer_experience` sections, expands `module_graph` with CI/CD and IaC.

## Schema

```json
{
  "version": "4",
  "generated": "<YYYY-MM-DD>",
  "project": "<project-name>",

  "purpose": "<one short sentence, max 15 words — what the system does in plain language>",

  "domain_model": {
    "primary": "<concept-name from catalog, e.g., property-graph, ledger, catalog>",
    "description": "<one sentence — what shape the core data takes>",
    "entities": ["<core entity types in the domain>"],
    "relationships": ["<how entities connect>"],
    "bounded_contexts": [
      {
        "id": "<kebab-case>",
        "name": "<Human Label>",
        "description": "<one sentence — what this context owns>",
        "entities": ["<entity names scoped to this context>"],
        "modules": ["<path/to/module>"],
        "ubiquitous_language": {
          "<term>": "<definition as used in this context>"
        }
      }
    ]
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

  "flows": [
    {
      "id": "<kebab-case>",
      "type": "data | control | event | state | resource",
      "name": "<Human Readable Flow Name>",
      "description": "<what this flow accomplishes>",
      "trigger": "<what starts it>",
      "actors": ["<actor-id>"],
      "grounded_in": ["<file:line>"],
      "steps": [
        {
          // ── Common (all flow types) ──
          "component": "<component-id>",
          "action": "<verb phrase>",
          "to": "<component-id>",

          // ── Data flow ──
          "data": "<what moves>",
          "technology": "<protocol or transport>",
          "transform": "<what changes about the data>",

          // ── Control flow ──
          "condition": "<predicate that gates this step>",
          "branch": "<which path taken: true | false | match-value>",
          "gate": "<auth | validation | rate-limit | feature-flag>",

          // ── Event flow ──
          "topic": "<topic or channel name>",
          "delivery": "<at-most-once | at-least-once | exactly-once>",

          // ── State flow ──
          "from_state": "<state before>",
          "to_state": "<state after>",
          "side_effects": "<what else happens on transition>",

          // ── Resource flow ──
          "resource": "<what is acquired: connection | lock | file-handle | memory | thread>",
          "operation": "<acquire | use | release | timeout>",
          "constraints": "<pool-size, timeout, max-concurrent>"
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
      "grounded_in": ["<file:line>"],
      "schema_evolution": {
        "migrations": "<path to migrations directory or null>",
        "strategy": "versioned | append-only | schema-on-read | none",
        "tools": "<alembic | flyway | knex | prisma | manual | null>"
      },
      "concurrency": {
        "strategy": "optimistic | pessimistic | lock-free | single-writer | none",
        "mechanism": "<row-level locks | MVCC | CAS | advisory locks | mutex | null>",
        "conflicts": "<what happens on conflict — retry, queue, reject, last-write-wins>"
      }
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
    "ci_cd": [
      {
        "platform": "github-actions | gitlab-ci | jenkins | circleci | argo | custom",
        "file": "<path to pipeline definition>",
        "triggers": ["<push | pr | schedule | manual | tag>"],
        "stages": ["<lint | test | build | deploy | scan>"],
        "deploys_to": "<environment or null>"
      }
    ],
    "iac": [
      {
        "tool": "terraform | cloudformation | pulumi | helm | kustomize | ansible | cdk",
        "files": ["<path>"],
        "resources": ["<resource type: aws_rds_instance | k8s_deployment | etc.>"],
        "environment": "<dev | staging | production | shared>"
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

  // ── Observability ──────────────────────────────────────────────

  "observability": {
    "logging": {
      "format": "json | plain | mixed",
      "levels_used": ["<DEBUG | INFO | WARN | ERROR>"],
      "correlation_id": true,
      "libraries": ["<structlog | winston | slog | log4j>"],
      "grounded_in": ["<file:line>"]
    },
    "metrics": {
      "format": "prometheus | statsd | otlp | none",
      "endpoint": "</metrics or null>",
      "key_metrics": ["<metric name or pattern>"],
      "grounded_in": ["<file:line>"]
    },
    "tracing": {
      "enabled": true,
      "provider": "<opentelemetry | jaeger | datadog | zipkin | none>",
      "propagation": "w3c | b3 | jaeger | none",
      "grounded_in": ["<file:line>"]
    },
    "gaps": ["<what's missing — e.g., no correlation IDs, no metrics endpoint, no error tracking>"]
  },

  // ── Security ───────────────────────────────────────────────────

  "security": {
    "authentication": {
      "methods": ["<jwt | oauth | api-key | session | mtls | basic | saml>"],
      "default_deny": true,
      "identity_provider": "<auth0 | keycloak | cognito | custom | null>",
      "grounded_in": ["<file:line>"]
    },
    "authorization": {
      "model": "rbac | abac | acl | ownership | none",
      "enforcement": "<middleware | decorator | manual-check>",
      "grounded_in": ["<file:line>"]
    },
    "secrets_management": {
      "strategy": "env-vars | vault | k8s-secrets | aws-ssm | azure-keyvault | sealed-secrets | dotenv | hardcoded",
      "hardcoded_secrets": ["<file:line — empty if none found>"],
      "rotation": "<automated | manual | none>",
      "grounded_in": ["<file:line>"]
    },
    "threat_surface": [
      {
        "entry_point": "<path or endpoint>",
        "type": "api | webhook | queue | cron | websocket | grpc | public-ui",
        "authentication": "<method or 'none'>",
        "validation": "<framework-native | manual | none>",
        "rate_limited": true
      }
    ]
  },

  // ── Developer Experience ───────────────────────────────────────

  "developer_experience": {
    "testing": {
      "frameworks": ["<pytest | jest | go-test | junit | vitest>"],
      "strategy": {
        "unit": "<path pattern or 'none'>",
        "integration": "<path pattern or 'none'>",
        "e2e": "<path pattern or 'none'>"
      },
      "coverage": "<tool and threshold or 'unknown'>",
      "grounded_in": ["<file:line>"]
    },
    "linting": [
      {
        "tool": "<eslint | ruff | golangci-lint | rubocop | prettier>",
        "config": "<path to config file>",
        "pre_commit": true
      }
    ],
    "documentation": {
      "readme": true,
      "adrs": "<path or null>",
      "api_docs": "<openapi | graphql-schema | grpc-proto | null>",
      "inline_coverage": "high | medium | low | none"
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

  // ── Metadata (v4) ──────────────────────────────────────────────

  "metadata": {
    "story_ids": ["<story-id>"],
    "flags": {
      "detect_only": false
    }
  }
}
```

## What Changed from v3

| Change | v3 | v4 |
|--------|-----|-----|
| Version | `"3"` | `"4"` |
| Flows | `data_flows` (single type) | `flows` with `type` discriminator: data, control, event, state, resource |
| Flow steps | Fixed schema (data-only fields) | Common base + type-specific fields |
| Domain model | entities + relationships | + `bounded_contexts` with ubiquitous language |
| State | stores inventory only | + `schema_evolution` and `concurrency` |
| Observability | Detected as concepts only | Dedicated section: logging, metrics, tracing, gaps |
| Security | Auth field on API endpoints only | Dedicated section: authn, authz, secrets, threat surface |
| Developer experience | N/A | Testing strategy, linting, documentation |
| Module graph | modules, deps, infra, risks | + `ci_cd` pipelines, `iac` manifests |

## Conventions

- All `id` fields are kebab-case, unique within their section
- Cross-references use `id` strings, not indices
- `concept` fields use generic infrastructure terms, `technology` fields name the specific tool
- `abstraction` values come from `abstractions.md`
- Component `type: store` covers embedded data persistence. External databases appear in `external_dependencies`
- **Components should number 5-10** for most projects. >12 means not abstracting enough. <4 means over-abstracting
- **Groups must number 3-5.** This is a hard constraint. If you have more, merge related groups. If you have fewer, the project may be too small to warrant grouping.
- **Flows trace critical paths**, not every code path. 2-6 flows typical across all types
- **Failure modes should cover** every external dependency and every stateful component
- Components nest via `children`. Don't nest deeper than the code's natural structure
- `deployment` field enables the deployment viewpoint. Only add to components that map to a k8s workload
- `technology` on flow steps enables annotated sequence diagrams
- Omit `events` if the project has none
- Omit `module_graph.reverse_dependencies` if `--reverse` was not used
- Omit `api_surface` entirely if no endpoints were found and the project is not an API
- Omit empty severity lists in `api_surface.findings` and empty `debt.by_category` entries
- Omit `observability` if no logging/metrics/tracing found (rare — flag as gap in debt)
- Omit `security` if the project has no auth, no secrets, no external entry points (flag as gap)
- Omit `developer_experience` fields that don't apply (e.g., no `e2e` if none exist)
- **`grounded_in`** on flows, state, failure_modes, observability, security, and concept evidence lists the source files that justify the entry. Format: `["<file:line>"]`. These are used during evaluation to verify claims against actual code — not against other atlas entries (which would be circular)

## Flow Type Guide

Each flow type captures a different dimension of system behavior. Use the type that matches what you're tracing.

### Data flows (`type: "data"`)
What moves where. Payloads, transforms, persistence. Use `data`, `technology`, `transform` on steps.
- Request/response paths, ETL pipelines, file ingestion, API data exchange

### Control flows (`type: "control"`)
Decision points and execution order. Gates, branches, orchestration. Use `condition`, `branch`, `gate` on steps.
- Auth middleware chains, feature flag routing, request validation gates, retry/fallback logic, orchestration sequences

### Event flows (`type: "event"`)
Async message propagation. Use `topic`, `delivery` on steps. Cross-reference `events` inventory for topology.
- Pub/sub propagation, webhook delivery, signal handling, queue consumption patterns

### State flows (`type: "state"`)
Transitions and lifecycle. Use `from_state`, `to_state`, `side_effects` on steps. Cross-reference `state` inventory for stores.
- Entity lifecycle (draft→published→archived), job execution (pending→running→completed→failed), circuit breaker (closed→open→half-open)

### Resource flows (`type: "resource"`)
Acquisition, use, release of constrained resources. Use `resource`, `operation`, `constraints` on steps.
- Connection pool lifecycle, file handle management, lock acquisition patterns, thread pool saturation, memory buffer allocation

## Bounded Context Guide

Bounded contexts identify where the same term means different things or where entity definitions diverge across modules.

- **Small projects (< 3 services):** Often a single context — include it but note it's unified
- **Monoliths with modules:** Look for modules that define the same entity differently (e.g., `User` in auth vs. `User` in billing)
- **Microservices:** Each service typically owns a context; map the translation layers between them
- `ubiquitous_language` entries should only include terms that are ambiguous or domain-specific — not every variable name

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
  "version": "4",
  "generated": "YYYY-MM-DD",
  "project": "<name>",
  "purpose": "",
  "domain_model": {
    "primary": "",
    "description": "",
    "entities": [],
    "relationships": [],
    "bounded_contexts": []
  },
  "stack": {"languages": [], "frameworks": [], "runtime": ""},
  "groups": [],
  "actors": [],
  "components": [],
  "flows": [],
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
    "ci_cd": [],
    "iac": [],
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

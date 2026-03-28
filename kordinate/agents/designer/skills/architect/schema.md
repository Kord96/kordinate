# architecture.yaml Schema (v2)

Level 3 resource for the architect skill. Referenced from step 9 (write). Defines the output format.

Version 2 adds four sections to the v1 schema: `concepts`, `module_graph`, `api_surface`, and `debt`. All v1 sections are unchanged.

## Schema

```yaml
version: "2"
generated: "<YYYY-MM-DD>"
project: "<project-name>"

purpose: "<one sentence — what the system does>"

stack:
  languages: ["<Python>", "<TypeScript>"]
  frameworks:
    - name: "<framework name>"
      concepts: ["<concept-name>"]         # which concepts from the catalog this framework provides
  runtime: "<description of how it runs>"

# ── Structure ────────────────────────────────────────────────────

actors:
  - id: "<kebab-case>"
    type: user | service | cron | cli | data-source | external
    description: "<what they do with the system>"

capabilities:
  - id: "<kebab-case>"
    description: "<business-level, not technical>"
    actors: ["<actor-id>"]
    components: ["<component-id>"]

components:
  - id: "<kebab-case>"
    name: "<Human Readable Name>"
    description: "<what it does — one sentence>"
    type: service | library | worker | api | frontend | cli | scheduler | store | gateway | broker
    modules:
      - "<path/to/module>"
    depends_on: ["<component-id>"]
    abstraction: ["<abstraction-name>"]    # from abstractions.md
    patterns: ["<pattern-name>"]           # always populated from inline detection
    deployment:                             # optional, for deployment viewpoint
      namespace: "<k8s namespace>"
      kind: "<Deployment | StatefulSet | CronJob | Pod>"
      replicas: <count>
      node: "<node name or selector>"
    children:                               # optional, recursive — same schema as parent
      - id: "<kebab-case>"
        name: "<Human Readable Name>"
        description: "<one sentence>"
        type: "<same types as parent>"
        modules: ["<path>"]
        abstraction: ["<abstraction-name>"]
        depends_on: ["<component-id>"]
        children: [...]

# ── Behavior ─────────────────────────────────────────────────────

data_flows:
  - id: "<kebab-case>"
    actors: ["<actor-id>"]
    name: "<Human Readable Flow Name>"
    description: "<what this flow accomplishes>"
    trigger: "<what starts it>"
    steps:
      - component: "<component-id>"
        action: "<verb phrase>"
        data: "<what moves>"
        to: "<component-id>"              # omit for terminal step
        technology: "<protocol or transport>"

state:
  - id: "<kebab-case>"
    concept: "<generic: relational-db | document-store | embedded-olap | cache | object-store | message-broker | filesystem | in-memory>"
    technology: "<specific: PostgreSQL | DuckDB | Redis | etc.>"
    component: "<component-id>"
    stores: "<what data>"
    purpose: source-of-truth | cache | derived | staging
    persistence: persistent | ephemeral

events:
  - id: "<kebab-case>"
    type: topic | signal | webhook | cron | pubsub
    name: "<topic.name or event name>"
    producer: "<component-id>"
    consumers: ["<component-id>"]
    data: "<what the event carries>"

external_dependencies:
  - id: "<kebab-case>"
    name: "<Human Readable Name>"
    concept: "<generic: http-api | message-broker | database | cache | object-store | dns | smtp | nfs | grpc | auth-provider | cdn>"
    technology: "<specific if known>"
    components: ["<component-id>"]
    purpose: "<why needed>"
    criticality: critical | important | optional
    resilience:
      timeout: true | false
      retry: true | false
      circuit_breaker: true | false
      fallback: "<description or null>"

failure_modes:
  - id: "<kebab-case>"
    trigger: "<what goes wrong>"
    cascade:
      - component: "<component-id>"
        effect: "<what happens to this component>"
    impact: "<what end users experience>"
    detection:
      - "<first signal — metric, log, error, or 'none'>"
    recovery:
      - "<first recovery step — automatic or manual>"
    severity: critical | high | medium | low

# ── Concepts (v2) ───────────────────────────────────────────────

concepts:
  detected_patterns:
    - id: "<pattern-name>"                  # matches catalog name
      category: "<category from index>"
      confidence: high | medium | low
      components: ["<component-id>"]        # which components exhibit this pattern
      evidence:
        files: ["<path>"]
        method: grep | ast-grep | semgrep | questions | manual
        note: "<one sentence>"

  detected_anti_patterns:
    - id: "<anti-pattern-name>"
      category: "<category from index>"
      confidence: high | medium | low
      components: ["<component-id>"]
      evidence:
        files: ["<path>"]
        method: grep | ast-grep | semgrep | questions | manual
        note: "<one sentence>"

  gaps:
    - id: "<pattern-name>"
      relevance: "<why it's expected>"
      recommendation: "<what to do>"

  scan_metadata:
    catalog_size:
      patterns: <N>
      anti_patterns: <N>
    tools_used: ["grep", "ast-grep", "semgrep"]
    categories_scanned: ["<category>"]

# ── Module Graph (v2) ────────────────────────────────────────────

module_graph:
  modules:
    - id: "<module-path>"
      imports: ["<module-path>"]
      imported_by: ["<module-path>"]
      role: hub | shared | leaf | standard

  circular_dependencies:
    - cycle: ["<module>", "<module>"]

  hub_modules: ["<module-path>"]

  infrastructure:
    - resource: "<name>"
      kind: "<PVC | ConfigMap | Secret | Service | StatefulSet | aws_rds_instance | ...>"
      source: "<namespace or Terraform module>"
      notes: "<detail>"

  inter_service:
    - service: "<name>"
      discovered_in: "<file>"
      pattern: "<*_URL | depends_on | connection string>"
      value: "<the reference>"

  reverse_dependencies:                     # only if --reverse was used
    - project: "<sibling project name>"
      reference_type: import | config | k8s-manifest
      files: ["<path>"]

  risks:
    hardcoded_endpoints: ["<file:line>"]
    missing_resilience:
      - file: "<path>"
        service_type: "<type>"
        missing: ["timeout", "retry", "circuit_breaker"]
    unversioned_deps: ["<description>"]

# ── API Surface (v2) ─────────────────────────────────────────────

api_surface:
  style: REST | GraphQL | gRPC | WebSocket | SSE | mixed
  frameworks:
    - name: "<framework>"
      version: "<version if known>"

  endpoints:
    - method: "<GET | POST | PUT | DELETE | PATCH>"
      path: "</route>"
      handler: "<function name>"
      file: "<path:line>"
      auth: yes | no | gateway | inherited
      validation: yes | no | partial

  findings:
    critical:
      - description: "<finding>"
        files: ["<path:line>"]
        count: <N>
    recommended:
      - description: "<finding>"
        files: ["<path:line>"]
        count: <N>
    minor:
      - description: "<finding>"
        files: ["<path:line>"]
        count: <N>

  compliance:
    gateway:
      status: compliant | partial | non-compliant
      notes: "<explanation>"
    hexagonal:
      status: compliant | partial | non-compliant
      notes: "<explanation>"
    external_gateway: "<Kong | AWS API Gateway | ... | null>"

# ── Debt (v2) ────────────────────────────────────────────────────

debt:
  score: <N>
  grade: A | B | C | D | F
  grade_capped: true | false                # true if hard floor rule applied
  interpretation: "<one sentence>"

  by_category:
    - category: Structural | Data | Integration | Resilience | Lifecycle
      points: <N>
      violations: <N>

  violations:
    - severity: CRITICAL | RECOMMENDED | MINOR
      category: "<category>"
      pattern: "<source pattern>"
      anti_pattern: "<what was violated>"
      components: ["<component-id>"]
      files: ["<path>"]
      detail: "<one sentence>"
      points: <N>

  recommendations:
    - priority: <1-7>
      title: "<short title>"
      severity: CRITICAL | RECOMMENDED | MINOR
      category: "<category>"
      files: ["<path>"]
      description: "<what to fix and why>"
      fixes: ["<anti-pattern-id>"]
```

## Conventions

- All `id` fields are kebab-case, unique within their section
- Cross-references use `id` strings, not indices
- `concept` fields use generic infrastructure terms, `technology` fields name the specific tool
- `abstraction` values come from `abstractions.md`
- Component `type: store` covers embedded data persistence. External databases appear in `external_dependencies`
- Components should number 5-10 for most projects. >12 means not abstracting enough. <4 means over-abstracting
- Data flows trace critical paths, not every code path. 2-4 flows typical
- Failure modes should cover every external dependency and stateful component
- Components nest via `children`. Don't nest deeper than the code's natural structure
- `deployment` field enables the deployment viewpoint. Only add to components that map to a k8s workload
- `technology` on flow steps enables annotated sequence diagrams
- Omit `events` if the project has none. Omit `module_graph.reverse_dependencies` if `--reverse` was not used
- Omit `api_surface` entirely if no endpoints were found and the project is not an API
- Omit empty severity lists in `api_surface.findings` and empty `debt.by_category` entries

## Minimal Skeleton

```yaml
version: "2"
generated: "YYYY-MM-DD"
project: "<name>"
purpose: "<one sentence>"
stack:
  languages: []
  frameworks: []
  runtime: ""
actors: []
capabilities: []
components: []
data_flows: []
state: []
external_dependencies: []
failure_modes: []
concepts:
  detected_patterns: []
  detected_anti_patterns: []
  gaps: []
  scan_metadata:
    catalog_size: { patterns: 0, anti_patterns: 0 }
    tools_used: []
    categories_scanned: []
module_graph:
  modules: []
  circular_dependencies: []
  hub_modules: []
  infrastructure: []
  inter_service: []
  risks: {}
debt:
  score: 0
  grade: A
  grade_capped: false
  interpretation: ""
  by_category: []
  violations: []
  recommendations: []
```

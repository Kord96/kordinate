# Augur Analyze Bundle — Holistic v1

## Shared analyze workflow

1. Resolve mode and scope (full, incremental, or skip).
2. Start from the prepared deterministic artifacts for this run: `$RUN/blast.json` and `$RUN/facts/`.
3. Use deterministic evidence, including `facts/concept-evidence.json`, to decide what deserves attention.
4. Interpret that evidence semantically.
5. Widen into source files only where the prepared artifacts leave ambiguity or show a larger boundary.
6. Build the architectural model, derive failure modes/debt, and write atlas/stories.

Deterministic detector evidence establishes what is likely present in the codebase. Semantic memory is used to interpret and evaluate that evidence, not to replace it.

This bundle includes the full semantic catalog in memory. Still begin with the prepared run artifacts so the analysis is grounded and focused.

## Workflow

---
description: Augur workflow — analyze existing code or design new projects, producing facts and atlas as structured outputs
---
# Workflow

## Skills

| Skill | Purpose |
|-------|---------|
| `/analyze` | Analyze existing codebases — pattern detection, debt assessment, failure modes |
| `/design` | Design new projects (4 modes: full, api, service, component) |

## Structured Outputs

### Facts

Facts are the normalized result of deterministic extraction. They are concrete observations like routes, models, external clients, import edges, jobs, and concept-evidence. Facts are consumed by semantic atlas work and may also be consumed directly for targeted tasks like blast radius or focused summaries.

See `schemas/facts-schema.md` for the full schema.

### Atlas

The atlas is the primary output consumed by all agents (charon, sauron, alfred). It contains:
- Components and their connections
- Failure modes with structured detection metadata (signals, concerns, source patterns)
- Infrastructure requirements (vitals config, dashboard stubs, resource defaults)
- Dependency map

See `agents/augur/schemas/atlas-schema.md` for the full atlas schema.

## Knowledge Base

- **Concept catalog semantics** at `memory/catalog/concepts/` — `<concept>.md` is canonical for concept meaning and architectural implications
- **Framework catalog semantics** at `memory/catalog/frameworks/` — framework primitives, conventions, and common co-occurring concepts
- **Ontology/index layer** at `memory/indexes/` — abstractions, concept index, anti-pattern index
- **Detector source assets** at `detectors/` — deterministic fact-production rules and policies
- **Generated bundles** at `.generated/bundles/` — derived prompt/runtime assets, not canonical source
- **Infra-atlas** at `/kord/agents/charon/memory/global/infra-atlas.json` — cluster topology, observability endpoints, workload contract
- **App contract** at `memory/contracts/app-contract.md` — requirements every deployed app must satisfy

## Analyze Workflow

1. Gather source code and identify languages and frameworks
2. Use deterministic detector assets to establish stack context and produce normalized facts
3. Treat `facts/index.json` as the manifest for deterministic evidence
4. Use deterministic facts, including `facts/concept-evidence.json`, to guide semantic atlas work
5. Use `agents/augur/schemas/atlas-schema.md`, `agents/augur/schemas/story-schema.md`, and `agents/augur/schemas/narratives-schema.md` as the canonical semantic output contracts

## Design Workflow

1. Read requirements and constraints
2. Select frameworks and patterns from the semantic catalogs
3. Compose architecture with component topology
4. Produce atlas with full detection metadata and infrastructure stubs

## Contracts

---
description: App Contract — requirements every deployed application must satisfy
---
# App Contract

Every deployed application must satisfy these requirements. For allowed app label values, see `profile/topology.yaml`. For full infrastructure details, see `infra-atlas.json` (`new_workload_contract` section).

## Labels

Required pod label:
- `app` -- project name that owns this workload

Optional pod labels:
- `component` -- individual service name (e.g., `classifier`, `kafka`)
- `tier` -- operational role (e.g., `ingest`, `process`, `store`)

The `pod` label is auto-injected by Alloy from Kubernetes metadata.

## Annotations

Required for pods exposing `/metrics`:
- `prometheus.io/scrape: "true"`
- `prometheus.io/port: "<port>"`

## Observability Contract

### Metrics

Expose `/metrics` in Prometheus format. Alloy discovers via pod annotations and scrapes automatically.

### Logging

Structured JSON to stdout. Required fields:

| Field | Purpose |
|-------|---------|
| `level` | debug, info, warn, error |
| `component` | which service/module emitted the log |
| `event` | what happened |
| `timestamp` | when it happened |

Alloy tails pod stdout and writes to Loki. Additional fields become Loki labels automatically.

### Health

`GET /health` serves as both readiness and liveness probe. Returns 200 when the process is alive and ready to serve. Startup grace period: 30s.

### Vitals

Standalone deployment (one per app, not a sidecar) that evaluates app health by querying Prometheus. Vitals produces tri-state health gauges (`0=FAIL, 1=WARNING, 2=OK`) on port 9131.

Required evaluations:
- **process** -- is the process alive and responsive?
- **deps** -- are dependencies (databases, queues, APIs) reachable?

Extend with additional sections as needed (e.g., `vitals_ingestion`, `vitals_storage`, `vitals_serving`).

**VitalsMissing meta-alert required**: every app must have an alert rule that fires when vitals metrics disappear:
```yaml
- alert: VitalsMissing
  expr: absent(vitals_process{app="<name>"})
  for: 5m
```

### Detection

Atlas `failure_modes` entries carry structured detection metadata:
- `signals` -- observable symptoms (metric behavior, log patterns, error types)
- `concern` -- abstract category (dependency-availability, data-integrity, throughput, latency, resource-exhaustion, state-consistency)
- `source_pattern` -- concept catalog entry the detection derives from

Sauron reads these from the atlas and maps them to vitals evaluations and alert rules. The detection structure is portable -- augur defines what to watch, sauron implements how.

## Ownership Model

| Agent | Role |
|-------|------|
| **Augur** | Defines the contract (this file) and produces atlas with failure_modes/detection |
| **Charon** | Enforces on deployment (`/wrap` skill validates contract compliance) |
| **Sauron** | Implements monitoring (reads atlas, configures vitals + dashboards) |
| **Alfred** | Manages secrets and overlays (never hardcoded in manifests) |

## Dev Deployment Model

- **git-sync sidecar** pulls main every 3s
- **File watcher** for hot reload (nodemon/uvicorn depending on runtime)
- **Image rebuilds only on dependency changes** (package.json, requirements.txt, etc.)
- **Webhook receiver** gates the deployment pipeline

## Enforcement

Charon's `/wrap` skill validates the contract on deployment:
- `app` label must be present with an allowed value from `profile/topology.yaml`
- `/metrics` endpoint must return valid Prometheus format
- Log output must be structured JSON with required fields
- Health endpoint must respond at `GET /health`

Apps that do not satisfy the contract are rejected.

## Ontology and indexes

---
description: Index of abstraction levels used to classify concepts — each answers a distinct architectural question
---

# Abstractions

Every concept in the catalog belongs to one or more abstractions. Abstractions describe the lens through which a concept is useful.

| Abstraction | Description | Examples |
|------------|-------------|---------|
| **architectural** | System-level structure — how services, modules, and layers are organized and separated | hexagonal, microservices, CQRS, event-sourcing, modular-monolith |
| **design** | Code-level structure — how classes, functions, and objects are composed within a component | factory, observer, decorator, strategy, composite |
| **data** | Data movement and persistence — how data is ingested, transformed, cached, queried, and stored | stream-to-store, ETL, cache-aside, materialized-view, sharding |
| **integration** | Cross-boundary communication — how independent components or services coordinate | saga, webhook, API gateway, anti-corruption-layer, strangler-fig |
| **messaging** | Message delivery mechanics — how messages are produced, routed, consumed, and acknowledged | pub-sub, message-queue, outbox, dead-letter, competing-consumers |
| **infrastructure** | Runtime resources — physical or virtual things that exist and need provisioning | connection-pooling, service-mesh, LRU cache, service-discovery |
| **resilience** | Failure tolerance — how the system detects, contains, and recovers from failures | circuit-breaker, bulkhead, retry, graceful-degradation, timeout |
| **concurrency** | Parallel execution — how concurrent work is coordinated without corruption or starvation | actor-model, worker-pool, read-write-lock, future-promise |
| **security** | Access and trust — how identity, authorization, and data protection are enforced | oauth-oidc, rbac, mtls, rate-limiting, tenant-isolation |
| **api** | Interface contracts — how services expose operations and data to consumers | REST, GraphQL, gRPC, BFF, content-negotiation |
| **lifecycle** | Runtime behavior — how a process starts, runs, shuts down, and transitions between states | service-manager, health-check, scheduler, strangler-fig |
| **deployment** | Release mechanics — how software moves from build to production safely and reversibly | blue-green, canary, gitops, immutable-infra, feature-flag |
| **observability** | System visibility — how operators see what the system is doing and detect anomalies | structured-logging, distributed-tracing, metrics-instrumentation |
| **testing** | Verification strategy — how correctness is validated at different boundaries | contract-testing, property-testing, test-doubles, fixture-builder |
| **frontend** | UI composition — how user interfaces are structured, rendered, and state-managed | MVC, MVVM, flux, component, micro-frontend |
| **error-handling** | Failure representation — how errors are modeled, propagated, and handled in code | result-type, monad, null-object |
| **realtime** | Time-sensitive execution — how simulations and real-time systems manage deterministic updates | game-loop, ECS, tick-simulation, spatial-partitioning |
| **ml** | Model lifecycle — how models are trained, versioned, experimented with, and served | feature-store, model-registry, training-pipeline, experiment-framework |
| **compiler** | Language tooling — how source code is parsed, represented, and transformed | lexer-parser, AST, intermediate-representation |

---
description: Index of recognized anti-patterns by category
---
# Anti-Patterns Index

22 anti-patterns across 6 categories. Each has recognition signatures and remediation steps.

## Categories

| Category | Key Question |
|----------|-------------|
| code-structure | Is the codebase organized and maintainable? |
| dependencies | Are dependencies clean and acyclic? |
| data | Is data accessed and modeled correctly? |
| concurrency | Is concurrent code safe and readable? |
| api | Are interfaces well-designed and efficient? |
| operations | Are errors handled and config managed cleanly? |

## Anti-Patterns

### Code Structure

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| God object | Classes with 1000+ lines touching many unrelated concerns | [view](concepts/god-object.md) |
| Spaghetti code | Deeply nested conditionals, 500+ line functions, untraceable flow | [view](concepts/spaghetti-code.md) |
| Lava flow | Dead code, commented-out blocks, unreachable branches | [view](concepts/lava-flow.md) |
| Golden hammer | One tool/framework forced onto every problem | [view](concepts/golden-hammer.md) |
| Cargo cult | Patterns applied without understanding (factory for one type, etc.) | [view](concepts/cargo-cult.md) |
| Big ball of mud | No directory structure, any file imports any other | [view](concepts/big-ball-of-mud.md) |

### Dependencies

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Circular dependency | A imports B imports A (direct or transitive) | [view](concepts/circular-dependency.md) |
| Tight coupling | Concrete class references everywhere, no interfaces | [view](concepts/tight-coupling.md) |
| Leaky abstraction | Implementation details in interface signatures | [view](concepts/leaky-abstraction.md) |

### Data

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| N+1 queries | Database query inside a loop, ORM lazy loading in iteration | [view](concepts/n-plus-one.md) |
| Premature optimization | Caching/denormalizing before measuring, complex structures for small data | [view](concepts/premature-optimization.md) |
| Stringly typed | Strings where enums/types should be, string comparison for branching | [view](concepts/stringly-typed.md) |
| Magic numbers | Hardcoded values with no explanation | [view](concepts/magic-numbers.md) |

### Concurrency

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Race condition | Unsynchronized read-modify-write on shared state | [view](concepts/race-condition.md) |
| Deadlock | Multiple locks acquired in inconsistent order | [view](concepts/deadlock.md) |
| Callback hell | Deeply nested callbacks, pyramid-shaped code | [view](concepts/callback-hell.md) |

### API / Interface

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Chatty API | 10+ sequential calls to assemble one view, no batch endpoints | [view](concepts/chatty-api.md) |
| Anemic domain model | Model classes with only getters/setters, all logic in services | [view](concepts/anemic-domain-model.md) |
| God endpoint | Single route handling multiple operations via action parameter | [view](concepts/god-endpoint.md) |

### Operations

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Log and throw | Same exception logged at multiple layers | [view](concepts/log-and-throw.md) |
| Swallowed exception | Empty catch/except blocks, errors silently ignored | [view](concepts/swallowed-exception.md) |
| Config sprawl | Config in env vars AND yaml AND code AND database, no single source of truth | [view](concepts/config-sprawl.md) |

---
description: Index of recognized architectural patterns by category
---
# Patterns Index

170 patterns across 21 categories. Each pattern has recognition signatures for code scanning.

## Categories

| Category | Description |
|----------|-------------|
| architecture | Overall system structure |
| structural | How code is organized within a service |
| data | How data flows and is stored |
| integration | How services communicate with each other |
| resilience | How the system handles failure |
| lifecycle | How a single service starts, runs, and stops |
| creational | How objects are created |
| behavioral | How objects communicate |
| concurrency | How parallel work is managed |
| frontend | How user interfaces are structured |
| storage | How data is persisted and accessed |
| messaging | How messages flow between components |
| deployment | How software is released |
| security | How access and trust are managed |
| api | How services expose interfaces |
| distributed | How distributed systems coordinate |
| testing | How code is verified |
| error-handling | How failures are represented |
| infrastructure | How environments are provisioned |
| domain-model | Core data shape of the system |
| networking | How network communication is handled |
| observability | How systems are monitored |
| realtime | How real-time systems are structured |
| ml | How ML systems are built |
| compiler | How language tooling is structured |

## Patterns

### Architecture

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Microservices | Multiple independently deployable services | [view](concepts/microservices.md) |
| Modular monolith | Single deployment with internal module boundaries | [view](concepts/modular-monolith.md) |
| Serverless / FaaS | Stateless request handlers triggered by events | [view](concepts/serverless.md) |

### Structural

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Hexagonal (ports & adapters) | Decouples business logic from infrastructure via ports and adapters | [view](concepts/hexagonal.md) |
| Domain-driven design (DDD) | Organizes code around bounded contexts and domain aggregates | [view](concepts/ddd.md) |
| Plugin architecture | Extensible core with pluggable components registered at startup | [view](concepts/plugin.md) |
| Aggregate root | Root entity controlling access to child entities within a consistency boundary | [view](concepts/aggregate.md) |
| Value object | Immutable objects compared by value, not identity | [view](concepts/value-object.md) |
| Anti-corruption layer | Boundary translation between systems or bounded contexts | [view](concepts/anti-corruption-layer.md) |
| Decorator / Wrapper | Adding behavior to an object without modifying its interface | [view](concepts/decorator.md) |
| Proxy | Controls access to an object through the same interface | [view](concepts/proxy.md) |
| Adapter | Translates one interface to another | [view](concepts/adapter.md) |
| Facade | Simplified interface to a complex subsystem | [view](concepts/facade.md) |
| Pipeline / Filter | Ordered chain of transform functions processing data through stages | [view](concepts/pipeline-filter.md) |
| Composite | Tree structures where leaves and containers share the same interface | [view](concepts/composite.md) |
| Flyweight | Shared immutable objects to reduce memory | [view](concepts/flyweight.md) |
| Bridge | Separating abstraction from implementation so both can vary | [view](concepts/bridge.md) |

### Data

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Stream-to-store | Kafka consumer that writes to a local store via buffered flushes | [view](concepts/stream-to-store.md) |
| ETL/ELT | Batch extract-transform-load for periodic data processing | [view](concepts/etl.md) |
| Event sourcing | Append-only event log as the source of truth | [view](concepts/event-sourcing.md) |
| CQRS | Separate models for reading and writing data | [view](concepts/cqrs.md) |
| MapReduce | Parallel map phase + reduce/aggregate phase over distributed data | [view](concepts/mapreduce.md) |
| Idempotent consumer | Message deduplication before processing | [view](concepts/idempotent-consumer.md) |
| Change data capture | Database log tailing to capture changes as events | [view](concepts/change-data-capture.md) |
| Ring buffer | Fixed-size circular buffer with wrap-around | [view](concepts/ring-buffer.md) |
| Bloom filter | Probabilistic membership test with bit array | [view](concepts/bloom-filter.md) |
| Trie | Prefix tree for autocomplete and routing | [view](concepts/trie.md) |

### Integration

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Saga | Distributed transactions via local transactions with compensating actions | [view](concepts/saga.md) |
| Choreography | Services react to events independently with no central coordinator | [view](concepts/choreography.md) |
| API gateway | Centralized entry point for routing, auth, and rate limiting | [view](concepts/api-gateway.md) |
| Webhook | Callback URL registration with event delivery | [view](concepts/webhook.md) |
| Claim check | Large payload stored externally, message contains reference | [view](concepts/claim-check.md) |

### Resilience

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Circuit breaker | Stops calling a failing dependency after a threshold, allows recovery | [view](concepts/circuit-breaker.md) |
| Bulkhead | Isolates components so one failure doesn't exhaust shared resources | [view](concepts/bulkhead.md) |
| Retry with backoff | Retries failed operations with exponential delay and jitter | [view](concepts/retry.md) |
| Backpressure | Flow control when a producer is faster than its consumer | [view](concepts/backpressure.md) |
| Timeout | Explicit timeout on every external call | [view](concepts/timeout.md) |
| Graceful degradation | Fallback responses when dependencies are down | [view](concepts/graceful-degradation.md) |

### Lifecycle

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Service manager | Manages service startup, shutdown, health reporting, and graceful degradation | [view](concepts/service-manager.md) |
| Sidecar | Auxiliary container handling cross-cutting concerns alongside the main workload | [view](concepts/sidecar.md) |
| Scheduler / Cron | Time-based triggers for periodic task execution | [view](concepts/scheduler.md) |
| Workflow engine | DAG-based step/task orchestration with dependencies | [view](concepts/workflow-engine.md) |
| Strangler fig | Incremental replacement of legacy system | [view](concepts/strangler-fig.md) |
| Database migration | Versioned schema changes with up/down rollback | [view](concepts/database-migration.md) |

### Creational

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Factory | Object creation via factory methods/classes returning interfaces | [view](concepts/factory.md) |
| Abstract factory | Family of related objects created through a factory interface | [view](concepts/abstract-factory.md) |
| Builder | Step-by-step object construction with fluent method chaining | [view](concepts/builder.md) |
| Singleton | Single instance shared across the application | [view](concepts/singleton.md) |
| Object pool | Reusable object pool with acquire/release lifecycle | [view](concepts/object-pool.md) |
| Dependency injection | Inversion of control via constructor/setter injection | [view](concepts/dependency-injection.md) |
| Prototype | Creating objects by cloning existing instances | [view](concepts/prototype.md) |

### Behavioral

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Strategy | Interchangeable algorithms behind a common interface | [view](concepts/strategy.md) |
| Observer | Event emitter with subscribe/notify for decoupled communication | [view](concepts/observer.md) |
| Command | Encapsulated operations as objects with execute/undo | [view](concepts/command.md) |
| State machine | Explicit states with defined transitions and lifecycle hooks | [view](concepts/state-machine.md) |
| Chain of responsibility | Ordered handler chain where each can process or pass the request | [view](concepts/chain-of-responsibility.md) |
| Mediator | Central coordinator for component communication | [view](concepts/mediator.md) |
| Template method | Abstract base with overridable hook methods | [view](concepts/template-method.md) |
| Visitor | Double-dispatch traversal with accept/visit methods | [view](concepts/visitor.md) |
| Iterator | Lazy sequential access to elements without exposing internals | [view](concepts/iterator.md) |
| Specification | Composable boolean predicates for business rules | [view](concepts/specification.md) |
| Monad / Railway | Chained operations that short-circuit on failure via bind/flatMap | [view](concepts/monad.md) |
| Memento | Capturing and restoring object state (undo/redo) | [view](concepts/memento.md) |

### Concurrency

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Actor model | Isolated actors communicating via asynchronous message passing | [view](concepts/actor-model.md) |
| Producer-consumer | Shared queue/buffer between producing and consuming threads | [view](concepts/producer-consumer.md) |
| Worker pool | Fixed pool of workers processing tasks from a queue | [view](concepts/worker-pool.md) |
| Reactor / Event loop | Single-threaded event loop with non-blocking I/O | [view](concepts/reactor.md) |
| Read-write lock | Separate locks for concurrent reads and exclusive writes | [view](concepts/read-write-lock.md) |
| Future / Promise | Deferred computation with async result containers | [view](concepts/future-promise.md) |

### Frontend

| Pattern | Description | Reference |
|---------|-------------|-----------|
| MVC | Model-View-Controller separation of concerns | [view](concepts/mvc.md) |
| MVVM | Model-View-ViewModel with observable data binding | [view](concepts/mvvm.md) |
| Component | Self-contained UI components with props/state composition | [view](concepts/component.md) |
| Flux / Redux | Unidirectional data flow with store, actions, and reducers | [view](concepts/flux.md) |
| Micro-frontend | Independently deployable frontend modules | [view](concepts/micro-frontend.md) |

### Storage

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Repository | Abstraction over data access with CRUD operations | [view](concepts/repository.md) |
| Unit of work | Transaction management wrapping multiple operations | [view](concepts/unit-of-work.md) |
| Active record | Model instances with built-in persistence methods | [view](concepts/active-record.md) |
| Data mapper | Separate mapper transferring data between objects and database | [view](concepts/data-mapper.md) |
| Cache-aside | Check cache first, load from source on miss | [view](concepts/cache-aside.md) |
| Read-through | Cache that loads from source on miss automatically | [view](concepts/read-through.md) |
| Refresh-ahead | Proactive cache refresh before TTL expiry | [view](concepts/refresh-ahead.md) |
| Write-behind | Writes go to cache first, async flush to backing store | [view](concepts/write-behind.md) |
| Cache stampede prevention | Lock-based or probabilistic cache population to prevent thundering herd | [view](concepts/cache-stampede-prevention.md) |
| LRU cache | Bounded cache with least-recently-used eviction | [view](concepts/lru-cache.md) |
| Sharding | Data partitioned across nodes by shard key | [view](concepts/sharding.md) |
| Optimistic locking | Version field for conflict detection on write | [view](concepts/optimistic-locking.md) |
| Soft delete | Logical deletion with timestamp/flag instead of physical removal | [view](concepts/soft-delete.md) |
| Materialized view | Pre-computed query results stored as table/cache | [view](concepts/materialized-view.md) |
| Batch loader | N+1 prevention via batched queries | [view](concepts/batch-loader.md) |
| Pagination | Cursor or offset-based result windowing | [view](concepts/pagination.md) |

### Messaging

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Publish-subscribe | Topic-based fan-out messaging to multiple subscribers | [view](concepts/pub-sub.md) |
| Message queue | Point-to-point messaging with each message consumed once | [view](concepts/message-queue.md) |
| Dead letter queue | Failed message routing with retry tracking | [view](concepts/dead-letter.md) |
| Competing consumers | Multiple consumers on the same queue for load balancing | [view](concepts/competing-consumers.md) |
| Request-reply | RPC over message broker with correlation IDs | [view](concepts/request-reply.md) |
| Event-driven architecture | Domain events as first-class objects flowing through an event bus | [view](concepts/event-driven.md) |
| Outbox | Events written to DB in same transaction, published by separate process | [view](concepts/outbox.md) |
| Event notification | Thin events containing only ID + type, consumer calls back for data | [view](concepts/event-notification.md) |
| Event-carried state | Fat events containing full entity state for replication | [view](concepts/event-carried-state.md) |

### Deployment

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Blue-green | Two identical environments with traffic switching | [view](concepts/blue-green.md) |
| Canary | Gradual traffic splitting between stable and new versions | [view](concepts/canary.md) |
| Feature flag | Runtime feature toggles for conditional functionality | [view](concepts/feature-flag.md) |
| GitOps | Git repo as source of truth with reconciliation loops | [view](concepts/gitops.md) |
| Immutable infrastructure | Replace-not-patch, image-based deployment | [view](concepts/immutable-infra.md) |

### Security

| Pattern | Description | Reference |
|---------|-------------|-----------|
| OAuth2 / OIDC | Authorization code flow with token-based access | [view](concepts/oauth-oidc.md) |
| RBAC | Role-based access control with role-permission mapping | [view](concepts/rbac.md) |
| Rate limiting | Request throttling with token bucket or sliding window | [view](concepts/rate-limiting.md) |
| Secret management | Vault/KMS-based credential storage, never hardcoded | [view](concepts/secret-management.md) |
| Session auth | Session-based authentication with server-side session store | [view](concepts/session-auth.md) |
| Token auth (JWT) | Stateless token-based authentication with Bearer tokens | [view](concepts/token-auth.md) |
| Mutual TLS | Client certificate authentication for service-to-service | [view](concepts/mtls.md) |
| API key auth | API key validation for programmatic access | [view](concepts/api-key-auth.md) |
| Audit logging | Immutable log of who-did-what-when for compliance | [view](concepts/audit-logging.md) |
| Input validation | Schema validation and sanitization at API boundary | [view](concepts/input-validation.md) |
| CORS | Cross-origin resource sharing configuration | [view](concepts/cors.md) |
| Tenant isolation | Tenant-scoped data access (DB/schema/row-level) | [view](concepts/tenant-isolation.md) |
| Tenant routing | Tenant-aware request routing and connection switching | [view](concepts/tenant-routing.md) |

### API

| Pattern | Description | Reference |
|---------|-------------|-----------|
| REST | Resource-based HTTP API with standard methods and status codes | [view](concepts/rest.md) |
| GraphQL | Schema-driven query language with single endpoint | [view](concepts/graphql.md) |
| gRPC | Protocol buffer-based RPC with generated stubs | [view](concepts/grpc.md) |
| BFF | Backend for Frontend — API layer tailored per client type | [view](concepts/bff.md) |
| Content negotiation | Format selection via Accept/Content-Type headers | [view](concepts/content-negotiation.md) |

### Distributed

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Service mesh | Sidecar proxy layer for service-to-service communication | [view](concepts/service-mesh.md) |
| Leader election | Single leader coordination with lease-based failover | [view](concepts/leader-election.md) |
| Distributed lock | Cross-node mutual exclusion with TTL | [view](concepts/distributed-lock.md) |
| Health check | Liveness/readiness probes with dependency health aggregation | [view](concepts/health-check.md) |
| Correlation ID | Request ID propagation for distributed tracing | [view](concepts/correlation-id.md) |
| Service discovery | Registry-based or DNS-based service endpoint resolution | [view](concepts/service-discovery.md) |

### Testing

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Test doubles | Mock, stub, fake, and spy implementations for isolation | [view](concepts/test-doubles.md) |
| Contract testing | Consumer-driven contracts verified against providers | [view](concepts/contract-testing.md) |
| Property testing | Generator-based input with invariant assertions | [view](concepts/property-testing.md) |
| Fixture builder | Test data factories and builder helpers | [view](concepts/fixture-builder.md) |
| Snapshot testing | Output comparison against stored snapshots | [view](concepts/snapshot-testing.md) |

### Error Handling

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Result / Either type | Errors as values, not exceptions — with map/bind composition | [view](concepts/result-type.md) |
| Null object | No-op implementations replacing null checks | [view](concepts/null-object.md) |

### Infrastructure

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Configuration management | 12-factor config with env vars and hierarchical overrides | [view](concepts/config-management.md) |
| Infrastructure as Code | Declarative infra definitions (Terraform, Pulumi, CloudFormation) | [view](concepts/infrastructure-as-code.md) |
| Connection pooling | Reusable connection pools for databases and HTTP | [view](concepts/connection-pooling.md) |

### Networking

| Pattern | Description | Reference |
|---------|-------------|-----------|
| WebSocket | Persistent bidirectional connection | [view](concepts/websocket.md) |
| Server-sent events | One-way server push via HTTP streaming | [view](concepts/server-sent-events.md) |
| Long polling | Client holds request until server has data | [view](concepts/long-polling.md) |

### Observability

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Structured logging | JSON log output with key-value fields | [view](concepts/structured-logging.md) |
| Metrics instrumentation | Prometheus client usage for counters, gauges, histograms | [view](concepts/metrics-instrumentation.md) |
| Distributed tracing | OpenTelemetry SDK with span context propagation | [view](concepts/distributed-tracing.md) |

### Realtime

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Entity-component-system | Entities as IDs, components as data, systems operating on queries | [view](concepts/entity-component-system.md) |
| Game loop | Fixed timestep update loop with input/update/render phases | [view](concepts/game-loop.md) |
| Spatial partitioning | Quadtree, octree, or spatial hash for neighbor queries | [view](concepts/spatial-partitioning.md) |
| Tick simulation | Discrete time steps with deterministic updates | [view](concepts/tick-simulation.md) |

### ML

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Feature store | Centralized feature repository with online/offline serving | [view](concepts/feature-store.md) |
| Model registry | Versioned model storage with stage transitions | [view](concepts/model-registry.md) |
| Training pipeline | Data-to-model stages with experiment tracking | [view](concepts/training-pipeline.md) |
| Experiment framework | A/B testing with variant bucketing and metric collection | [view](concepts/experiment-framework.md) |

### Compiler

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Lexer / Parser | Tokenization + parsing into structured representation | [view](concepts/lexer-parser.md) |
| Abstract syntax tree | Tree node hierarchy representing language constructs | [view](concepts/ast.md) |
| Intermediate representation | Lowered representation for optimization passes | [view](concepts/intermediate-representation.md) |

## Libraries

Patterns with kordinate library implementations: stream-to-store (stoik), service-manager (orchestrator).
Implementation files are co-located in the pattern directory.

## Domain Model

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Ledger | Double-entry ledger — debits, credits, balanced transactions | [view](concepts/ledger.md) |
| Property graph | Typed nodes and edges with properties and traversal queries | [view](concepts/property-graph.md) |
| Search index | Inverted index, analyzers, ranked full-text retrieval | [view](concepts/search-index.md) |
| Time-series | Timestamp-indexed append-only data with retention and downsampling | [view](concepts/time-series.md) |
| Versioned document | Immutable revisions, diffs, conflict resolution | [view](concepts/versioned-document.md) |
| Tensor | Multi-dimensional array computation with GPU dispatch | [view](concepts/tensor.md) |
| Spatial | Geographic/geometric data with spatial indexes | [view](concepts/spatial.md) |
| Rule engine | Declarative business rules, policy evaluation, decision tables | [view](concepts/rule-engine.md) |
| Multi-tenant | Tenant-scoped data isolation and configuration | [view](concepts/multi-tenant.md) |
| Subscription | Recurring billing, plan management, usage metering | [view](concepts/subscription.md) |
| Block content | Structured rich text with nested typed blocks | [view](concepts/block-content.md) |
| Catalog | Product/variant/SKU hierarchy with inventory | [view](concepts/catalog.md) |
| Social graph | Follow/connection relationships with feed generation | [view](concepts/social-graph.md) |
| Conversation thread | Threaded messaging with real-time delivery | [view](concepts/conversation-thread.md) |
| Graph | Generic graph model — DAGs, traversal, cycle detection | [view](concepts/graph.md) |

## Framework semantics

# FastAPI

FastAPI is an async Python web API framework centered on typed request/response models, declarative routing, and dependency injection.

## Recognition
Common signals:
- `from fastapi import FastAPI`
- `app = FastAPI()`
- `APIRouter()`
- route decorators like `@app.get`, `@router.post`
- Pydantic models for request/response validation

## Architectural implications
- API boundary validation is often framework-native
- request lifecycle is explicit and async-aware
- dependency injection is commonly used for repositories, services, auth, and DB sessions
- route handlers may stay thin, or may accumulate business logic if architecture is weak

## Common co-occurring concepts
- REST
- Input validation
- Dependency injection
- Repository
- Layered architecture
- Hexagonal

## Common failure modes
- business logic in route handlers
- leaking ORM/session objects through the API layer
- implicit dependency wiring that hides boundaries
- mixed sync/async I/O causing latency or deadlocks

## Concept semantics

---
description: Abstract Factory architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Abstract Factory

## Recognition

How to identify this pattern in code.

### Signatures

- Family of related objects created through a factory interface
- `*Factory` interfaces with multiple `create*()` methods producing related types
- Theme factories (light theme factory, dark theme factory producing consistent widget sets)
- Platform-specific widget factories (Windows, macOS, Linux UI component creation)
- Factory selection based on configuration or runtime environment
- Concrete factories implementing a shared factory interface with consistent product families

### Confidence

- **high** -- Factory interface with multiple `create*()` methods, concrete factory implementations producing families of related objects, factory selected at configuration time
- **medium** -- Factory class producing multiple related objects but without a formal factory interface hierarchy
- **low** -- Single `create()` factory method that returns one type (closer to factory method than abstract factory)

## Architecture

Look for a factory interface that produces families of related objects, with concrete factories swapped to change the entire product family.

### Review Checklist

- All products within a family are consistent and compatible with each other
- New product families can be added by implementing the factory interface without modifying existing code
- Factory selection is centralized (configuration, environment, or dependency injection)
- Products created by the factory are used through their abstract interfaces, not concrete types
- Adding a new product type to the family requires updating all concrete factories (understand the cost)
- Factory does not accumulate unrelated creation methods (stays focused on one product family)

### Anti-patterns

- Factory producing unrelated objects that do not form a coherent family
- Client code depending on concrete product types instead of abstractions
- Single concrete factory with conditional logic instead of polymorphic factory hierarchy
- Over-engineering with abstract factory when only one product family will ever exist

---
description: Active Record architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design, data]
---
# Active Record

## Recognition

How to identify this pattern in code.

### Signatures

- Model classes with instance methods `save()`, `delete()`, `update()`
- Class methods like `Model.find()`, `Model.create()`, `Model.where()`
- Models inherit from a base class that provides persistence (e.g., `models.Model`, `ActiveRecord::Base`)
- Django ORM models with `objects.filter()`, `instance.save()`
- Rails ActiveRecord: `belongs_to`, `has_many`, `validates`
- Laravel Eloquent models extending `Model`
- Database columns mapped directly to model attributes

### Confidence

- **high** -- model instances call `self.save()` and class methods query the database directly
- **medium** -- ORM models with persistence mixed in but additional service layer present
- **low** -- data classes with a `to_dict()` or `from_row()` that partially resemble active record

## Architecture

Look for model objects that combine domain data and persistence logic in a single class.

### Review Checklist

- Validations are defined on the model and enforced before persistence
- Callbacks/hooks (before_save, after_create) have clear, limited scope
- Query scopes or named queries keep complex lookups readable
- Associations are declared and lazy/eager loading is intentional
- Migrations match the model schema declarations

### Anti-patterns

- Complex business logic embedded in model callbacks (hidden side effects)
- Models with dozens of query scopes that belong in a dedicated query object
- Direct SQL queries that bypass model validations and callbacks
- God models with hundreds of methods mixing persistence, business logic, and presentation

---
description: Actor Model architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [concurrency, architectural]
---
# Actor Model

## Recognition

How to identify this pattern in code.

### Signatures

- Message passing between isolated actors with no shared mutable state
- Mailbox/inbox queues per actor, `receive()` or `handle_message()` methods
- Actor references or PIDs used to address messages, not direct function calls
- Libraries: Python `pykka`, Akka (JVM), Erlang/Elixir processes, `thespian`
- Directory structures with `actors/`, `messages/`, or `mailbox` modules

### Confidence

- **high** -- Actor classes with explicit `receive()`/`on_receive()` handlers and mailbox-based dispatch
- **medium** -- Message-passing between isolated objects with no shared state, but no formal actor library
- **low** -- Isolated workers communicating through any form of async messages

## Architecture

Look for isolated actors communicating exclusively through asynchronous messages with no shared mutable state.

### Review Checklist

- Each actor encapsulates its own state -- no shared mutable data between actors
- Messages are immutable value objects, not references to mutable state
- Supervision hierarchy exists for actor failure recovery
- Mailbox overflow is handled (bounded mailbox, backpressure, or dead letters)
- Actor lifecycle is explicit: creation, restart policy, and termination

### Anti-patterns

- Actors sharing mutable state through closures or global variables
- Synchronous blocking calls between actors (defeats the concurrency model)
- Unbounded mailboxes that grow without limit under load
- Single god-actor that handles all message types instead of decomposing responsibility

---
description: Adapter architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design, integration]
---
# Adapter

## Recognition

How to identify this pattern in code.

### Signatures

- Classes named `*Adapter`, `*Gateway`, `*Wrapper`
- Translating one interface to match another expected by the caller
- Wrapper around third-party libraries isolating external API changes
- Anti-corruption layer between bounded contexts or legacy systems (see also: anti-corruption-layer)
- Import of external SDK with a thin local interface in front of it
- `adapt()`, `convert()`, `translate()` functions bridging two APIs

### Confidence

- **high** -- Class that implements a target interface by delegating to an adaptee with a different interface, with explicit mapping between the two
- **medium** -- Thin wrapper around a third-party library exposing a simplified or project-specific interface
- **low** -- Utility function that converts between two data formats without a formal adapter class

## Architecture

Adapter translates one interface to match another. Look for clean separation between the target interface and the adaptee, with mapping logic isolated in the adapter.

### Review Checklist

- Adapter maps cleanly between target and adaptee interfaces without leaking adaptee types to callers
- Third-party dependencies are wrapped so swapping the vendor only changes the adapter
- Error translation is handled -- adaptee exceptions are mapped to domain-appropriate errors
- Adapter is stateless where possible, holding no mutable state beyond the adaptee reference

### Anti-patterns

- Leaky adapter that exposes adaptee types or exceptions to callers (defeats the purpose)
- Adapter with business logic -- it should only translate, not make decisions
- No adapter at all -- third-party types used directly throughout the codebase making vendor migration painful

---
description: Aggregate Root architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design, data]
---
# Aggregate Root

## Recognition

How to identify this pattern in code.

### Signatures

- `AggregateRoot` or `AggregateBase` base class / mixin
- Root entity class that holds references to child entities (e.g., `Order` containing `OrderLine` list)
- All mutations on children go through the root's methods, never directly
- Invariant checks (guard clauses) inside root methods before modifying state
- Repository interface returns only the root entity, never child entities alone
- Domain events raised from within the aggregate root after state changes

### Confidence

- **high** -- Explicit `AggregateRoot` base class, repository loads/saves only roots, child entity constructors are internal/protected
- **medium** -- Root entity that owns a collection of child entities with mutator methods, but no formal base class
- **low** -- A "god object" that holds many child references but exposes setters on children directly

## Architecture

Look for a consistency boundary where one root entity controls all mutations to its children.

### Review Checklist

- All state changes on child entities pass through the root's public methods
- Invariants are enforced at the aggregate level before persisting
- Repository loads and saves the entire aggregate as a unit
- References between aggregates use IDs, not direct object references
- Aggregate boundaries are small enough to avoid contention
- Domain events are raised after successful state transitions, not before

### Anti-patterns

- Child entities expose public setters that bypass the root
- Aggregates reference other aggregates by object pointer instead of ID
- Single aggregate spans too many entities, causing lock contention on writes
- Business rules split between the aggregate and the service layer

See also: ddd

---
description: Anemic Domain Model anti-pattern
type: anti-pattern
graphable: false
---
# Anemic Domain Model

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Model or entity classes containing only getters and setters with no behavior or business logic methods
- All domain logic lives in `*Service` or `*Manager` classes that operate on passive data objects
- DTOs and data bags are passed everywhere with transformation logic external to the objects
- Domain objects have no validation, invariant enforcement, or state transition methods
- `*Service` classes with hundreds of methods that each manipulate the same entity types

### Confidence

- **high** -- entity classes have zero methods beyond getters/setters and all business rules are in separate service classes that accept those entities as parameters
- **medium** -- domain objects expose all fields publicly and service classes contain validation logic that belongs on the objects themselves
- **low** -- some business logic is on domain objects but key invariants (state transitions, validation) are enforced only by external services

## Impact

Business rules are scattered across service classes, making invariants impossible to enforce consistently and domain knowledge hard to locate.

### Symptoms

- The same validation logic is duplicated in multiple service classes that handle the same entity
- Invariant violations (invalid state transitions, negative balances) slip through because enforcement depends on which service method was called
- New developers cannot find business rules because they are spread across dozens of service files instead of living on the domain objects
- Unit testing requires instantiating heavyweight service classes instead of testing small domain methods in isolation
- Refactoring is risky because moving logic between services may break invariants that were implicitly maintained by call order

### Remediation

- Move business rules onto the domain objects themselves: validation in constructors, state transitions as methods
- Make domain object fields private and expose behavior through intention-revealing methods (`order.cancel()` instead of `order.setStatus("cancelled")`)
- Push invariant enforcement into the domain layer so invalid states are unrepresentable
- Use service classes only for orchestration (coordinating multiple aggregates, calling infrastructure) not for business logic
- Apply the "Tell, Don't Ask" principle: tell objects to perform actions rather than extracting data and computing externally

See also: ddd pattern (remediation)

---
description: Anti-Corruption Layer architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [integration, design]
---
# Anti-Corruption Layer

## Recognition

How to identify this pattern in code.

### Signatures

- `*Translator`, `*Mapper`, `*Adapter` classes at integration boundaries
- Separate model/DTO classes for the external system distinct from the internal domain model
- A facade or gateway wrapping an external API that returns internal domain objects
- Package or module named `integration`, `external`, `anticorruption`, or `acl`
- Mapping functions converting between external and internal representations
- External API clients isolated behind an interface the domain depends on

### Confidence

- **high** -- Dedicated translation layer with separate external and internal models, explicit mapper classes, domain never imports external types
- **medium** -- Adapter wrapping an external client that converts responses, but external types occasionally leak into domain code
- **low** -- Direct external API calls with inline field mapping in the service layer, no dedicated translation module

## Architecture

Look for a boundary translation layer that isolates internal domain models from external system models.

### Review Checklist

- External models never appear in internal domain code or interfaces
- Translation logic is centralized in mapper/translator classes, not scattered across services
- The ACL has its own test suite validating mapping correctness
- Changes to the external API require updates only in the ACL, not in domain logic
- Error handling translates external failures into domain-appropriate exceptions
- The ACL defines the interface it exposes to the domain, not the other way around

### Anti-patterns

- External DTOs used directly inside domain logic, coupling the domain to the external system
- Translation logic duplicated across multiple services instead of centralized
- ACL that grows business logic beyond translation (should only translate, not decide)
- No ACL at all -- domain objects mirror the external system's schema one-to-one

See also: adapter (implementation mechanism)

---
description: API Gateway architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [integration, infrastructure, security]
---
# API Gateway


## Recognition

How to identify this pattern in code.

### Signatures

- Kong, Envoy, NGINX Ingress, or Traefik as the gateway runtime
- AWS API Gateway or similar managed gateway service
- `Ingress` or `IngressRoute` CRDs in Kubernetes manifests
- `HTTPRoute` resources from the Gateway API spec
- Zuul or Spring Cloud Gateway in Java service configurations
- Rate limiting middleware configured at the gateway layer
- Auth middleware (JWT validation, API key checks) applied at the gateway before backend routing

### Confidence

- **high** -- dedicated gateway service with `Ingress`/`HTTPRoute` CRDs, rate limiting, and auth middleware all present
- **medium** -- gateway runtime (Kong, Envoy, Traefik) deployed with routing rules but cross-cutting concerns partially handled elsewhere
- **low** -- reverse proxy configuration (NGINX, HAProxy) performing routing without explicit rate limiting or auth enforcement

## Architecture

Look for the gateway being a thin routing/policy layer with no business logic.

### Review Checklist

- Gateway handles cross-cutting concerns only: auth, rate limiting, routing
- No business logic in the gateway — it delegates to backend services
- Timeouts and circuit breakers configured for each upstream backend
- Request/response transformation is minimal and well-documented
- Gateway failure mode is defined (fail open vs. fail closed)

### Anti-patterns

- Business logic creeping into the gateway (becomes a monolith bottleneck)
- Gateway as single point of failure with no redundancy or health checks
- Tight coupling between gateway routing rules and backend implementation details

---
description: API Key Authentication architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [security]
---
# API Key Authentication

## Recognition

How to identify this pattern in code.

### Signatures

- `X-API-Key` header extraction in middleware or gateway configuration
- `?api_key=` or `?key=` query parameter parsing
- API key validation middleware looking up keys in a database or cache
- Key-to-tenant or key-to-user mapping tables
- Rate limiting and quota enforcement per API key
- Key generation and revocation endpoints (`POST /api-keys`, `DELETE /api-keys/{id}`)
- Key rotation support with grace periods for old keys
- Key hashing before storage (keys stored as hashes, not plaintext)

### Confidence

- **high** -- `X-API-Key` header extraction, key lookup against a store with tenant mapping, and rate limiting per key
- **medium** -- API key validation present but keys used only for identification without rate limiting or tenant isolation
- **low** -- Static key comparison in code or config (hardcoded key check without a proper key management system)

## Architecture

Look for API key lifecycle management with secure storage, tenant isolation, and usage controls.

### Review Checklist

- API keys are generated with sufficient entropy (256+ bits, cryptographically random)
- Keys are hashed before storage (never stored in plaintext in the database)
- Key validation is constant-time to prevent timing attacks
- Rate limiting and quota enforcement are applied per key
- Key revocation is immediate (not cached for extended periods after revocation)
- Keys are transmitted only in headers, never in URLs (URLs are logged by proxies and browsers)

### Anti-patterns

- Hardcoding API keys in source code or configuration files checked into version control
- Storing keys in plaintext in the database (compromised DB exposes all keys)
- Using API keys as the sole authentication for sensitive operations (keys lack identity binding, prefer OAuth for user context)
- Passing keys in URL query parameters (logged in access logs, browser history, and referrer headers)

---
description: Abstract Syntax Tree (AST) architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [data, compiler]
---
# Abstract Syntax Tree (AST)

## Recognition

How to identify this pattern in code.

### Signatures

- Tree node classes or enums representing language constructs (`IfExpr`, `BinOp`, `FnDecl`, `LetStmt`)
- Base type `ASTNode`, `Node`, or `Expr` with subtypes for each syntactic form
- `ExprNode`/`StmtNode`/`DeclNode` hierarchy separating expressions, statements, and declarations
- Visitor pattern: `visit_*` methods or `accept()` on nodes dispatching to a visitor
- Source location fields (`span`, `loc`, `pos`) on every node for error reporting and tooling
- Node type enum or tagged union discriminating between syntactic forms
- Tree traversal utilities: `walk()`, `traverse()`, `fold()` operating on the node tree

### Confidence

- **high** — node type hierarchy with `visit_*` methods, source location tracking, and distinct expression/statement/declaration categories
- **medium** — enum or tagged union of syntax node types with recursive children and span information
- **low** — nested data structures representing code with type tags but no formal visitor or traversal API

## Architecture

Look for a well-typed tree representation of parsed source code with systematic traversal support.

### Review Checklist

- Every node type carries source location for error messages, diagnostics, and source maps
- Node types are exhaustive: all language constructs have explicit representations (no catch-all "Other" node)
- Visitor or walker pattern enables traversal without modifying node definitions
- Tree is immutable after construction, with transformations producing new trees
- Type nodes distinguish expressions (produce values) from statements (produce effects)
- Pretty-printer can reconstruct source from AST, validating round-trip fidelity

### Anti-patterns

- Catch-all node type (e.g., `GenericNode`) used for multiple unrelated constructs
- Mutable AST nodes modified in place during analysis passes (hard to debug, prevents parallelism)
- No source location on nodes, making downstream error reporting impossible
- Visitor with default no-op methods that silently skip new node types after grammar changes

---
description: Audit Logging architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [security, observability]
---
# Audit Logging

## Recognition

How to identify this pattern in code.

### Signatures

- `AuditLog` model, table, or collection storing who-did-what-when
- Fields: `actor`, `action`, `target`, `timestamp` (and optionally `before`/`after` state)
- Audit middleware intercepting requests or database operations
- `@audited` or `@audit_log` decorators on endpoints or service methods
- Append-only write pattern -- no UPDATE or DELETE on the audit table
- Compliance logging for regulatory requirements (SOC2, HIPAA, GDPR)
- Separate audit storage or write-ahead log distinct from application logs

### Confidence

- **high** -- dedicated audit table with actor/action/target/timestamp fields and append-only writes
- **medium** -- structured logging of user actions but stored in general application logs, not a dedicated audit trail
- **low** -- `logger.info` calls that include user and action but no structured schema or immutability guarantee

## Architecture

Look for an immutable, structured record of every significant action with actor attribution.

### Review Checklist

- Audit records are append-only -- no mechanism to update or delete entries
- Every state-changing operation is captured with actor, action, target, and timestamp
- Audit log is stored separately or with different retention than application logs
- Sensitive fields are redacted or masked in audit records
- Audit writes do not block the primary operation (async or fire-and-forget with delivery guarantee)
- Tamper detection is in place (checksums, hash chains, or write-once storage)

### Anti-patterns

- Audit records stored in the same mutable table as application data
- Missing actor attribution -- logs show what happened but not who did it
- Audit writes in the critical path causing latency on every user action
- No retention policy -- audit data grows unbounded without archival or rotation

---
description: Backpressure architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [resilience, concurrency]
---
# Backpressure

## Recognition

How to identify this pattern in code.

### Signatures

- `Flowable` or `Observable` with `onBackpressure*` operators (RxJava)
- `asyncio.Queue(maxsize=)` with bounded capacity (Python)
- `BoundedChannel` from Rust tokio for capacity-limited async channels
- `BlockingQueue` with explicit capacity (Java `ArrayBlockingQueue`, `LinkedBlockingQueue(capacity)`)
- Kafka consumer configuration with `max.poll.records` limiting batch size
- `reactor.core.publisher.Flux` with backpressure operators (`limitRate`, `onBackpressureBuffer`, `onBackpressureDrop`)
- Go channel with explicit buffer size (`make(chan T, N)`) used for flow control

### Confidence

- **high** -- explicit backpressure operators (`onBackpressureDrop`, `onBackpressureBuffer`, `limitRate`) with bounded queues and rejection/drop policies
- **medium** -- bounded queues or channels with capacity limits but no explicit backpressure signaling to the producer
- **low** -- unbounded queues with consumer lag monitoring but no active flow control mechanism

## Architecture

Flow control mechanism for when a producer is faster than its consumer. Prevents memory exhaustion and queue overflow by signaling the producer to slow down or by shedding load. Common strategies include rate limiting, bounded queues with rejection, and reactive pull-based consumption.

---
description: Batch Loader (N+1 Prevention) architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [data]
---
# Batch Loader (N+1 Prevention)

## Recognition

How to identify this pattern in code.

### Signatures

- DataLoader pattern: batched key collection with deferred resolution (`new DataLoader(batchFn)`)
- Batched queries: `SELECT ... WHERE id IN (...)` replacing per-item lookups
- `prefetch_related` (Django), `includes` (Rails), `Include` (EF Core) for eager loading associations
- GraphQL DataLoader for batching field resolvers across a single request
- `@BatchMapping` (Spring), `@ResolveField` with loader injection
- Deferred resolution or promise-based batching that collects keys and flushes in one query
- Query batching middleware that groups individual lookups into bulk fetches

### Confidence

- **high** -- Explicit DataLoader instances or batch functions that collect keys and execute `WHERE id IN (?)`
- **medium** -- ORM eager loading directives (`includes`, `prefetch_related`) applied to associations
- **low** -- Manual query grouping where related IDs are collected into an array before a single query

## Architecture

Look for systematic batching of data fetches to eliminate per-item queries, especially in nested or graph-shaped data.

### Review Checklist

- DataLoader or equivalent batching is applied to all association lookups in resolver/handler layers
- Batch functions handle partial results gracefully (return null for missing keys, maintain key order)
- Cache scope is per-request to avoid serving stale data across different users or contexts
- Maximum batch size is configured to prevent excessively large `IN (...)` clauses
- Batch loaders are tested for correctness: key ordering matches result ordering
- N+1 detection tooling or query logging is in place to catch regressions

### Anti-patterns

- DataLoader cache persisting across requests, serving stale or leaked data between users
- Batch function that does not preserve key-to-result ordering, returning mismatched data
- Applying batching only at the top level while nested resolvers still trigger per-item queries
- No maximum batch size, generating SQL queries with thousands of IDs in the IN clause

See also: n-plus-one anti-pattern

---
description: Batch processing flow — data processed in discrete chunks on a schedule
type: flow-shape
abstraction: [data, lifecycle]
---
# Batch Processing

## Recognition

### Signatures

- Cron-scheduled jobs processing accumulated data
- `LIMIT`/`OFFSET` or cursor-based pagination through a large dataset
- Batch size configuration: `BATCH_SIZE = 1000`
- Spring Batch `ItemReader` → `ItemProcessor` → `ItemWriter`
- Celery tasks with `chunks()` or batch processing
- DuckDB/Spark batch queries over partitioned data
- Nightly/hourly report generation
- Bulk API endpoints: `POST /api/bulk-import`
- Queue-based batch: accumulate N messages then process together
- `flush()` or `commit()` after processing a batch

### Confidence

- **high** — explicit batch framework or scheduled job with configurable batch size, progress tracking, and error handling per batch
- **medium** — periodic job processing accumulated data but without structured batching (processes all at once)
- **low** — large query results processed in a loop without explicit batch boundaries

---
description: Backend for Frontend architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [api, architectural]
---
# Backend for Frontend

## Recognition

How to identify this pattern in code.

### Signatures

- Separate API layers per frontend type: `/api/mobile/*`, `/api/web/*`, `/api/admin/*`
- Distinct services or modules named `mobile-bff`, `web-bff`, `admin-gateway`
- Response shaping logic tailored to specific frontend needs (mobile gets compact payloads, web gets richer data)
- Aggregation of multiple microservice calls into a single frontend-optimized response
- Frontend-specific authentication flows (cookie-based for web, token-based for mobile)
- Different API versioning or deprecation timelines per frontend

### Confidence

- **high** -- separate deployable services per frontend type, each aggregating calls to shared backend microservices
- **medium** -- single API with frontend-specific routes or middleware that shape responses differently per client type
- **low** -- `User-Agent` based response variation or a single monolithic API serving all frontends

## Architecture

Look for a dedicated API aggregation layer per frontend with clear separation of frontend-specific concerns from shared backend services.

### Review Checklist

- Each BFF is owned by the frontend team that consumes it
- BFF contains only aggregation and response shaping logic, not business rules
- Shared business logic lives in backend services, not duplicated across BFFs
- Each BFF has independent deployment and scaling from other BFFs
- Authentication and session management are appropriate for each frontend's platform constraints

### Anti-patterns

- Putting business logic in the BFF instead of shared backend services (logic duplication)
- Single BFF serving all frontends (defeats the purpose, becomes a generic API gateway)
- BFF-to-BFF calls (BFFs should only call downstream services, never each other)
- Frontend teams blocked by a shared BFF team (BFF should be frontend-team owned)

---
description: Big Ball of Mud anti-pattern
type: anti-pattern
graphable: false
---
# Big Ball of Mud

## Recognition

How to identify this anti-pattern in code.

### Signatures

- No directory structure convention -- files placed arbitrarily without grouping by feature, layer, or domain
- Any file can import any other file with no enforced module boundaries
- Business logic embedded directly in controllers, handlers, or route definitions
- Database queries written directly in templates, views, or presentation layer
- No separation between public API surface and internal implementation
- Circular imports treated as normal rather than as a design smell

### Confidence

- **high** -- business logic in controllers, SQL in templates, no discernible directory organization, any-to-any import graph
- **medium** -- import graph shows no layering (presentation imports data layer and vice versa), directory names are generic ("utils", "helpers", "misc")
- **low** -- inconsistent organization that mixes conventions (some modules follow a pattern, others do not)

## Impact

No discernible architecture makes it impossible to reason about the system, predict side effects, or onboard new developers.

### Symptoms

- Changing a database schema requires modifying files across every directory
- There is no answer to "where does X logic live?" -- it could be anywhere
- Developers duplicate functionality because they cannot find existing implementations
- Test setup requires initializing the entire application because nothing is isolated
- Architectural diagrams do not match the code because the code has no enforced structure

### Remediation

- Define explicit module boundaries: group code by domain or feature, enforce import rules (e.g., domain must not import from presentation)
- Extract business logic from controllers into dedicated service or domain modules
- Move database access behind repository interfaces so queries are not scattered
- Introduce an architectural linter (e.g., import-linter for Python, ArchUnit for Java) to enforce layering
- Start with one bounded context: refactor it into a clean structure as a model for the rest

---
description: Block-based content model for structured rich text editing
type: pattern
category: domain-model
abstraction: [data, content]
---
# Block Content

## Recognition

How to identify this pattern in code.

### Signatures

- `block`, `Block`, `block_type` fields defining typed content units
- `children` arrays on blocks forming a nested tree structure
- `rich_text`, `RichText` models or fields with inline formatting spans
- Slate.js: `slate`, `slate-react`, `Editable`, `Element`, `Leaf` components
- ProseMirror: `prosemirror-model`, `prosemirror-state`, `Schema`, `Node`, `Mark`
- Tiptap: `@tiptap/core`, `@tiptap/starter-kit`, `Editor`, custom `Extension`
- Draft.js: `draft-js`, `EditorState`, `ContentBlock`, `convertToRaw`
- Editor.js: `@editorjs/editorjs`, `tools` configuration, block-based output JSON
- Python: Wagtail `StreamField`, `StructBlock`, `ListBlock`, `RichTextBlock`
- `content_block`, `BlockSerializer`, `block_data` in API payloads

### Confidence

- **high** -- ProseMirror/Slate/Tiptap editor with typed block schema, nested block hierarchy, and collaborative editing support
- **medium** -- Editor.js or Wagtail StreamField with block type definitions and structured JSON output
- **low** -- HTML blob stored in a text column with client-side WYSIWYG editing but no block structure

## Architecture

### When to use
- Content management systems where editors need structured, reusable content blocks
- Collaborative editing platforms requiring granular change tracking per block
- Applications where content must render across multiple targets (web, mobile, email) from a single structured source

### Anti-patterns
- Storing content as raw HTML, losing semantic structure and making cross-platform rendering brittle
- Deeply nested block hierarchies without depth limits, causing rendering performance issues
- Building a custom block editor instead of using ProseMirror/Slate/Tiptap, which handle edge cases in text editing

### Complements
- [versioned-document](/concepts/versioned-document) — block content benefits from per-block version tracking
- [component](/concepts/component) — content blocks map to rendering components in the frontend
- [search-index](/concepts/search-index) — block content must be flattened for full-text indexing

## Impact

Block-based content structures determine how content is stored, edited, and rendered across platforms. The choice of editor framework cascades into serialization format, collaboration protocol, and rendering pipeline, making it a foundational architectural decision.

---
description: Bloom Filter architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [data]
---
# Bloom Filter

## Recognition

How to identify this pattern in code.

### Signatures

- Probabilistic membership test: `add()` and `might_contain()` (or `__contains__` returning possible matches)
- Multiple independent hash functions applied to the same element
- Underlying bit array (bitset) with fixed size
- False positive rate configuration parameter (e.g., `error_rate=0.01`)
- No delete or remove support (standard Bloom filter)
- Libraries: `pybloom`, `pybloomfilter`, `bloom-filter` (Node), Guava `BloomFilter` (Java)
- Redis `BF.ADD`, `BF.EXISTS` commands (RedisBloom module)
- Counting Bloom filter variant with decrement support

### Confidence

- **high** -- Bit array with multiple hash functions, explicit false positive rate, and no deletion
- **medium** -- Probabilistic set membership check with configurable accuracy but unclear internals
- **low** -- Hash-based lookup with possible false positives that may be a Bloom filter

## Architecture

Look for correct probabilistic semantics where false positives are acceptable but false negatives are not.

### Review Checklist

- False positive rate is configured based on expected element count and acceptable error margin
- Bit array size and hash function count are derived from the target false positive rate
- No code path assumes `might_contain()` means "definitely contains"
- Filter is sized for the expected dataset -- undersized filters degrade to near-100% false positive rate
- Membership checks that return true are followed by a definitive lookup (database, cache)
- Filter is not used where deletion is required (use counting Bloom filter or cuckoo filter instead)

### Anti-patterns

- Treating a Bloom filter positive as a definitive answer without secondary verification
- Undersizing the filter for the dataset, causing unacceptable false positive rates
- Attempting to remove elements from a standard (non-counting) Bloom filter
- Using a Bloom filter where exact membership is required (correctness over performance)

---
description: Blue-Green Deployment architectural pattern
type: pattern
observable: true
distributed: true
graphable: true
abstraction: [deployment]
---
# Blue-Green Deployment

## Recognition

How to identify this pattern in code.

### Signatures

- Two identical environments labeled `blue`/`green` or `active`/`standby`
- Traffic switching via DNS, load balancer, or service selector swap
- Environment variables like `DEPLOY_ENV=blue`, `ACTIVE_SLOT=green`
- K8s: duplicate Deployment manifests with Service selector toggling between label values
- Infrastructure-as-code with mirrored environment blocks (Terraform workspaces, duplicate modules)
- Health check validation on standby before traffic switch

### Confidence

- **high** -- two parallel deployments with identical specs differing only by environment label, plus a traffic switch mechanism
- **medium** -- blue/green naming in manifests or CI/CD pipeline stages, LB target group swaps
- **low** -- two environments exist but no automated switch mechanism is visible

## Architecture

Look for paired environments with an atomic traffic cutover and rollback path.

### Review Checklist

- Both environments are truly identical (same image, config, resource limits)
- Traffic switch is atomic (no period where both receive production traffic unintentionally)
- Database migrations are backward-compatible (both versions must work during switch window)
- Rollback procedure is tested and can revert traffic to the previous environment quickly
- Health checks validate the standby environment before the switch executes

### Anti-patterns

- Database schema changes that break the old version (no backward compatibility)
- Manual traffic switching with no automation or runbook
- Letting the idle environment drift in configuration or fall behind on patches
- No smoke tests on the standby environment before switching traffic

---
description: Boolean Blindness anti-pattern
type: anti-pattern
graphable: false
---
# Boolean Blindness

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Functions taking 3 or more boolean parameters: `create(true, false, true)`
- Boolean arguments with no name visible at the call site, making intent unclear
- Parameters named `flag1`, `flag2`, `flag3` or single-letter booleans
- Long chains of `if flag_a and not flag_b or flag_c` with no explanation of what the combination means
- Functions where adding a new option means adding another boolean parameter

### Confidence

- **high** -- a function call passes 3+ boolean literals with no keyword names: `process(true, false, true, false)`
- **medium** -- a function signature has 2 boolean parameters and callers never use keyword arguments
- **low** -- a boolean parameter exists but is always called with a named argument or has a self-documenting name

## Impact

Unreadable call sites where the meaning of each `true`/`false` is invisible, leading to subtle errors when arguments are swapped or misunderstood.

### Symptoms

- Developers must jump to the function definition to understand what each boolean means at every call site
- Arguments accidentally swapped (both are bool, compiler does not catch it) cause silent logic errors
- Adding a new boolean option to an existing function creates a combinatorial explosion
- Code reviews cannot verify correctness without cross-referencing the function signature
- Boolean parameters accumulate over time as quick fixes for "just one more flag"

### Remediation

- Replace boolean parameters with enums or named constants: `Mode.STRICT` instead of `True`
- Use a configuration object or builder pattern when a function needs multiple options
- In languages that support it, require keyword-only arguments for booleans: `def create(*, strict: bool, verbose: bool)`
- Split the function into separate methods if the booleans select fundamentally different behavior
- As a minimum, always use named arguments at call sites: `create(strict=True, validate=False)`

---
description: Breaking Changes anti-pattern
type: anti-pattern
graphable: false
---
# Breaking Changes

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Removed fields from API responses without a deprecation period
- Changed response types (string to integer, object to array) in existing endpoints
- Renamed endpoints or changed URL paths with no version bump
- No API versioning strategy: no `/v1/`, `/v2/` prefix, no `Accept` header versioning
- Clients breaking after every deploy due to contract changes
- Database column renames or type changes that break existing queries from other services

### Confidence

- **high** -- fields removed or types changed in a response schema with no version increment and no deprecation notice
- **medium** -- an API versioning scheme exists but breaking changes are shipped within the same version
- **low** -- additive changes (new optional fields) are introduced, which are usually safe but not always

## Impact

Downstream failures and broken integrations every time the API changes, eroding trust and forcing consumers to pin to old versions or break.

### Symptoms

- Consumer applications crash or show errors after an API deployment they were not warned about
- Multiple teams spend time debugging the same breaking change independently
- API consumers refuse to upgrade because previous upgrades broke them
- Changelog is empty or vague, giving no indication of what changed
- Integration test suites that worked yesterday fail today with deserialization errors

### Remediation

- Adopt a versioning strategy (URL path, header, or query parameter) and increment the version for any breaking change
- Deprecate fields before removing them: mark as deprecated, wait one or more release cycles, then remove
- Use additive-only changes within a version: new fields are optional, old fields remain
- Publish a machine-readable API schema (OpenAPI, Protobuf) and run contract tests in CI
- Notify consumers proactively through changelogs, migration guides, or deprecation headers in responses

---
description: Bridge architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Bridge

## Recognition

How to identify this pattern in code.

### Signatures

- Separating abstraction from implementation so both can vary independently
- Abstraction holding a reference to an implementor interface
- Platform-specific implementations behind a stable API
- `*Impl` classes or interfaces (`Renderer`, `RendererImpl`, `OpenGLRenderer`)
- Constructor injection of the implementation into the abstraction
- Two parallel class hierarchies (one for abstraction, one for implementation)

### Confidence

- **high** -- Abstraction class holding a reference to an `Impl` interface, with multiple concrete implementations that can be swapped independently of the abstraction hierarchy
- **medium** -- Interface-based dependency injection where the abstraction and implementation evolve in separate packages or modules
- **low** -- Simple interface extraction without a separate abstraction hierarchy (closer to strategy than bridge)

## Architecture

Look for two independent hierarchies connected by composition: an abstraction hierarchy delegating to an implementation hierarchy.

### Review Checklist

- Abstraction and implementation can vary independently without modifying each other
- Implementation is injected, not hardcoded in the abstraction
- The bridge interface is minimal and stable (changes are rare)
- Both hierarchies are tested independently
- New implementations can be added without modifying existing abstractions
- The indirection is justified by actual variation on both sides

### Anti-patterns

- Only one implementation exists with no realistic expectation of a second (unnecessary abstraction)
- Abstraction leaking implementation details through its interface
- Tight coupling between abstraction and implementation hierarchies despite the bridge
- Confusing bridge with simple interface extraction or strategy pattern

---
description: Builder architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Builder

## Recognition

How to identify this pattern in code.

### Signatures

- Classes ending in `Builder`, `Config`, or `Options` with fluent setter methods
- Methods returning `self` or `this` to enable chaining
- Terminal `build()`, `create()`, or `make()` method that produces the final object
- Python: setter methods with `return self`, `@dataclass` with builder wrapper
- JS/TS: method chaining patterns, optional `Director` class orchestrating build steps
- Go: functional options pattern (`With*()` functions), or `*Builder` structs with `Build()` method

### Confidence

- **high** -- class named `*Builder` with fluent methods and a terminal `build()` returning a different type
- **medium** -- method chaining returning `self`/`this` with a finalizing method
- **low** -- constructor with many optional parameters or a config dict

## Architecture

Look for separation between construction steps and the final product representation.

### Review Checklist

- Builder validates required fields in `build()`, not silently producing incomplete objects
- Builder is independent of the product's internal representation
- Fluent methods are idempotent (calling the same setter twice overwrites, not appends)
- Builder can be reused to create multiple instances without state leakage between builds
- Director (if present) encapsulates a specific construction sequence, not arbitrary logic

### Anti-patterns

- Builder that exposes product internals (setters map 1:1 to private fields)
- No validation in `build()` -- produces invalid objects that fail later at runtime
- Builder and product tightly coupled -- changing the product breaks the builder
- God-builder with dozens of methods that should be split into multiple builders

---
description: Bulkhead architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [resilience]
---
# Bulkhead


## Recognition

How to identify this pattern in code.

### Signatures

- `resilience4j-bulkhead` dependency and `@Bulkhead` annotations (Java)
- Hystrix thread pool isolation configuration (`HystrixCommand` with `threadPoolKey`)
- Envoy circuit breaking configuration with `max_connections`, `max_pending_requests` per cluster
- `Semaphore`-based isolation limiting concurrent access to a resource
- `ThreadPoolBulkhead` configuration in Java resilience libraries
- Separate thread pools or connection pools allocated per downstream dependency

### Confidence

- **high** -- named bulkhead instances per dependency with explicit pool sizing, rejection metrics, and fallback behavior
- **medium** -- separate connection pools or thread pools per dependency but without formal bulkhead library usage or rejection handling
- **low** -- single pool with per-dependency concurrency limits enforced via semaphores or ad-hoc locking

## Architecture

Look for isolated resource pools per dependency — one failing dependency must not exhaust all resources.

### Review Checklist

- Each external dependency has its own bounded resource pool (threads, connections)
- Pool sizes are configured per dependency based on expected load
- Pool exhaustion triggers rejection (fast fail), not unbounded queuing
- Metrics exposed per pool: active, idle, waiting, rejected counts

### Anti-patterns

- Single shared connection/thread pool across all dependencies
- No pool size limits — one slow dependency consumes all available resources
- Bulkhead without monitoring — pool exhaustion goes unnoticed until outage

---
description: Busy Waiting anti-pattern
type: anti-pattern
observable: true
graphable: false
---
# Busy Waiting

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `while True: sleep(0.1); if condition: break` polling loops
- Polling loops with `time.sleep()` or `Thread.sleep()` checking a flag or state
- CPU spin waiting for a state change without yielding (`while not ready: pass`)
- `setTimeout`/`setInterval` polling for a value that could be pushed via events or callbacks
- Repeated database or API polling in a loop instead of using webhooks, subscriptions, or message queues
- Retry loops with fixed sleep intervals and no exponential backoff

### Confidence

- **high** -- a `while` loop contains only a `sleep()` call and a condition check, running continuously in a thread or process, confirmed by CPU profiling showing time spent in the polling function
- **medium** -- `time.sleep()` or `Thread.sleep()` appears inside a loop that checks an external condition (file existence, API response, flag variable)
- **low** -- a `setInterval` or scheduled task polls a resource at a fixed interval where an event-driven alternative exists (webhooks, pub/sub, filesystem watchers)

## Impact

Wasted CPU cycles, delayed response times (up to the sleep interval), and battery/resource drain on constrained environments.

### Symptoms

- CPU usage remains elevated even when the system is idle
- Response to state changes is delayed by the polling interval (latency floor)
- Thread or process pool is consumed by polling loops, reducing capacity for real work
- Battery drain on mobile or edge devices from constant wake-ups
- Unnecessary load on polled services (database, API) from repeated queries

### Remediation

- Replace polling with event-driven mechanisms: callbacks, promises/futures, condition variables, or message queues
- Use OS-level or framework-level waiting primitives (`threading.Event.wait()`, `asyncio.Event`, `select()`, `epoll`)
- For file system changes, use watchers (`inotify`, `fswatch`, `watchdog`) instead of polling loops
- If polling is unavoidable, use exponential backoff with jitter to reduce load and improve responsiveness
- For inter-service communication, prefer webhooks or pub/sub over periodic API polling

---
description: Cache-Aside architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [data, resilience]
---
# Cache-Aside

## Recognition

How to identify this pattern in code.

### Signatures

- Check cache first, on miss load from source, then populate cache before returning
- TTL (time-to-live) configuration on cached entries
- Cache key generation functions or key templates
- Redis or Memcached client calls with fallback to database queries
- `@cache` or `@cached` decorators with expiration parameters
- Pattern: `get from cache -> if nil -> fetch from DB -> set in cache -> return`
- Cache invalidation on write paths: `cache.delete(key)` after updates

### Confidence

- **high** -- explicit check-cache/load-source/populate-cache flow with TTL configuration
- **medium** -- caching decorator or middleware with automatic key generation
- **low** -- manual in-memory dict used as a cache with no eviction policy

## Architecture

Look for a read path that tries cache first and falls back to the source of truth, with explicit cache population and invalidation.

### Review Checklist

- Cache miss path correctly populates the cache before returning the result
- TTLs are set appropriately for the data's staleness tolerance
- Cache invalidation happens on every write path that modifies the cached data
- Cache key collisions are prevented (namespaced, versioned, or hashed keys)
- Thundering herd is mitigated (locking, request coalescing, or stale-while-revalidate)
- Serialization format is versioned to survive schema changes

### Anti-patterns

- Forgetting to invalidate cache on write (serving stale data indefinitely)
- Cache keys without namespacing leading to collisions across entities
- No TTL set, relying entirely on manual invalidation (cache grows unbounded)
- Caching errors or empty results (negative caching without short TTL)

---
description: Cache Stampede Prevention architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [data, resilience, concurrency]
---
# Cache Stampede Prevention

## Recognition

How to identify this pattern in code.

### Signatures

- Lock-based cache population (only one thread/process recomputes on miss)
- `singleflight` package (Go) coalescing concurrent requests for the same key
- Probabilistic early recomputation (XFetch algorithm)
- Request coalescing for identical in-flight cache loads
- `SETNX` or `SET NX` for distributed cache locks
- `@CachePut` with locking or mutex around the computation
- Semaphore or mutex guarding cache population code paths

### Confidence

- **high** -- `singleflight.Group.Do()` or explicit mutex/lock around cache-miss computation with other requesters waiting
- **medium** -- `SETNX`-based distributed lock for cache population, or probabilistic early recomputation logic
- **low** -- Short TTLs with staggered expiry that reduce but do not eliminate stampede risk

## Architecture

Look for coordination mechanisms that ensure only one caller recomputes a cache entry while others wait or receive a stale value.

### Review Checklist

- Lock holder timeout prevents deadlock if the computing thread crashes
- Waiters have a bounded timeout and fallback (do not block indefinitely)
- Lock granularity is per-key, not global (avoids serializing unrelated cache misses)
- Stale-while-revalidate is used where acceptable to serve old values during recomputation
- Distributed lock cleanup handles node failures (TTL on the lock key itself)
- Probabilistic early recomputation parameters are tuned to the access pattern

### Anti-patterns

- Global lock for all cache misses, serializing unrelated keys
- No timeout on the lock, causing permanent blocking if the holder crashes
- Every caller independently recomputes on miss without coordination (the stampede itself)
- Lock without retry or fallback, causing callers to fail instead of waiting

---
description: Callback Hell anti-pattern
type: anti-pattern
graphable: false
---
# Callback Hell

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Deeply nested callbacks (4+ levels of indentation from nested anonymous functions)
- Pyramid-shaped code where each async step is indented further than the last
- `.then().then().then()` chains exceeding 5 links without intermediate variables
- Error handling duplicated at every callback level instead of centralized
- No use of async/await despite the language and runtime supporting it

### Confidence

- **high** -- 4+ nested callback levels with error handling duplicated at each level in a language that supports async/await
- **medium** -- 3+ nested callbacks or a `.then()` chain longer than 5 steps without named intermediate functions
- **low** -- a single 2-level nested callback that could become deeper as the feature grows

## Impact

Unreadable and error-prone async code where control flow, error handling, and resource cleanup are nearly impossible to reason about.

### Symptoms

- Developers cannot trace the execution order without careful manual indentation-counting
- Errors are silently swallowed because a catch handler was missed at one nesting level
- Adding a new async step requires re-indenting large blocks of code
- Resource cleanup (closing connections, releasing locks) is duplicated or missed across branches
- Testing requires complex mocking of nested callback chains

### Remediation

- Convert nested callbacks to async/await syntax where the language supports it
- Extract each callback into a named function with a clear purpose and flat structure
- Use promise/future combinators (`Promise.all`, `Promise.race`) for parallel operations instead of nesting
- Centralize error handling with a single try/catch or `.catch()` at the top level of the async flow
- For languages without async/await, adopt a control flow library (async.js, Reactor) that linearizes callback sequences

---
description: Canary Release architectural pattern
type: pattern
observable: true
distributed: true
graphable: true
abstraction: [deployment]
---
# Canary Release

## Recognition

How to identify this pattern in code.

### Signatures

- Traffic splitting with explicit percentages (e.g., 5%, 10%, 50%, 100%)
- Canary annotations in K8s manifests or Ingress resources
- Istio `VirtualService` with traffic weights between stable and canary subsets
- Argo Rollouts `Rollout` resources with `canary` strategy and `steps`
- Flagger `Canary` CRDs with `stepWeight` and `maxWeight` fields
- Metrics comparison logic between canary and stable (error rate, latency thresholds)
- CI/CD pipeline stages named `canary-deploy`, `canary-promote`, `canary-rollback`

### Confidence

- **high** -- traffic weight configuration with gradual step increments and automated promotion/rollback based on metrics
- **medium** -- canary-labeled deployments or pods alongside stable, manual promotion steps in pipeline
- **low** -- separate deployment for a subset of traffic but no automated analysis or rollback

## Architecture

Look for gradual traffic shifting with metrics-driven promotion or rollback decisions.

### Review Checklist

- Promotion criteria are defined with measurable thresholds (error rate, p99 latency)
- Automatic rollback triggers on metric degradation before reaching full traffic
- Canary and stable run the same configuration except for the image version
- Metrics comparison uses a statistically meaningful sample size and time window
- Canary traffic percentage steps are small enough to limit blast radius

### Anti-patterns

- Promoting canary based on time alone without checking metrics
- Starting canary at too high a percentage (defeats the purpose of gradual rollout)
- No automated rollback -- relying on human intervention to catch regressions
- Comparing canary metrics against static thresholds instead of the live stable baseline

---
description: Cargo Cult Programming anti-pattern
type: anti-pattern
graphable: false
---
# Cargo Cult Programming

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Design patterns applied without understanding their purpose (e.g., a Factory that only ever creates one type, a Singleton wrapping a stateless utility, a Repository layered over another Repository)
- Copy-pasted boilerplate with no modification or adaptation to the local context
- Over-abstracted simple code: interfaces with a single implementation and no foreseeable second one
- Cargo-culted configuration: settings copied from tutorials with no understanding of what they do
- "Best practice" applied everywhere regardless of whether the problem it solves exists here

### Confidence

- **high** -- Factory with one product, Singleton around pure functions, interface with exactly one implementation and no test doubles, Repository wrapping an ORM that is itself a repository
- **medium** -- boilerplate blocks identical across files with only names changed, configuration values matching popular tutorial defaults
- **low** -- abstractions that seem premature but might have future justification

## Impact

Adds complexity without benefit, making the codebase harder to read and maintain while solving no actual problem.

### Symptoms

- Developers must navigate through multiple indirection layers to find actual logic
- New team members ask "why is this pattern here?" and nobody can answer
- Adding a simple feature requires modifying boilerplate in 5+ files
- The codebase has more structural code (interfaces, factories, registries) than business logic
- Removing an abstraction layer causes no test failures, proving it added no value

### Remediation

- For each abstraction, document the concrete problem it solves -- delete it if no concrete problem exists
- Apply YAGNI: do not add patterns until a second use case demands them
- Replace single-implementation interfaces with concrete classes until polymorphism is actually needed
- Consolidate copy-pasted boilerplate into shared utilities or eliminate it entirely
- Review configuration values against documentation and remove or explain each non-default setting

---
description: Catalog and inventory pattern for product management and stock tracking
type: pattern
category: domain-model
abstraction: [data, commerce]
---
# Catalog

## Recognition

How to identify this pattern in code.

### Signatures

- `Product`, `Variant`, `SKU` model classes with relationships between them
- `stock`, `inventory`, `quantity_on_hand`, `available_quantity` fields
- `Catalog`, `Category`, `Collection` grouping models for product organization
- `price`, `Price`, `PricingRule` models with currency and amount fields
- `cart`, `Cart`, `CartItem`, `line_item`, `LineItem` for purchase aggregation
- Python: `django-oscar`, `saleor`, `product` app with variant and stock models
- JS/TS: `medusa`, `saleor`, `shopify-api` imports, product/variant types
- Go: product/variant/inventory structs, stock management service
- Rust: commerce domain models with `Sku`, `Variant`, `InventoryLevel`
- Java: `Product` entity with `@OneToMany` variants, `StockLevel` tracking

### Confidence

- **high** -- Product/Variant/SKU hierarchy with inventory tracking, pricing rules, and cart/line-item models forming a complete commerce domain
- **medium** -- Product catalog with categories and variants but inventory managed externally
- **low** -- Simple item list with a price field but no variant, stock, or pricing rule concepts

## Architecture

### When to use
- E-commerce platforms with product listings, variants (size, color), and inventory management
- Marketplace applications with multi-seller catalogs and unified search
- Any system managing a catalog of purchasable items with pricing and availability

### Anti-patterns
- Storing variant attributes as free-form JSON without a defined schema, making queries and validation unreliable
- Stock tracking without concurrency control, allowing overselling under concurrent purchases
- Price calculation scattered across the codebase instead of centralized in a pricing service or rule engine

### Complements
- [search-index](/concepts/search-index) — product catalogs need full-text search with faceted filtering
- [rule-engine](/concepts/rule-engine) — pricing rules and promotions often use rule-based evaluation
- [subscription](/concepts/subscription) — subscription commerce combines catalog with recurring billing

## Impact

Catalog models sit at the center of commerce systems, affecting search, checkout, fulfillment, and analytics. Stock accuracy directly impacts customer experience, and pricing consistency requires centralized rule evaluation. Testing must cover concurrent stock operations, and monitoring should track inventory accuracy and pricing rule evaluation.

---
description: Cell-based structure — independent cells that can scale, deploy, and fail independently
type: structure-shape
abstraction: [architectural, deployment]
---
# Cell-Based

## Recognition

### Signatures

- Multiple identical deployments serving different customer segments or regions
- Shard-nothing architecture: each cell has its own database, cache, and queue
- Cell routing: requests routed to the correct cell by tenant ID, region, or hash
- Blast radius isolation: failure in one cell doesn't affect others
- Independent deployment: cells can be updated one at a time (canary per cell)
- Cell-level configuration: each cell can have different feature flags or limits
- AWS Cell-Based Architecture patterns or similar cloud-native cell designs
- `cell_id` or `shard_id` in routing logic and configuration

### Confidence

- **high** — explicit cell architecture with independent data stores, cell routing, and independent deployment
- **medium** — multi-region deployment with region-specific resources but shared control plane
- **low** — sharded database with application-level routing but shared application tier

---
description: Chain of Responsibility architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Chain of Responsibility

## Recognition

How to identify this pattern in code.

### Signatures

- Middleware chains: `app.use()`, `next()` calls, ordered handler lists
- Handler objects with `next` or `successor` references
- Pipeline or processor chain: `pipeline.add()`, `chain.add_handler()`
- Express/Koa middleware stacks, Django `MIDDLEWARE` setting, ASP.NET middleware pipeline
- Python: logging `Handler` with `setLevel()` chains, WSGI/ASGI middleware
- Go: `http.Handler` wrapping with `ServeHTTP`, middleware functions returning `http.Handler`
- Java: servlet filters, Spring interceptors

### Confidence

- **high** -- ordered list of handlers where each handler can process or pass to `next`, with explicit chain construction
- **medium** -- middleware registration with `use()`/`add()` and `next()` callback convention
- **low** -- if/else cascade where each branch handles a specific case (degenerate chain)

## Architecture

Look for correct chain traversal: each handler decides to process, pass through, or short-circuit.

### Review Checklist

- Each handler has a single responsibility and clear criteria for when it processes vs passes
- Chain order is intentional and documented (auth before validation before business logic)
- A request that no handler processes is handled explicitly (default/fallback handler at end)
- Handlers do not modify the request in ways that break downstream handlers
- Chain can be reconfigured without modifying individual handlers
- Short-circuit behavior (early return) is well-defined and tested

### Anti-patterns

- Handlers that silently swallow requests without calling next (request disappears)
- Order-dependent handlers with no documentation of required ordering
- Chain with no termination -- request falls through without any handler processing it
- Handlers with circular references causing infinite loops

---
description: Change Data Capture (CDC) architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [data, integration]
---
# Change Data Capture (CDC)

## Recognition

How to identify this pattern in code.

### Signatures

- Database log tailing (WAL, binlog, oplog)
- Debezium connector configurations
- WAL readers (`wal2json`, `pgoutput`, `test_decoding`)
- Binlog consumers (Maxwell, Canal)
- `source.connector.class=io.debezium` in connector configs
- Outbox table polling as a CDC alternative
- Event sourcing derived from database changes rather than application events

### Confidence

- **high** -- Debezium connector config or WAL/binlog reader setup with downstream event publishing
- **medium** -- Outbox table with a polling mechanism or trigger-based change capture
- **low** -- Database triggers that write to a separate events table without explicit CDC framing

## Architecture

Look for database change streams being captured and published as events to downstream consumers.

### Review Checklist

- CDC connector tracks its position (LSN/offset) durably to survive restarts without data loss
- Schema evolution is handled (schema registry or compatible deserialization)
- Ordering guarantees are preserved per-key/per-table through the pipeline
- Tombstone/delete events are propagated correctly, not silently dropped
- Connector lag is monitored with alerts for growing replication delay
- Snapshot strategy is defined for initial load and connector recovery

### Anti-patterns

- Polling the source table with timestamps instead of using the database log (misses deletes, has clock skew)
- No schema evolution strategy, causing downstream deserialization failures on ALTER TABLE
- Ignoring connector offset management, leading to duplicate or lost events on restart
- Capturing all tables indiscriminately instead of targeting specific tables that need change events

---
description: Chatty API anti-pattern
type: anti-pattern
graphable: false
---
# Chatty API

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Client making 10+ sequential API calls to assemble a single view or page
- No batch or bulk endpoints for operations that naturally apply to collections
- No GraphQL or aggregation layer despite clients needing data from multiple resources per screen
- N HTTP requests required to display N items (fetching details one by one)
- Frontend code orchestrating multiple backend calls and merging responses client-side

### Confidence

- **high** -- network tab or client code shows 10+ sequential requests to the same API for a single user action
- **medium** -- API provides only single-resource endpoints and the client loops over IDs to fetch related data
- **low** -- API lacks batch endpoints but current usage patterns fetch only a few items at a time

## Impact

Latency multiplies with each additional call, creating fragile client logic tightly coupled to backend resource structure.

### Symptoms

- Page load times are dominated by network round-trips rather than server processing
- Mobile clients suffer disproportionately due to higher per-request latency
- Client code contains complex orchestration logic to sequence, merge, and error-handle multiple API calls
- A single slow or failing backend call breaks the entire page because the client depends on all responses
- API rate limits are hit quickly because a single user action generates many requests

### Remediation

- Introduce batch/bulk endpoints that accept arrays of IDs and return aggregated results in one response
- Add a Backend-for-Frontend (BFF) layer that composes multiple service calls into a single client-facing response
- Consider GraphQL or a query-based API that lets clients request exactly the data they need in one round-trip
- Implement server-side view models or aggregation endpoints tailored to specific UI screens
- Combine related resources into composite responses with embedded or sideloaded associations

---
description: Choreography architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [integration, architectural]
---
# Choreography


## Recognition

How to identify this pattern in code.

### Signatures

- Event-based service communication without a central orchestrator or saga coordinator
- `EventBus` usage (Guava, Vert.x, or custom) for in-process event dispatch
- `@EventListener` annotations (Spring) for reacting to published domain events
- SNS/SQS fan-out topology where services publish events and others subscribe independently
- Kafka topic-to-topic chaining where each service consumes from one topic and produces to another
- NATS subjects used for decoupled pub/sub communication between services
- Absence of `Saga`, `Orchestrator`, or `Workflow` classes coordinating multi-service flows

### Confidence

- **high** -- multiple services communicating exclusively through events with no orchestrator, correlation IDs propagated, and event schemas versioned
- **medium** -- event-driven communication present but some services also use synchronous calls, or event flow is partially orchestrated
- **low** -- pub/sub infrastructure in use but event contracts are implicit and no correlation ID tracing exists

## Architecture

Look for clear event contracts and no hidden coupling between services.

### Review Checklist

- Event schemas are versioned and documented — consumers know what to expect
- Each service can be deployed independently without breaking the chain
- Event flows are traceable end-to-end (correlation IDs in every event)
- Failure in one service does not silently stall the entire workflow

### Anti-patterns

- Implicit ordering assumptions — Service B assumes A always fires first
- Event ping-pong — two services triggering each other in a loop
- No observability — impossible to reconstruct what happened from logs alone
- Choreography used where a saga/orchestrator would be clearer (too many steps)

---
description: Circuit Breaker architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [resilience, integration]
---
# Circuit Breaker


## Recognition

How to identify this pattern in code.

### Signatures

- `resilience4j` with `CircuitBreaker` and `CircuitBreakerConfig` classes (Java)
- `pybreaker` library usage (`CircuitBreaker` class, `@circuit` decorator) in Python
- `polly` with `CircuitBreakerPolicy` in .NET applications
- Hystrix `HystrixCommand` with circuit breaker configuration (legacy Java)
- Istio `DestinationRule` with `outlierDetection` settings in service mesh configuration
- `opossum` circuit breaker library in Node.js applications
- `tenacity` with stop conditions and retry state tracking (Python)

### Confidence

- **high** -- explicit circuit breaker library with configured thresholds, state transitions (closed/open/half-open), and fallback behavior
- **medium** -- retry logic with failure counting and a threshold that disables calls, but no formal state machine or half-open probing
- **low** -- try/catch around external calls with manual error counting but no automatic state transitions or recovery mechanism

## Architecture

Look for correct state machine implementation: closed -> open -> half-open.

### Review Checklist

- Failure threshold and recovery timeout are configurable, not hardcoded
- Half-open state allows a limited number of probe requests
- Circuit state is observable (logging or metrics on state transitions)
- Fallback behavior is explicitly defined (not silent swallowing)

### Anti-patterns

- Wrapping every call in a circuit breaker (only external dependencies need them)
- No fallback — circuit opens and the caller gets raw exceptions
- Shared circuit state across unrelated dependencies

---
description: Circular Dependency anti-pattern
type: anti-pattern
graphable: false
---
# Circular Dependency

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Module A imports module B which imports module A (direct cycle)
- Transitive cycles: A imports B, B imports C, C imports A
- `ImportError` or `AttributeError` at runtime due to partially initialized modules
- `from __future__ import annotations` used specifically to break import cycles
- `TYPE_CHECKING` blocks (`if TYPE_CHECKING: import ...`) to separate runtime from type-time imports
- Deferred imports inside function bodies to avoid top-level circular references
- Build tools reporting dependency cycle warnings

### Confidence

- **high** -- direct A-imports-B-imports-A cycle, runtime ImportError traced to circular imports, function-level imports with comments explaining the cycle
- **medium** -- `TYPE_CHECKING` imports or `from __future__ import annotations` used to work around import issues, transitive cycles visible in dependency graphs
- **low** -- modules that seem conceptually intertwined and might form cycles under future changes

## Impact

Creates fragile import ordering, makes modules impossible to test or refactor independently, and causes mysterious runtime failures.

### Symptoms

- Import order matters: rearranging imports or moving code between files causes runtime crashes
- Unit testing a single module pulls in a chain of unrelated modules
- Refactoring one module forces changes in its cycle partners
- IDE tooling and static analysis struggle to resolve types across the cycle
- New developers encounter confusing errors when adding imports that close a cycle

### Remediation

- Extract the shared concepts into a new module that both sides depend on (dependency inversion)
- Use interfaces or protocols: depend on abstractions rather than concrete implementations
- Apply the Dependency Inversion Principle: high-level modules define interfaces, low-level modules implement them
- Merge tightly coupled modules if they truly represent one concept split artificially
- Use dependency graph visualization tools to detect and monitor cycles in CI

---
description: Claim Check architectural pattern
type: pattern
testable: true
distributed: true
graphable: true
abstraction: [integration, messaging]
---
# Claim Check

## Recognition

How to identify this pattern in code.

### Signatures

- Large payload stored in blob or object storage before sending a message
- Message body contains a reference/URL instead of the full payload
- `s3://` or `gs://` or `az://` references embedded in message fields
- Download-on-consume pattern where the consumer fetches data by reference
- Payload size threshold triggering offload to external storage
- Separate upload and notify steps in producer code
- Claim token or reference ID passed through the message bus

### Confidence

- **high** -- explicit size-check logic that offloads to object storage and replaces payload with a reference
- **medium** -- messages contain storage URLs but no explicit size threshold or offload logic visible
- **low** -- large blob references in messages but could be a normal file-sharing workflow rather than intentional claim check

## Architecture

Look for payload offloading to external storage with reference-based message passing.

### Review Checklist

- Size threshold for offloading is configurable and documented
- References include enough metadata to retrieve the payload (bucket, key, version)
- Consumers handle both inline payloads and claim-check references transparently
- Stored payloads have a retention/expiration policy to avoid orphaned blobs
- Access control on the storage matches the message consumer's permissions

### Anti-patterns

- No cleanup -- offloaded payloads accumulate indefinitely in storage
- Consumer assumes all messages are inline and crashes on references
- Reference points to storage the consumer cannot access (permission mismatch)
- No fallback for storage unavailability -- producer fails entirely instead of degrading

---
description: Command architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Command

## Recognition

How to identify this pattern in code.

### Signatures

- Classes with `execute()`, `run()`, `do()` methods, often paired with `undo()` or `rollback()`
- Command queue, command history, or command stack structures
- Classes ending in `Command`, `Action`, `Operation`, `Task`
- Undo/redo functionality with a history list of executed commands
- Python: command objects with `__call__` or `execute()`, `cmd` module patterns
- JS/TS: action objects in Redux/Flux, command classes with `execute()`/`undo()`
- Go: structs implementing a `Command` interface with `Execute()` method

### Confidence

- **high** -- command objects with both `execute()` and `undo()`, stored in a history stack
- **medium** -- objects encapsulating an operation with `execute()` method, queued for later execution
- **low** -- action/event objects dispatched to a handler (overlaps with event sourcing)

## Architecture

Look for proper encapsulation of operations as objects, enabling queuing, logging, and undo.

### Review Checklist

- Commands are self-contained (carry all parameters needed for execution)
- Undo restores state completely (not just partially reverting)
- Command history has bounded size to prevent unbounded memory growth
- Commands are serializable if they need to cross process boundaries or be persisted
- Invoker is decoupled from concrete command types

### Anti-patterns

- Commands that reach into global state instead of carrying their own parameters
- Undo that only works if commands are undone in exact reverse order (fragile)
- Bloated command objects containing business logic that belongs in a service
- Command queue with no error handling or dead-letter mechanism for failed commands

---
description: Competing Consumers architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [messaging, concurrency]
---
# Competing Consumers

## Recognition

How to identify this pattern in code.

### Signatures

- Multiple consumers reading from the same queue or topic partition
- Consumer groups: Kafka `group.id`, RabbitMQ multiple consumers on one queue
- Partition assignment and rebalancing logic
- Load balancing across consumers: round-robin, least-connections, or partition-based
- Concurrency configuration: `concurrency=N`, `prefetch_count`, `maxConcurrentConsumers`
- SQS with multiple readers, Celery worker pool, Sidekiq processes
- Auto-scaling consumer count based on queue depth

### Confidence

- **high** -- consumer group configuration with partition assignment and rebalance handling
- **medium** -- multiple worker processes or threads consuming from the same queue
- **low** -- horizontally scaled service instances that each poll the same data source

## Architecture

Look for multiple consumer instances sharing the workload of a single queue or topic, with each message processed by exactly one consumer.

### Review Checklist

- Message processing is idempotent (rebalancing may cause redelivery)
- Consumer rebalancing is handled gracefully (in-progress work is not lost)
- Prefetch/batch size is tuned to balance throughput and fairness
- Partition count or queue configuration supports the desired parallelism
- Consumer lag is monitored per consumer group
- Ordering guarantees are maintained within partitions where required

### Anti-patterns

- Assuming strict ordering across all messages when consumers process in parallel
- No rebalance listener, causing duplicate processing during consumer group changes
- All consumers configured with the same partition affinity (no actual distribution)
- Scaling consumers beyond the partition count (idle consumers with no work)

---
description: Component Slot — parent-controlled content injection into child components
type: pattern
graphable: false
abstraction: [frontend, design]
---
# Component Slot

## Recognition

How to identify this pattern in code.

### Signatures

- `children` prop for content projection and `Slot` component from Radix/headless libraries (React)
- `v-slot`, `<template #name>`, named and scoped slots with slot props (Vue)
- `<ng-content>`, `ContentChild`, `ContentChildren`, `select` attribute for named projection (Angular)
- `<slot>` element with `name` attribute and `let:` directive for passing data back (Svelte)
- Render props pattern: `render` or `children` as a function receiving data from the child (React)
- Compound components: `Select.Root`, `Select.Trigger`, `Select.Content` (Radix, Headless UI)
- `React.cloneElement` or `React.Children.map` for augmenting projected children
- Default slot content with fallback: `<slot>fallback</slot>`, `{children ?? <Default />}`
- `as` or `asChild` prop for polymorphic rendering (Radix, styled-components)

### Confidence

- **high** -- Framework slot API (v-slot, ng-content, Svelte slot) or explicit children/render prop pattern with named slots and scoped data passing
- **medium** -- Component accepts a `children` prop or render function and places it in its output, but without named slots or scoped data
- **low** -- Component renders arbitrary content via props (like a `label` string prop) but without true content projection

## Architecture

Look for a component that defines insertion points where parent-provided content is rendered, enabling flexible composition without the child dictating the content.

### Review Checklist

- Slots have meaningful names when a component has multiple insertion points
- Scoped slots or render props provide only the data the parent needs, not the entire internal state
- Default slot content is provided for optional slots so the component works standalone
- TypeScript types or PropTypes define the expected shape of render props and scoped slot data
- Compound component context is properly scoped so nested sub-components do not leak state
- Slot content is not deeply coupled to the child's internal DOM structure

### Anti-patterns

- Passing complex JSX through regular props (like `header={<div>...</div>}`) instead of using slots or children for content projection
- Scoped slots that expose too much internal state, creating tight coupling between parent and child
- Using `React.cloneElement` to inject props into arbitrary children without type safety
- Compound components without context, requiring specific DOM nesting order that breaks when rearranged
- Overusing render props when simple children composition would suffice

---
description: Component Architecture architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design, frontend]
---
# Component Architecture

## Recognition

How to identify this pattern in code.

### Signatures

- Self-contained UI components with props/state, composed into a tree
- `render()`, `template`, or JSX/TSX returning UI markup from component logic
- Component files: `.jsx`, `.tsx`, `.vue`, `.svelte`, or `@Component` decorators
- Props passed down, events emitted up (unidirectional data flow within the tree)
- Libraries: React, Vue, Svelte, Angular components, Web Components (`customElements.define`)

### Confidence

- **high** -- Framework component files with explicit props interface, local state, and render function
- **medium** -- Reusable UI modules with encapsulated markup and behavior, but no formal component framework
- **low** -- Any UI code organized into isolated, composable pieces with some form of data passing

## Architecture

Look for a tree of self-contained, composable UI components with clear data flow through props and events.

### Review Checklist

- Components have a single responsibility -- not doing data fetching, rendering, and business logic in one component
- Props interface is explicit and typed (PropTypes, TypeScript interfaces, or equivalent)
- State is owned by the appropriate component -- lifted only when necessary for sibling communication
- Side effects (API calls, subscriptions) are isolated in lifecycle hooks or dedicated hooks/composables
- Components are reusable -- no hardcoded parent-specific assumptions

### Anti-patterns

- God components with hundreds of lines mixing data fetching, state management, and rendering
- Prop drilling through many levels instead of using context/provide-inject or state management
- Direct DOM manipulation bypassing the component framework's rendering cycle
- Tightly coupled components that import and reference each other's internal state

---
description: Composite architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Composite

## Recognition

How to identify this pattern in code.

### Signatures

- Tree structures where leaves and containers share the same interface
- `children` list or collection on composite nodes
- Recursive `render()`, `execute()`, `accept()`, or `calculate()` methods
- File system tree implementations (files and directories as same type)
- UI widget trees (containers holding other widgets)
- Menu hierarchies with nested submenus
- `Component` base class/interface with `Leaf` and `Composite` subclasses

### Confidence

- **high** -- Shared interface with `children` collection on composite nodes and recursive operation delegation to children
- **medium** -- Tree structure with uniform operations on nodes but without an explicit component interface
- **low** -- Nested data structures with recursive processing that resemble but do not formally implement the pattern

## Architecture

Look for a uniform interface applied to both individual objects and compositions, enabling recursive tree operations.

### Review Checklist

- Leaf and composite nodes implement the same interface consistently
- Add/remove child operations are only meaningful on composite nodes (not exposed on leaves, or safely no-op)
- Recursive operations have a clear base case at the leaf level
- Tree depth is bounded or guarded against stack overflow in recursive traversals
- Parent references, if present, are maintained consistently on add/remove

### Anti-patterns

- Leaf nodes exposing child-management methods that throw at runtime
- No depth limit on recursive operations, risking stack overflow on deep trees
- Type-checking nodes to determine leaf vs composite instead of relying on polymorphism
- Mutable shared state in the tree that causes unintended side effects during traversal

---
description: Configuration Management architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [infrastructure, lifecycle]
---
# Configuration Management

## Recognition

How to identify this pattern in code.

### Signatures

- 12-factor config via environment variables (`os.environ`, `process.env`, `std::env`)
- Config files in YAML, TOML, JSON, or INI format (`config.yaml`, `settings.toml`)
- Config server or centralized config service (Spring Cloud Config, etcd, Consul KV)
- `settings.py`, `config.py`, `application.yml`, `.env` files with `dotenv` loading
- Feature toggles and feature flag systems (`LaunchDarkly`, `Unleash`, custom flags)
- Hierarchical config with overrides (default -> environment -> instance)
- Config validation at startup with fail-fast on missing required values

### Confidence

- **high** -- Structured config loading with environment-specific overrides, validation at startup, and no hardcoded values in business logic
- **medium** -- Environment variables or config files loaded at startup but without formal validation or override hierarchy
- **low** -- Scattered hardcoded constants with some values extracted to a config file as an afterthought

## Architecture

Look for config separated from code, loaded once at startup, validated early, and injected into components rather than globally accessed.

### Review Checklist

- All environment-specific values are externalized (no hardcoded URLs, ports, or credentials in code)
- Config is validated at startup -- missing or malformed values cause a clear failure, not a runtime surprise
- Override hierarchy is well-defined (defaults < environment < instance < explicit overrides)
- Secrets are handled separately from plain config (not in the same config file)
- Config changes can be applied without code changes or redeployment where appropriate
- Feature flags have a defined lifecycle (creation, rollout, cleanup after full adoption)

### Anti-patterns

- Secrets stored in plain config files alongside non-sensitive configuration
- No validation -- missing config values cause cryptic runtime errors instead of startup failures
- Config scattered across multiple mechanisms (env vars, files, hardcoded) with no clear precedence
- Feature flags that never get cleaned up, accumulating as permanent conditional branches

---
description: Configuration Sprawl anti-pattern
type: anti-pattern
graphable: false
---
# Configuration Sprawl

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Config values spread across environment variables AND yaml files AND code constants AND database settings
- No single source of truth for configuration: same logical setting defined in 3+ places
- Same configuration key appears in multiple files with potentially different values
- Config key typos cause silent failures because there is no schema or validation
- Startup code pulls configuration from multiple unrelated sources with no unified loader

### Confidence

- **high** -- the same logical setting (e.g., database URL, timeout value) is defined in 3+ distinct sources with no clear precedence order
- **medium** -- configuration is loaded from 2+ sources (env vars, config file, code defaults) with ad-hoc precedence logic scattered across modules
- **low** -- configuration exists in one primary source but a few hardcoded fallback values in code shadow the intended settings

## Impact

Inconsistent behavior across environments because no one knows which configuration source actually wins.

### Symptoms

- Changing a config value in one place has no effect because another source overrides it
- Different environments behave differently despite "identical" deployments because config sources vary
- Debugging requires checking env vars, config files, database rows, and code defaults to find the effective value
- New team members cannot determine where to change a setting without reading all config-loading code
- Outages caused by config key typos that silently fell back to default values

### Remediation

- Establish a single configuration loader that reads from sources in a documented, deterministic precedence order
- Validate all configuration at startup with a schema that fails fast on missing or invalid values
- Eliminate duplicate definitions: each setting is defined in exactly one canonical source
- Use typed configuration objects that centralize all settings with default values and validation in one module
- Add integration tests that verify configuration loading produces expected values for each environment

See also: config-management pattern

---
description: Connection Pooling architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [infrastructure]
---
# Connection Pooling

## Recognition

How to identify this pattern in code.

### Signatures

- `pool_size`, `max_connections`, `min_idle` configuration parameters
- `SQLAlchemy create_engine(pool_size=)` (Python)
- `HikariCP` configuration (`maximumPoolSize`, `minimumIdle`) (Java)
- `pgBouncer` or `PgPool` as external connection pooler (PostgreSQL)
- `redis.ConnectionPool` or `redis.BlockingConnectionPool` (Python/Redis)
- `http.Agent({keepAlive: true, maxSockets:})` (Node.js)
- Connection checkout/checkin lifecycle in application code
- Pool exhaustion handling (`pool_timeout`, `QueuePool` overflow settings)

### Confidence

- **high** -- explicit pool configuration with size limits, idle management, and health checks on pooled connections
- **medium** -- pool is configured via framework defaults but pool size and timeout are not explicitly tuned
- **low** -- connections are reused implicitly by a library but no pool configuration is visible in the codebase

## Architecture

Look for bounded, reusable connection pools with health checks and proper lifecycle management.

### Review Checklist

- Pool size is tuned for the workload -- not left at framework defaults
- Idle connections are cleaned up to avoid holding resources unnecessarily
- Connection health is validated before checkout (test-on-borrow or background validation)
- Pool exhaustion behavior is defined (block with timeout, reject, or overflow)
- Connections are always returned to the pool -- no leaks from unclosed connections in error paths
- Pool metrics are exposed (active, idle, waiting, timeout counts)

### Anti-patterns

- Creating a new connection per request instead of pooling
- Pool size set to match max concurrent users (overprovisioned, exhausting DB connection limits)
- No connection validation -- stale or broken connections handed to callers
- Missing connection return in error paths -- pool drains under sustained errors

---
description: Content/Protocol Negotiation architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [api]
---
# Content/Protocol Negotiation

## Recognition

How to identify this pattern in code.

### Signatures

- `Accept` and `Content-Type` HTTP headers used for format selection
- `produces` and `consumes` annotations on API endpoints (JAX-RS, Spring)
- Format selection logic dispatching between JSON, XML, protobuf, or other serializations
- API versioning via `Accept-Version`, `Accept: application/vnd.api.v2+json`, or URL path segments
- Media type routing: `application/json`, `application/xml`, `application/protobuf`
- `406 Not Acceptable` or `415 Unsupported Media Type` error responses
- Content negotiation middleware or request interceptors
- `Vary: Accept` response header for cache correctness

### Confidence

- **high** -- Explicit `Accept`/`Content-Type` handling with multiple format serializers and `406`/`415` responses
- **medium** -- API version headers or vendor media types with format-specific serialization
- **low** -- Single format API that sets `Content-Type` without any negotiation logic

## Architecture

Look for correct format dispatch based on client preferences with proper error responses for unsupported types.

### Review Checklist

- All supported media types are explicitly declared, not inferred
- Unsupported `Accept` types return `406 Not Acceptable` with a list of supported types
- Unsupported `Content-Type` on requests returns `415 Unsupported Media Type`
- `Vary: Accept` header is set on responses to prevent cache poisoning
- Default format is defined for requests without an `Accept` header
- API versioning strategy is consistent (header-based, URL-based, or media type -- not mixed)

### Anti-patterns

- Silently ignoring the `Accept` header and always returning JSON
- Missing `Vary` header causing CDN or proxy caches to serve wrong formats
- Mixing version negotiation strategies across endpoints (some URL-based, some header-based)
- Supporting content types that are never tested or documented

---
description: Contract Testing architectural pattern
type: pattern
testable: true
distributed: true
graphable: true
abstraction: [testing, integration]
---
# Contract Testing

## Recognition

How to identify this pattern in code.

### Signatures

- Pact files (`.json` contracts) in a `pacts/` or `contracts/` directory
- `@Pact`, `@PactVerification` annotations in Java/Kotlin tests
- `pact-jvm`, `pact-js`, `pact-python`, `pact-go` library imports
- Consumer-driven contract definitions with `interaction()` or `upon_receiving()`
- Provider verification test suites that replay contracts against a running service
- Contract broker configuration (Pact Broker URL, publish/verify steps in CI)
- Spring Cloud Contract DSL files (`.groovy` or `.yml` stubs)

### Confidence

- **high** — Pact contract files present with both consumer-side generation and provider-side verification tests
- **medium** — Contract broker configured in CI but only one side (consumer or provider) has tests
- **low** — API schema validation (OpenAPI) in tests without explicit consumer-driven contracts

## Architecture

Look for bidirectional contract verification: consumers define expectations, providers verify against them.

### Review Checklist

- Consumer tests generate contracts that are published to a broker or shared artifact store
- Provider verification tests run against the latest contracts from all consumers
- Contract versions are tied to git commits or semantic versions for traceability
- Breaking changes are caught before deployment via CI contract checks (can-i-deploy gates)
- Contracts cover error responses and edge cases, not just happy paths
- Provider states are set up explicitly so verification runs against realistic conditions

### Anti-patterns

- Only testing the happy path in contracts, missing error and edge-case interactions
- Contracts maintained manually instead of generated from consumer tests
- Provider verification skipped in CI, running only locally
- Tight coupling in contracts that specify implementation details (exact headers, timestamps) instead of semantic content

---
description: Conversation threading pattern for messaging and real-time communication
type: pattern
category: domain-model
abstraction: [data, communication]
---
# Conversation Thread

## Recognition

How to identify this pattern in code.

### Signatures

- `Message`, `Thread`, `Conversation` model classes with parent-child relationships
- `reply_to`, `parent_message_id`, `thread_id` foreign keys linking messages
- `Reaction`, `reaction`, `emoji` models attached to messages
- `read_receipt`, `ReadReceipt`, `last_read_at`, `seen_by` read state tracking
- `Channel`, `channel_id`, `Room` grouping constructs for message streams
- Python: `channels`, message models with `sender`, `content`, `thread` fields
- JS/TS: `socket.io` or WebSocket handlers for real-time message delivery, `stream-chat`
- Go: message structs with `ThreadID`, `ParentID`, WebSocket hub for broadcasting
- Rust: message types with `reply_to: Option<MessageId>`, async channel for delivery
- Java: `@Entity Message` with `@ManyToOne` thread relationship, STOMP/WebSocket messaging

### Confidence

- **high** -- Thread/Message hierarchy with reply_to references, real-time delivery via WebSocket, read receipts, and reactions on messages
- **medium** -- Message model with conversation grouping and reply chains but polling-based delivery
- **low** -- Simple comment list without threading, real-time delivery, or read state management

## Architecture

### When to use
- Chat and messaging features where users converse in threads or channels
- Comment systems with threaded replies and nested discussions
- Customer support systems with conversation history and agent assignment

### Anti-patterns
- Polling for new messages instead of using WebSocket or SSE for real-time delivery
- Unbounded thread depth without pagination, causing query and rendering performance issues
- Storing read state per-message-per-user in a flat table, which grows as O(messages * users)

### Complements
- [websocket](/concepts/websocket) — real-time message delivery uses WebSocket connections
- [pub-sub](/concepts/pub-sub) — message distribution across channels follows pub/sub patterns
- [pagination](/concepts/pagination) — message history requires cursor-based pagination for infinite scroll

## Impact

Conversation threading combines data modeling complexity with real-time delivery requirements. Read state tracking creates significant storage and query pressure at scale, and message ordering guarantees affect both user experience and system design for distributed deployments.

---
description: Copy-Paste Programming anti-pattern
type: anti-pattern
graphable: false
---
# Copy-Paste Programming

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Identical or near-identical code blocks in multiple files
- Duplicated error handling logic with minor variations across modules
- Same regex, validation, or transformation logic in 3+ places
- `# copied from X` or `// TODO: deduplicate` comments
- Functions with the same name or signature in different modules doing essentially the same thing
- Test files with large blocks of duplicated setup code

### Confidence

- **high** -- two or more code blocks of 10+ lines are textually identical or differ only in variable names, confirmed by clone detection tools or diff comparison
- **medium** -- the same business rule, validation regex, or error handling pattern appears in 3+ locations with minor variations
- **low** -- functions in different modules perform similar transformations with different implementations, or `# copied from` comments exist in the codebase

## Impact

Bugs fixed in one copy but not others, leading to inconsistent behavior and a maintenance burden that scales with the number of duplicates.

### Symptoms

- A bug fix applied in one location does not resolve the same bug in duplicated code elsewhere
- Behavior diverges between features that should work identically
- Code reviews repeatedly flag "this exists elsewhere" but deduplication never happens
- Refactoring one module requires hunting for and updating all copies
- Test coverage appears high but is redundant, testing the same logic multiple times

### Remediation

- Extract duplicated logic into a shared function, module, or utility library
- Use parameterization or configuration to handle variations between the copies instead of separate code paths
- Run clone detection tools (jscpd, PMD CPD, Simian) in CI to prevent new duplication from being merged
- Apply the Rule of Three: tolerate minor duplication up to two occurrences, extract on the third
- For duplicated test setup, use fixtures, factories, or shared test helpers

---
description: Correlation ID architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [observability, integration]
---
# Correlation ID

## Recognition

How to identify this pattern in code.

### Signatures

- Request ID generation: `uuid4()`, `ulid()`, `nanoid()` for unique correlation IDs
- Header propagation: `X-Request-ID`, `X-Correlation-ID` headers on HTTP requests
- Middleware extracting or generating request IDs on incoming requests
- Structured logging with bound context: `structlog.bind(request_id=...)`, log correlation fields
- Logging context injection: `MDC.put("correlationId", id)` (Java), `contextvars` (Python)

### Confidence

- **high** -- Middleware generates/extracts correlation ID, propagates it in headers to downstream calls, and binds it to all log entries
- **medium** -- request ID header generated and logged but not propagated to downstream service calls
- **low** -- unique IDs in logs but no structured propagation or trace header handling

## Architecture

Look for consistent ID propagation across all service boundaries with structured logging that includes the correlation ID.

### Review Checklist

- Every incoming request gets a correlation ID (generated if not present, propagated if provided)
- ID is propagated to all downstream calls (HTTP headers, message queue metadata, gRPC metadata)
- Structured logs include the correlation ID in every log entry for the request lifecycle
- Correlation ID is searchable across all services in log aggregation

### Anti-patterns

- Generating a new ID at each service instead of propagating the original (breaks cross-service correlation)
- Logging the correlation ID only at entry and exit points, not in intermediate operations
- Propagating IDs in HTTP headers but not in async message payloads (losing correlation at queue boundaries)

See also: distributed-tracing

---
description: CORS architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [security, api]
---
# CORS (Cross-Origin Resource Sharing)

## Recognition

How to identify this pattern in code.

### Signatures

- `Access-Control-Allow-Origin` response headers
- CORS middleware in the HTTP pipeline (`flask-cors`, `cors()` in Express, `@CrossOrigin` in Spring)
- Preflight `OPTIONS` request handling
- `allowed_origins`, `allow_methods`, `allow_headers` configuration
- `Access-Control-Allow-Credentials: true` for cookie-based auth
- Origin whitelist or regex matching logic
- `Vary: Origin` header in responses

### Confidence

- **high** -- explicit CORS middleware with a configured origin allowlist and preflight handling
- **medium** -- CORS headers present but using wildcard `*` origin without credential restrictions
- **low** -- scattered `Access-Control-*` headers set manually in individual route handlers

## Architecture

Look for centralized CORS policy enforcement with explicit origin allowlisting.

### Review Checklist

- Origins are explicitly allowlisted -- no wildcard `*` when credentials are enabled
- CORS configuration is centralized in middleware, not scattered across handlers
- Preflight `OPTIONS` requests are handled correctly with appropriate cache headers
- `Access-Control-Max-Age` is set to reduce preflight request frequency
- Allowed methods and headers are restricted to what the API actually uses

### Anti-patterns

- `Access-Control-Allow-Origin: *` combined with `Access-Control-Allow-Credentials: true`
- Reflecting the request Origin header back without validation (open relay)
- CORS headers set inconsistently across different endpoints
- No `Vary: Origin` header causing incorrect caching of CORS responses

---
description: CQRS architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [architectural, data]
---
# CQRS


## Recognition

How to identify this pattern in code.

### Signatures

- Separate `CommandHandler` and `QueryHandler` classes or interfaces
- `@CommandHandler` and `@QueryHandler` annotations (Axon Framework)
- MediatR `IRequest<T>` and `IRequestHandler<TRequest, TResponse>` with distinct command/query request types (.NET)
- Separate read and write repository interfaces (e.g., `WriteRepository`, `ReadRepository` or `CommandStore`, `QueryStore`)
- Separate database connections or data sources for read operations vs write operations

### Confidence

- **high** -- explicit command/query separation with distinct handlers, separate read/write stores, and a projection or sync mechanism between them
- **medium** -- separate handler classes for reads and writes but both using the same underlying database or store
- **low** -- read-heavy endpoints using a cache or materialized view alongside a primary write store, but no formal command/query separation in code

## Architecture

Look for strict separation between write and read paths with an explicit sync mechanism.

### Review Checklist

- Commands mutate only the write model — no direct writes to the read store
- Queries read only from the read model — never from the write store
- Projection/sync mechanism is explicit and observable (not ad-hoc cache fills)
- Eventual consistency is documented and acceptable for the use case
- Read model can be rebuilt from scratch (replayable projections)

### Anti-patterns

- Read path sneaking writes back into the write model
- No clear sync mechanism — read model silently drifts from write model
- Applying CQRS where a single model would suffice (unnecessary complexity)

---
description: Data Mapper architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design, data]
---
# Data Mapper

## Recognition

How to identify this pattern in code.

### Signatures

- Separate mapper classes that transfer data between domain objects and database rows
- Domain models have zero persistence logic (no `save()`, no `query()`)
- Explicit mapping functions: `to_entity()`, `from_row()`, `map_to_model()`
- SQLAlchemy classical mapping: `mapper()` calls separate from model definitions
- TypeORM entity decorators with repository pattern alongside
- Dedicated `mappers/` directory or mapping configuration files
- Domain objects are plain classes or dataclasses with no ORM base class

### Confidence

- **high** -- domain models are plain objects and a separate mapper handles all persistence translation
- **medium** -- ORM entities exist but domain logic uses separate DTOs or value objects mapped from them
- **low** -- mapping functions exist but domain objects still inherit from an ORM base

## Architecture

Look for domain models completely decoupled from the database, with an explicit mapping layer in between.

### Review Checklist

- Domain objects have no import of any ORM or database library
- Mapper handles both directions: domain-to-persistence and persistence-to-domain
- Complex relationships (aggregates, value objects) are mapped correctly, not flattened
- Mapper is tested independently with both domain and persistence fixtures
- Schema changes require mapper updates but never domain model changes

### Anti-patterns

- Domain objects importing or inheriting from ORM classes (mapper becomes pointless)
- Mapper that simply copies fields 1:1 with no structural difference (unnecessary indirection)
- Mapping logic scattered across services instead of centralized in mapper classes
- Leaking database column names into the domain model vocabulary

---
description: Data pipeline flow — linear transformation stages from source to sink
type: flow-shape
abstraction: [data, integration]
---
# Data Pipeline

## Recognition

### Signatures

- ETL/ELT patterns: extract → transform → load
- Airflow DAGs, Prefect flows, Dagster pipelines, Luigi tasks
- Spark jobs with `read` → `filter` → `map` → `groupBy` → `write` chain
- dbt models with `ref()` dependencies forming a DAG
- Pandas/Polars DataFrames with chained transformations
- Kafka Streams `topology.addSource().addProcessor().addSink()`
- Step Functions or workflow engine with sequential stages
- Source → staging → cleaned → enriched → target table progression
- Batch job schedulers (cron, k8s CronJob) triggering data processing

### Confidence

- **high** — explicit pipeline framework (Airflow, dbt, Spark) with defined stages and dependencies
- **medium** — sequential data transformations with clear source → sink but no pipeline framework
- **low** — ad-hoc scripts that read, transform, and write data without pipeline structure

---
description: Database Migration architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [lifecycle, data]
---
# Database Migration

## Recognition

How to identify this pattern in code.

### Signatures

- Versioned migration files: numbered or timestamped scripts (`001_create_users.sql`, `V2__add_index.sql`)
- Migration frameworks: `alembic` (Python), `flyway` (Java/JVM), `knex migrate` (Node), `django migrate`, `golang-migrate`, `dbmate`, `liquibase`
- Up/down functions: `def upgrade()` / `def downgrade()`, `exports.up` / `exports.down`
- Migration runner commands: `alembic upgrade head`, `flyway migrate`, `knex migrate:latest`
- `ALTER TABLE`, `CREATE TABLE`, `DROP TABLE` in numbered or versioned scripts
- Schema version tracking table: `alembic_version`, `flyway_schema_history`, `schema_migrations`
- Migration generation commands: `alembic revision --autogenerate`, `knex migrate:make`

### Confidence

- **high** -- migration framework configured with versioned up/down scripts and a schema version tracking table
- **medium** -- numbered SQL files exist in a migrations directory but no framework manages execution order
- **low** -- ad-hoc `ALTER TABLE` statements in deployment scripts without versioning or rollback support

## Architecture

Look for versioned, reversible schema changes managed by a migration framework with a clear execution order and rollback path.

### Review Checklist

- Every schema change is a versioned migration file -- no manual DDL against production
- Migrations are backward-compatible: old application code can run against the new schema during rolling deployments
- Down/rollback migrations are implemented and tested, not left as stubs
- Migrations run in a transaction where the database supports transactional DDL
- Large table migrations use online DDL or batched operations to avoid locking
- Migration execution is idempotent -- running the same migration twice does not fail or corrupt state

### Anti-patterns

- Schema changes applied directly to production without migration files
- Migrations that break backward compatibility (dropping columns still referenced by running code)
- No rollback path -- down migrations are empty or missing entirely
- Coupling data migrations with schema migrations in the same file (mixing DDL and bulk DML)

---
description: Domain-Driven Design architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [architectural, design]
---
# Domain-Driven Design (DDD)


## Recognition

How to identify this pattern in code.

### Signatures

- `Entity`, `ValueObject`, or `AggregateRoot` base classes or interfaces in domain layer
- `DomainEvent` classes published from aggregate operations
- `Repository` interfaces defined in the domain layer, implemented in infrastructure
- `domain/` package or directory structure separating domain logic from infrastructure
- Bounded context directories or modules with explicit boundaries (e.g., `ordering/`, `shipping/`, `inventory/`)

### Confidence

- **high** -- aggregate roots enforcing invariants, domain events published on state changes, repository interfaces in the domain layer, and bounded context boundaries with anti-corruption layers
- **medium** -- domain layer with entities and value objects but aggregates do not enforce invariants strictly, or bounded contexts share some infrastructure
- **low** -- `domain/` package exists with entity-like classes but no explicit aggregates, events, or bounded context separation

## Architecture

Look for clear bounded context boundaries with no leaking of internal models.

### Review Checklist

- Each bounded context owns its data and exposes only domain events or APIs
- Aggregates enforce invariants — no external code mutates aggregate state directly
- Ubiquitous language is consistent within a context (naming matches domain terms)
- Anti-corruption layers translate between contexts — no shared domain objects
- Context map exists documenting upstream/downstream relationships

### Anti-patterns

- Shared database tables across bounded contexts
- Domain objects imported directly from another context's internals
- Anemic domain model — aggregates are plain data bags with logic elsewhere
- God aggregate that grows unbounded instead of splitting into sub-contexts

---
description: Dead Letter Queue architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [messaging, resilience]
---
# Dead Letter Queue

## Recognition

How to identify this pattern in code.

### Signatures

- DLQ or DLX (dead-letter exchange) configuration on queues or topics
- Failed message routing: messages moved after max retry count exceeded
- Retry count tracking: `x-death` headers, `retry_count` field, `delivery_count`
- Max retry limits: `max_retries`, `maxReceiveCount`, `x-max-retries`
- Poison message handling: dedicated error queue, alert on DLQ depth
- RabbitMQ `x-dead-letter-exchange`, SQS `RedrivePolicy`, Kafka error topics
- DLQ consumer or dashboard for inspecting and replaying failed messages

### Confidence

- **high** -- explicit DLQ configuration with retry count tracking and max retry threshold
- **medium** -- error handling that moves failed messages to a separate queue but without formal DLQ naming
- **low** -- failed messages logged or stored in a database table for manual review

## Architecture

Look for a secondary destination that captures messages that cannot be processed after exhausting retries.

### Review Checklist

- Max retry count is configured and appropriate for the failure type
- DLQ messages retain the original payload and failure metadata (reason, timestamp, stack trace)
- Alerting fires when DLQ depth exceeds zero or a threshold
- A replay mechanism exists to reprocess DLQ messages after fixing the root cause
- DLQ is monitored separately from the main queue

### Anti-patterns

- No DLQ configured, causing poison messages to block the queue or retry forever
- DLQ messages silently accumulating with no alerting or review process
- Replaying DLQ messages without fixing the underlying cause (re-poisoning the queue)
- Losing original message metadata during dead-lettering (cannot diagnose failures)

---
description: Deadlock anti-pattern
type: anti-pattern
testable: true
observable: true
graphable: false
---
# Deadlock

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Multiple locks acquired in inconsistent order across different code paths
- Nested `synchronized` blocks, `with lock:` statements, or `mutex.Lock()` calls where inner locks vary by call site
- Circular wait on resources (thread A holds lock X and waits for lock Y, thread B holds lock Y and waits for lock X)
- Thread dumps showing BLOCKED threads waiting on each other in a cycle
- Database transactions that lock rows in different orders depending on the operation

### Confidence

- **high** -- thread dump or goroutine dump shows two or more threads blocked in a cycle, each holding a lock the other needs
- **medium** -- code acquires two or more locks in different orders across different functions or methods
- **low** -- nested lock acquisition exists but ordering appears consistent; risk increases if new call sites are added

## Impact

System hangs completely with no error message, requiring manual restart to recover.

### Symptoms

- Application stops responding but process is still alive and consuming no CPU
- Thread dumps show all worker threads in BLOCKED or WAITING state
- Health checks time out even though the process has not crashed
- The hang is intermittent and load-dependent, making reproduction difficult
- Restarting the service is the only recovery, causing downtime

### Remediation

- Establish and enforce a global lock ordering: always acquire locks in the same sequence everywhere
- Reduce lock scope to the minimum critical section needed, avoiding holding locks during I/O or external calls
- Use a single coarse lock instead of multiple fine-grained locks when the performance trade-off is acceptable
- Prefer lock-free data structures or channels/message passing over shared-state locking
- Add deadlock detection tooling (jstack analysis, Go deadlock detector, database lock wait monitoring) to CI and production alerting

---
description: Decorator/Wrapper architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Decorator/Wrapper

## Recognition

How to identify this pattern in code.

### Signatures

- Object wrapping another object while exposing the same interface
- `@decorator` syntax in Python (function or class decorators)
- Middleware wrapping in web frameworks (`app.use()`, handler chains)
- Logging, caching, or auth wrappers around core logic
- Classes named `*Decorator`, `*Wrapper`, `Logging*`, `Cached*`
- Nested composition: `new AuthDecorator(new LoggingDecorator(new Service()))`
- `functools.wraps`, higher-order functions returning enhanced versions of the input

### Confidence

- **high** -- Class implementing the same interface as the wrapped object, delegating calls and adding behavior before/after
- **medium** -- `@decorator` annotations or middleware chains that wrap request/response processing
- **low** -- Higher-order function that adds behavior but does not preserve the original interface contract

## Architecture

Look for decorators preserving the wrapped object's interface and each decorator handling exactly one concern.

### Review Checklist

- Decorator implements the same interface as the component it wraps
- Each decorator adds exactly one responsibility (logging, caching, auth -- not all combined)
- Decoration order is intentional and documented when order matters
- Decorated object is unaware it is being wrapped -- no back-references or tight coupling
- Stack depth is bounded -- deeply nested decorators add latency and obscure debugging

### Anti-patterns

- Decorator that modifies the wrapped object's interface (callers must know about the decorator)
- God decorator that adds logging, caching, auth, and validation in a single wrapper
- Circular decoration where decorator A wraps B which wraps A
- Decorators with hidden side effects that change behavior in non-obvious ways when composed

See also: proxy (controls access vs adds behavior)

---
description: Deep Nesting anti-pattern
type: anti-pattern
graphable: false
---
# Deep Nesting

## Recognition

How to identify this anti-pattern in code.

### Signatures

- 5 or more levels of if/for/try nesting
- Arrow-shaped code: indentation increases to a peak then decreases, forming a sideways arrow
- Long functions (50+ lines) with nested conditionals that span most of the body
- `}}}}}` or dedent cascades at the end of blocks
- Nested ternary expressions: `a ? b ? c : d : e ? f : g`
- Multiple nested callbacks (related to callback hell but applies to synchronous code too)

### Confidence

- **high** -- a function contains 5+ levels of indentation with mixed if/for/try blocks and exceeds 40 lines
- **medium** -- 3-4 nesting levels with each level adding a conditional that could be an early return
- **low** -- 3 nesting levels that are semantically necessary (e.g., iterating a 3D matrix)

## Impact

Hard to read, hard to test, and high cyclomatic complexity makes it impossible to reason about which path executes under which conditions.

### Symptoms

- Developers cannot determine all possible execution paths through the function
- Unit tests require dozens of cases to achieve branch coverage
- Bug fixes in one branch inadvertently break another because the conditions interact
- Code formatters produce unreadable output because the line is mostly indentation
- New developers are afraid to touch the function and work around it instead

### Remediation

- Apply guard clauses: invert conditions and return early to flatten the main path
- Extract nested blocks into well-named helper functions
- Replace nested conditionals with polymorphism or strategy pattern where applicable
- Use loop constructs like `continue` and `break` to avoid nesting inside loops
- Set a maximum nesting depth lint rule (3-4 levels) and enforce it in CI

---
description: Dependency Injection/IoC architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design, architectural]
---
# Dependency Injection

## Recognition

How to identify this pattern in code.

### Signatures

- Constructor parameters that are interfaces/protocols, not concrete classes
- Decorators: `@inject`, `@Autowired`, `@Injectable`, `@Provides`
- DI container or service registry: `Container`, `Injector`, `ServiceProvider`, `Registry`
- Python: `dependency-injector` library (`providers`, `containers`), `injector` library, `fastapi.Depends`
- Java/Kotlin: Spring `@Autowired`/`@Component`, Dagger `@Inject`/`@Module`, Guice
- JS/TS: Angular `@Injectable`, NestJS `@Inject`, InversifyJS, tsyringe

### Confidence

- **high** -- DI container with explicit bindings (interface to implementation), constructor injection throughout
- **medium** -- constructor accepts interfaces and callers pass implementations, but no formal container
- **low** -- functions receiving collaborators as parameters (manual poor-man's DI)

## Architecture

Look for inversion of control: high-level modules define interfaces, low-level modules implement them, and a container wires them together.

### Review Checklist

- Dependencies are injected, not constructed internally (no `new ConcreteClass()` inside business logic)
- Binding configuration is centralized (composition root), not scattered
- Scopes are correct (singleton vs request vs transient) and documented
- Circular dependencies are absent or explicitly broken with lazy injection
- Test configuration can substitute real dependencies with fakes without code changes
- Container is initialized once at startup, not resolved dynamically at runtime

### Anti-patterns

- Service locator disguised as DI (classes calling `container.get()` at arbitrary points)
- Over-injection: dozens of constructor parameters indicating a god class
- Registering concrete classes directly instead of binding interface to implementation
- Runtime resolution scattered throughout business logic instead of at composition root

---
description: Distributed Lock architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [concurrency, resilience]
---
# Distributed Lock

## Recognition

How to identify this pattern in code.

### Signatures

- Lock acquire/release calls with TTL (time-to-live) for automatic expiry
- Redis-based locking: `SETNX`, `SET NX EX`, Redlock algorithm across multiple Redis instances
- etcd lock operations using `concurrency.NewMutex`
- Database advisory locks (`pg_advisory_lock`, `GET_LOCK` in MySQL)
- Optimistic locking with version fields (`version`, `etag`, compare-and-swap)
- Lock key naming conventions: `lock:resource:id`, `distributed-lock-*`
- Try-lock patterns with timeout and retry logic

### Confidence

- **high** -- explicit distributed lock implementation with TTL, acquire/release semantics, and a shared lock store (Redis, etcd, DB)
- **medium** -- database row-level locking or optimistic concurrency control with version fields
- **low** -- in-process mutex used in a multi-instance deployment (broken distributed locking)

## Architecture

Look for correct lock lifecycle management with TTL, fencing, and proper handling of lock loss during execution.

### Review Checklist

- Lock TTL is set appropriately (long enough for the operation, short enough for timely recovery)
- Lock holder checks ownership before releasing (does not release a lock it no longer holds)
- Fencing tokens are used to prevent operations from completing after lock expiry
- Lock acquisition has a bounded timeout (does not block indefinitely)
- Graceful handling when lock is lost mid-operation (operation is idempotent or compensatable)

### Anti-patterns

- No TTL on locks (risk of permanent deadlock if the holder crashes)
- Releasing a lock without verifying ownership (may release another process's lock)
- Using in-process locks (mutex/semaphore) in a distributed multi-instance deployment
- Redlock without sufficient independent Redis instances (minimum 5 for safety guarantees)

---
description: Distributed Monolith anti-pattern
type: anti-pattern
distributed: true
graphable: false
---
# Distributed Monolith

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Microservices sharing a single database (multiple services with connection strings to the same DB)
- Services that must be deployed together or in a specific order
- Synchronous call chains across 5+ services to complete a single request
- Shared libraries containing business logic imported by multiple services
- No independent deployability (deploying service A breaks service B)
- Distributed transactions or two-phase commit across services
- Shared data models or generated client code tightly coupling service interfaces
- A single CI pipeline that builds and deploys all services together

### Confidence

- **high** -- multiple services share a database schema, require coordinated deployment, and communicate via synchronous chains of 5+ hops
- **medium** -- shared business logic libraries exist, or services cannot be deployed independently without integration test failures
- **low** -- services share a code repository or CI pipeline, or cross-service calls are predominantly synchronous

## Impact

Microservice complexity with monolith coupling, yielding the worst properties of both architectures: network latency, operational overhead, and deployment fragility.

### Symptoms

- Deploying one service requires simultaneously deploying others
- A single service failure cascades across the entire system
- Cross-service debugging requires tracing through many synchronous hops
- Schema changes in the shared database require coordinated updates across teams
- Teams cannot release independently despite having separate services

### Remediation

- Assign each service its own database or schema with clear ownership boundaries
- Replace synchronous call chains with asynchronous messaging (events, message queues)
- Extract shared business logic into each service's codebase (duplication over coupling)
- Establish independent CI/CD pipelines per service with contract tests at boundaries
- Define service boundaries using domain-driven design bounded contexts

---
description: Distributed Tracing Instrumentation architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [observability, integration]
---
# Distributed Tracing

## Recognition

How to identify this pattern in code.

### Signatures

- OpenTelemetry SDK: `opentelemetry-api`, `opentelemetry-sdk`, `@opentelemetry/api`, `go.opentelemetry.io/otel`
- Span creation: `tracer.start_span()`, `tracer.startSpan()`, `tracer.Start()`
- Decorator-based instrumentation: `@trace`, `@WithSpan`, `@Traced`
- Span context propagation: `inject()`, `extract()`, `context.propagation`
- `traceparent` header in HTTP middleware or gRPC interceptors
- Baggage: `baggage.set_baggage()`, cross-service key-value propagation
- `TracerProvider` setup with exporter configuration (OTLP, Jaeger, Zipkin)
- Libraries: OpenTelemetry, Jaeger client, Zipkin, DataDog `ddtrace`, AWS X-Ray SDK

### Confidence

- **high** -- TracerProvider configured, spans created with parent-child relationships, and context propagated across service boundaries
- **medium** -- OpenTelemetry SDK imported and auto-instrumentation enabled but no manual spans
- **low** -- `traceparent` header forwarded in HTTP calls but no tracing SDK in dependencies

## Architecture

Look for consistent span creation, context propagation across service boundaries, and meaningful span attributes.

### Review Checklist

- TracerProvider is configured once at application startup with an appropriate exporter
- Every inbound request creates or continues a trace (middleware/interceptor handles extraction)
- Outbound calls (HTTP, gRPC, message publish) inject trace context into headers
- Spans include meaningful attributes: operation name, status code, error flag, key business identifiers
- Span names are low-cardinality and describe the operation, not the specific input
- Sensitive data is never added as span attributes (no tokens, passwords, or PII)

### Anti-patterns

- Creating spans without propagating context -- traces break at service boundaries
- Span-per-line instrumentation that creates thousands of spans per request with no useful structure
- Hardcoding exporter endpoints instead of using environment-based OTLP configuration
- Missing error recording on spans -- failures are invisible in trace views

---
description: Dual Writes anti-pattern
type: anti-pattern
observable: true
distributed: true
graphable: false
---
# Dual Writes

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Writing to a database AND publishing to a message broker in the same method without a transactional outbox
- Separate try/catch blocks for database write and event publish
- `db.save()` followed by `producer.send()` or `queue.publish()` in sequence
- Cache write and database write in the same function without atomicity guarantees
- Writing to two different databases in a single operation without distributed transactions
- `commit()` followed by `notify()` or `emit()` where either can fail independently
- REST API call to another service after a local database write, with no compensation logic

### Confidence

- **high** -- database write and message broker publish in the same method, with separate error handling and no outbox pattern
- **medium** -- two different data stores written in sequence, where failure of the second leaves the first inconsistent
- **low** -- cache update and database write in the same path, but eventual consistency may be acceptable

## Impact

Data inconsistency between stores when either write fails, leaving the system in a partially updated state that is difficult to detect and repair.

### Symptoms

- Events published for records that were not persisted (or vice versa)
- Consumers process events for data that does not exist in the database
- Retry logic causes duplicate events or duplicate database entries
- Inconsistency reports between the database and downstream systems
- Manual reconciliation scripts needed to fix data drift between stores

### Remediation

- Implement the transactional outbox pattern: write the event to an outbox table in the same database transaction, then relay asynchronously
- Use change data capture (Debezium, DynamoDB Streams) to derive events from database changes
- If using Kafka, consider the Kafka transaction API for exactly-once semantics
- Replace dual writes with an event-sourced approach where the event log is the source of truth
- Add idempotency keys to consumers so that retries and duplicates are safe

See also: outbox pattern, change-data-capture pattern

---
description: Entity-Component-System (ECS) architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [architectural, realtime]
---
# Entity-Component-System (ECS)

## Recognition

How to identify this pattern in code.

### Signatures

- Entities represented as plain integer IDs or opaque handles, not class hierarchies
- Components are pure data structs with no behavior (e.g., `Position`, `Velocity`, `Health`)
- Systems are functions that iterate over entities matching a component query
- Central `World` or `Registry` object that owns all entities and components
- Methods like `add_component()`, `remove_component()`, `query()`, `spawn()`
- Component storage organized by type (struct-of-arrays) rather than by entity
- Libraries: Bevy ECS (Rust), entt (C++), bitecs (JS), esper (Python), flecs (C/C++), legion (Rust)

### Confidence

- **high** — `World`/`Registry` class with `add_component()`/`query()` methods and entity IDs as integers
- **medium** — pure data structs paired with standalone processing functions, no inheritance hierarchy for game objects
- **low** — integer IDs used as keys into multiple parallel arrays or maps

## Architecture

Look for strict separation of identity (entities), data (components), and behavior (systems).

### Review Checklist

- Entities are plain IDs with no embedded data or methods
- Components contain only data, never logic or references to other components
- Systems declare their component dependencies explicitly via queries
- World/Registry is the single owner of all entity-component relationships
- Component queries use archetypes or bitmasks for efficient iteration
- Systems can run in parallel when their component access does not overlap

### Anti-patterns

- Components that hold methods or reference other components directly
- Systems that store state between ticks instead of reading from components
- Entity IDs used as indices into a single monolithic struct (god object)
- Inheritance hierarchies for entities instead of composition via components

---
description: Environment Parity Gap anti-pattern
type: anti-pattern
graphable: false
---
# Environment Parity Gap

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Different databases in dev vs prod: SQLite in development, PostgreSQL in production
- Different runtimes or runtime versions across environments
- `if env == "development"` or `if ENV['RAILS_ENV'] == 'test'` blocks with substantially different behavior
- Docker Compose for local dev but Kubernetes in production with no configuration overlap
- In-memory fakes replacing real services in dev (in-memory queue instead of Kafka, local filesystem instead of S3)
- Test suites that pass locally but fail in CI due to environment differences

### Confidence

- **high** -- the project uses SQLite in dev and PostgreSQL in production, or uses an in-memory substitute for a critical infrastructure dependency
- **medium** -- environment-conditional code paths exist that change business logic, not just configuration values
- **low** -- minor version differences between dev and prod runtimes, or different OS distributions

## Impact

Bugs that only appear in production because dev and prod environments behave differently in ways that matter.

### Symptoms

- "Works on my machine" is a recurring phrase during incident postmortems
- SQL queries succeed in dev (SQLite) but fail in prod (Postgres) due to syntax or type differences
- Performance issues only surface in production because dev uses simplified infrastructure
- Race conditions and concurrency bugs invisible in single-threaded dev but devastating in prod
- Deployments that passed all local tests fail immediately in staging or production

### Remediation

- Use the same database engine, message broker, and cache in all environments (Docker makes this trivial)
- Replace environment-conditional logic with configuration injection: same code paths, different config values
- Use Docker Compose profiles or Tilt to replicate production topology locally
- Run CI tests against real dependencies (not mocks) using containers or testcontainers
- Maintain a parity checklist: for every production dependency, verify the dev equivalent is the same technology

---
description: Error Boundary — component-level error catching and fallback rendering
type: pattern
graphable: true
abstraction: [frontend, error-handling]
---
# Error Boundary

## Recognition

How to identify this pattern in code.

### Signatures

- `ErrorBoundary` class component with `componentDidCatch` and `getDerivedStateFromError` (React)
- `react-error-boundary` library with `ErrorBoundary` component, `fallbackRender`, `useErrorBoundary`
- `onErrorCaptured` lifecycle hook in parent components (Vue)
- `ErrorHandler` class or `APP_INITIALIZER` with global error handling (Angular)
- `handleError` hook in `hooks.client.ts` or `+error.svelte` pages (SvelteKit)
- `errorElement` property on route definitions (React Router)
- `<Suspense>` with `fallback` combined with error boundaries for async error handling
- `fallback` or `FallbackComponent` props on boundary components
- `resetErrorBoundary` or retry mechanisms allowing recovery from errors
- Per-route `+error.svelte`, `error.tsx`, or `error.vue` files in file-based routing

### Confidence

- **high** -- Dedicated error boundary component wrapping a subtree with explicit fallback UI, error logging, and recovery mechanism
- **medium** -- Try/catch in render logic or lifecycle hooks that sets local error state and conditionally renders an error message
- **low** -- Global `window.onerror` or `unhandledrejection` handler that logs but does not provide component-level recovery

## Architecture

Look for a component boundary that intercepts rendering errors in its subtree, displays fallback UI, and optionally supports recovery or error reporting.

### Review Checklist

- Error boundaries are placed at meaningful subtree boundaries (per route, per feature section) not just at the root
- Fallback UI communicates the error clearly and offers a recovery action (retry, navigate away)
- Caught errors are reported to an error tracking service (Sentry, Datadog, etc.)
- Boundaries do not swallow errors silently -- logging or reporting always accompanies the catch
- Async errors (promise rejections, data fetching) are handled in addition to synchronous render errors
- Nested boundaries allow granular degradation without taking down the entire page

### Anti-patterns

- A single root-level error boundary that shows a generic error page for any failure anywhere
- Fallback UI that provides no recovery path, forcing the user to reload the entire application
- Error boundaries that catch and hide errors without reporting them to monitoring
- Using error boundaries to handle expected control flow (form validation, empty states) instead of exceptional failures
- No error boundary at all, letting uncaught errors crash the entire React tree to a white screen

---
description: Error Code Returns anti-pattern
type: anti-pattern
graphable: false
---
# Error Code Returns

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Functions returning -1, 0, or 1 to indicate success/failure instead of using exceptions or Result types
- Functions returning `null`/`None`/`nil` for error conditions with no way to distinguish "not found" from "failed"
- Caller code checking `if result == -1` or `if result is None` after every call
- C-style error handling idioms in languages that have exceptions (Python, Java, C#, Ruby)
- Magic sentinel values: `return ""` for error, `return -999` for missing data
- Functions with return type documented as "returns X or null on error"

### Confidence

- **high** -- a function in Python/Java/Ruby returns -1 or null for errors, and callers check the return value with comparisons instead of try/catch
- **medium** -- functions return None for both "not found" and "error occurred" with no way to distinguish the two
- **low** -- a function returns a boolean success flag alongside the actual result via output parameter or tuple

## Impact

Unchecked error codes lead to silent failures, because nothing forces the caller to inspect the return value before proceeding.

### Symptoms

- Bugs manifest far from the actual failure point because the error code was ignored
- Null/None propagates through multiple layers before finally causing a crash
- Code is littered with `if result == -1` checks that are easy to forget
- Error handling is inconsistent: some callers check, some do not
- Impossible to distinguish between a legitimate return value and an error sentinel

### Remediation

- Use the language's native error mechanism: exceptions in Python/Java/Ruby, Result/Either types in Rust/Haskell/Kotlin
- Replace null returns with Optional/Maybe types that force the caller to handle the empty case
- If error codes are unavoidable (C, Go), use a consistent struct or tuple: `(result, error)` not magic values
- Wrap legacy error-code APIs in an adapter that throws exceptions for your application code
- Add static analysis rules to flag unchecked return values from functions known to return error codes

---
description: ETL architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [data]
---
# ETL/ELT


## Recognition

How to identify this pattern in code.

### Signatures

- Airflow `DAG` definitions with operators (`PythonOperator`, `BashOperator`, `SqlOperator`)
- dbt project structure with `models/` directory containing SQL transformations
- Luigi `Task` classes with `requires()` and `output()` methods
- Prefect `@flow` and `@task` decorators defining pipeline steps
- Dagster `@op` and `@job` decorators for pipeline operations
- AWS Glue jobs or crawlers in infrastructure configuration
- `pandas` pipelines with read/transform/write stages (e.g., `read_csv` -> transformations -> `to_sql`)

### Confidence

- **high** -- dedicated pipeline framework (Airflow, dbt, Dagster) with explicit extract, transform, and load stages, checkpoint tracking, and idempotent loads
- **medium** -- scheduled scripts performing data extraction and loading with some checkpoint logic but no formal pipeline framework
- **low** -- ad-hoc data processing scripts that read from one source and write to another without explicit staging, checkpointing, or idempotency guarantees

## Architecture

Look for idempotent loads and clear checkpoint/bookmark tracking.

### Review Checklist

- Extract phase tracks a bookmark (timestamp, offset) for incremental runs
- Transform logic is pure — no side effects, testable in isolation
- Load phase is idempotent (re-running does not create duplicates)
- Failures at any stage produce clear errors and do not leave partial state
- Schema validation happens between extract and transform

### Anti-patterns

- Full re-extract every run when incremental is possible (wastes resources)
- Transform logic embedded in SQL without version control or tests
- No checkpoint — failures require manual restart from scratch
- Silent data loss on transform errors (records dropped without logging)

---
description: Event-Carried State Transfer architectural pattern
type: pattern
testable: true
distributed: true
graphable: true
abstraction: [messaging, data]
---
# Event-Carried State Transfer (Fat Events)

## Recognition

How to identify this pattern in code.

### Signatures

- Events containing full entity state, not just identifiers
- Consumers do not need to call back to the source service for data
- Larger message payloads with complete entity snapshots
- Event payloads like `{"type": "order.created", "data": {...full order object...}}`
- Eventual consistency achieved via state replication through events
- Reduced runtime coupling at the cost of larger messages and potential staleness
- Local read replicas built from consumed event data

### Confidence

- **high** -- events explicitly carry full entity state and consumers maintain local replicas without calling back
- **medium** -- events contain substantial data but consumers also make some API calls to the source
- **low** -- large event payloads that might be fat events or just verbose logging

## Architecture

Look for events carrying complete entity state that enables consumers to operate independently of the source.

### Review Checklist

- Event schema includes all fields consumers need -- no callback to the source required
- Consumers maintain local projections or caches updated from event data
- Event schema is versioned to handle additions and removals of fields over time
- Message size is monitored -- large payloads do not exceed broker limits
- Consumers handle out-of-order or duplicate events gracefully (idempotent upserts)
- Staleness is acceptable for the use case -- consumers may read slightly outdated data

### Anti-patterns

- Events so large they exceed message broker size limits or cause serialization overhead
- No schema versioning -- adding a field breaks all consumers
- Consumers treating event data as authoritative when strong consistency is required
- Including sensitive fields in fat events that propagate to services without need-to-know

---
description: Event-Driven architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [architectural, messaging]
---
# Event-Driven Architecture

## Recognition

How to identify this pattern in code.

### Signatures

- Domain events as first-class objects with type, timestamp, and payload
- Event bus or event dispatcher: `emit_event()`, `publish_event()`, `dispatch()`
- Event handler registration: `@event_handler`, `on_event()`, `subscribe(EventType, handler)`
- Event store for persisting events (distinct from event sourcing if no replay)
- Event classes: `OrderCreated`, `UserRegistered`, `PaymentProcessed`
- `events/` directory containing event definitions and handlers
- Event metadata: event ID, timestamp, source, correlation ID

### Confidence

- **high** -- domain events published through an event bus with registered handlers reacting to typed events
- **medium** -- service emits events to a message broker and downstream services consume them
- **low** -- callback hooks or observer pattern used for loose coupling without explicit event objects

## Architecture

Look for components communicating through well-defined domain events rather than direct method calls, with producers decoupled from consumers.

### Review Checklist

- Events are immutable and carry all data needed for handlers to act (no callbacks to the source)
- Event schema is versioned to allow independent evolution of producers and consumers
- Handler failures do not prevent other handlers from processing the same event
- Event ordering is preserved where business logic requires it
- Idempotent handlers tolerate duplicate event delivery

### Anti-patterns

- Events used as remote procedure calls (event payload is a command, not a fact)
- Circular event chains where event A triggers B which triggers A
- Handlers that query back to the producer for additional data (tight coupling disguised as events)
- No event schema registry, leading to silent contract breakage between services

See also: event-notification (thin events), event-carried-state (fat events)

---
description: Event log domain model — append-only log of events as source of truth
type: domain-model
abstraction: [data, messaging]
---
# Event Log

## Recognition

### Signatures

- Append-only tables or streams — inserts only, no updates or deletes
- Event tables with `event_type`, `payload`, `timestamp`, `sequence_number`
- Kafka topics, Kinesis streams, or Pulsar topics as primary data store
- Event replay capability — can rebuild state from events
- Schema registry for event versioning (Avro, Protobuf schemas)
- Snapshotting to avoid replaying entire history
- Event upcasting/versioning for schema evolution
- Audit log tables that record every state change

### Confidence

- **high** — append-only event store with replay capability, schema versioning, and snapshotting
- **medium** — append-only audit tables with event types but no replay or schema versioning
- **low** — log tables that record changes but are treated as secondary data, not source of truth

---
description: Event Notification architectural pattern
type: pattern
testable: true
distributed: true
graphable: true
abstraction: [messaging, integration]
---
# Event Notification (Thin Events)

## Recognition

How to identify this pattern in code.

### Signatures

- Events containing only ID, type, and timestamp -- no entity payload
- Consumer must call back to the source service for full data
- Lightweight event bus or notification channel with minimal message size
- Event payloads like `{"type": "order.created", "id": "123", "timestamp": "..."}`
- Decoupled notification with consumer-initiated data fetch
- Contrast with event-carried state transfer where events contain full entity data

### Confidence

- **high** -- events explicitly carry only identifiers and consumers have a documented callback API to fetch full data
- **medium** -- small event payloads with IDs but unclear whether consumers are expected to call back or the data is just minimal
- **low** -- events are small but could simply be incomplete rather than intentionally thin

## Architecture

Look for notification-only events that trigger consumers to fetch data on demand from the source.

### Review Checklist

- Events are intentionally minimal -- ID, type, and timestamp only
- The source service exposes a stable API for consumers to fetch full entity data
- Consumers handle the case where the entity has changed between notification and fetch
- Event schema is versioned so consumers know what callback API to use
- The callback API can handle the load spike from many consumers fetching after a burst of events

### Anti-patterns

- Consumers making redundant callbacks for data they already have (no local caching)
- Source API not designed for the read amplification caused by thin events
- No versioning -- consumers break when the callback API changes
- Thin events used when consumers always need full data (unnecessary round trip)

---
description: Event Sourcing architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [architectural, data]
---
# Event Sourcing

## Recognition

How to identify this pattern in code.

### Signatures

- `EventStore` or `EventStream` classes managing append-only event persistence
- `append_events()` / `load_events()` methods on repositories or stores
- Axon Framework imports (`org.axonframework.eventsourcing`)
- EventStoreDB client usage or connection configuration
- `apply()` methods on aggregate classes that mutate state from events
- Event upcasting logic that transforms old event versions to new schemas
- `Snapshot` classes or snapshot repository interfaces for aggregate state caching
- Events named in past tense (`OrderPlaced`, `PaymentReceived`) as immutable facts

### Confidence

- **high** -- EventStore/EventStream classes with `append_events()` and `load_events()`, or Axon/EventStoreDB imports with aggregate `apply()` methods
- **medium** -- Snapshot classes alongside event replay logic, or event upcasting transformations
- **low** -- Past-tense named event classes without clear append-only storage or replay mechanics

## Architecture

Look for correct event modeling and state reconstruction.

### Review Checklist

- Events are immutable facts, named in past tense (OrderPlaced, not PlaceOrder)
- Aggregate state is derived solely from replaying events — no side-channel writes
- Event schema includes a version field for future evolution
- Snapshots exist for aggregates with long event histories

### Anti-patterns

- Mutable events or events that reference other events by content
- Business logic in the event store layer
- Missing event versioning — schema changes break replay

---
description: A/B Experiment Framework architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [deployment, ml]
---
# A/B Experiment Framework

## Recognition

How to identify this pattern in code.

### Signatures

- Experiment assignment logic: users bucketed into control/treatment variants
- Methods like `assign_variant()`, `get_variant()`, `track_metric()`, `is_in_experiment()`
- Experiment configuration defining variants, traffic allocation, and target population
- Metric collection per variant with statistical significance checks
- Feature flag integration gating code paths by experiment variant
- Hash-based or random assignment ensuring consistent bucketing per user
- Libraries: Statsig, LaunchDarkly, Optimizely, GrowthBook, Unleash, custom frameworks

### Confidence

- **high** — `assign_variant()`/`track_metric()` calls with experiment configs, bucketing logic, and significance analysis
- **medium** — feature flags with variant-specific metric tracking and traffic percentage allocation
- **low** — conditional code paths toggled by user segment with separate metric counters

## Architecture

Look for a system that assigns users to experiment variants, tracks per-variant metrics, and evaluates statistical significance.

### Review Checklist

- Assignment is deterministic per user (same user always gets the same variant for a given experiment)
- Metrics are tracked per variant with enough granularity for statistical analysis
- Experiment configuration is separate from application code (external config or service)
- Sample size and duration are planned to reach statistical significance
- Interaction effects between concurrent experiments are considered (mutual exclusion or layering)
- Experiments have clear start/end criteria and cleanup process for concluded experiments

### Anti-patterns

- Non-deterministic assignment causing users to flip between variants across sessions
- Tracking only aggregate metrics with no per-variant breakdown
- No sample size planning, ending experiments before reaching significance
- Leaving concluded experiment code paths in production indefinitely

---
description: Facade architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Facade

## Recognition

How to identify this pattern in code.

### Signatures

- Classes named `*Facade` or `*Gateway` or `*Client` that wrap complex subsystems
- Single entry point class providing simplified interface to a library or subsystem
- Methods that orchestrate multiple internal calls into one high-level operation
- Wrapper modules around third-party libraries (e.g., `email_service.py` wrapping SMTP + templates + attachments)
- `__init__.py` re-exporting a simplified public API from a complex package
- SDK client classes that hide REST/gRPC details behind method calls

### Confidence

- **high** — Class explicitly named Facade wrapping multiple subsystem classes with simplified methods
- **medium** — Wrapper module/class providing high-level operations that delegate to multiple internal components
- **low** — `__init__.py` with selective re-exports or a convenience function wrapping library calls

## Architecture

Look for clean simplification of complex subsystems without adding logic.

### Review Checklist

- Facade delegates to subsystem classes, does not contain business logic itself
- Subsystem classes remain usable directly for advanced use cases
- Facade does not become a god object — one facade per cohesive subsystem
- Facade interface is stable even as subsystem internals change
- No circular dependency between facade and subsystem classes

### Anti-patterns

- Facade that adds business logic instead of just simplifying access
- Single facade wrapping the entire application (becomes god object)
- Facade that makes subsystem classes inaccessible (forced indirection)
- Nested facades (facade wrapping facade wrapping subsystem)

---
description: Factory Method architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Factory

## Recognition

How to identify this pattern in code.

### Signatures

- Classes ending in `Factory`, `Creator`, or `Provider`
- Methods named `create`, `make`, `build`, `new_*`, or `get_*` that return interfaces/base types
- Switch/match statements on a type discriminator to select which concrete class to instantiate
- Python: `class *Factory` with `create()` methods returning protocol/ABC instances
- Java/TS: `interface *Factory` with generic creation methods
- Go: `New*()` free functions returning interfaces

### Confidence

- **high** -- class named `*Factory` with `create()` returning an interface type, plus multiple concrete implementations
- **medium** -- function that switches on a type string to return different implementations of the same interface
- **low** -- constructor-like function returning a base class or union type

## Architecture

Look for correct abstraction: callers depend on the factory interface, never on concrete product classes.

### Review Checklist

- Factory returns interfaces/protocols, not concrete types
- Adding a new product type does not require modifying existing factory code (open/closed)
- Factory creation logic is centralized, not duplicated across callers
- Error handling for unknown or unsupported product types is explicit

### Anti-patterns

- Factory that returns concrete classes, defeating the abstraction
- Giant switch/match that must be edited for every new type (violation of open/closed)
- Factory with side effects beyond object creation (network calls, disk I/O)
- Caller immediately casting the factory result to a concrete type

---
description: Failure cascade flow — propagation of failure through dependent components
type: flow-shape
abstraction: [resilience, integration]
---
# Failure Cascade

## Recognition

### Signatures

- Component A depends on B depends on C — if C fails, B fails, then A fails
- No circuit breakers or timeouts on dependency calls
- Synchronous call chains where one slow/failed service blocks the caller
- Thread pool exhaustion from blocked calls propagating up the chain
- Database connection pool exhaustion causing cascading timeouts
- Retry storms: failed service recovers but gets overwhelmed by queued retries
- Health check endpoints that don't distinguish between own health and dependency health
- Missing fallback or degraded-mode behavior when dependencies are unavailable

### Confidence

- **high** — documented or observable chain where component failure propagates through multiple dependents with no isolation
- **medium** — synchronous dependency chain without circuit breakers, but failure hasn't been observed yet
- **low** — dependency chain exists but has some resilience patterns (retries, timeouts) that may or may not prevent cascading

---
description: Fan-in flow — parallel results converge into a single aggregation point
type: flow-shape
abstraction: [data, integration]
---
# Fan-In

## Recognition

### Signatures

- `Promise.all()` or `asyncio.gather()` collecting parallel results
- Map-reduce: map phase fans out, reduce phase fans in
- Scatter-gather: request sent to N services, responses aggregated
- Barrier/join patterns: wait for all N tasks before proceeding
- Kafka consumer reading from multiple partitions into one handler
- `CompletableFuture.allOf()` in Java collecting concurrent results
- Go `sync.WaitGroup` or channel-based fan-in collecting goroutine results
- GraphQL DataLoader batching multiple individual requests into one query
- Aggregation service that calls multiple backends and merges responses

### Confidence

- **high** — explicit parallel dispatch with barrier/join collecting all results before proceeding
- **medium** — sequential calls to multiple services with results merged at the end
- **low** — multiple data sources queried but aggregation is ad-hoc, not structured

---
description: Fan-out flow — one event triggers parallel processing across multiple consumers
type: flow-shape
abstraction: [messaging, integration]
---
# Fan-Out

## Recognition

### Signatures

- One Kafka/RabbitMQ/SNS producer with multiple consumer groups on the same topic
- Event emitter with multiple listeners: `emitter.on('user_created', handler1, handler2)`
- Pub/sub topic with multiple subscriptions
- `Promise.all()` or `asyncio.gather()` dispatching parallel work
- Webhook dispatcher sending the same event to multiple registered URLs
- CDC (Change Data Capture) feeding multiple downstream systems
- SNS → multiple SQS queues pattern
- One database trigger firing multiple downstream processes

### Confidence

- **high** — explicit pub/sub with multiple independent consumer groups processing the same event
- **medium** — one event handler dispatching to multiple functions sequentially (fan-out but not parallel)
- **low** — multiple modules importing the same event type but unclear if they process the same instance

---
description: Feature Envy anti-pattern
type: anti-pattern
testable: true
graphable: false
---
# Feature Envy

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Methods that access more fields from another class than from their own class
- Getter chains to extract data from other objects (`order.customer.address.city`)
- Utility methods that should live on the data class they operate on
- Functions taking an object as a parameter and accessing 3+ of its attributes
- Methods that destructure or unpack another object's internals to perform logic
- Static methods or free functions that operate entirely on another class's data
- Long parameter lists where all parameters come from a single other object

### Confidence

- **high** -- a method accesses 4+ fields of another class and 0-1 fields of its own, and this pattern repeats across multiple methods
- **medium** -- a method primarily operates on data from one other object, using getter chains or attribute access
- **low** -- a utility function takes an object and reads a couple of its fields, but the logic may legitimately belong elsewhere

## Impact

Misplaced responsibility and tight coupling, where behavior lives apart from the data it operates on, making both classes harder to change independently.

### Symptoms

- Changing a class's internal structure breaks methods in other unrelated classes
- Logic for a concept is scattered across multiple classes instead of being cohesive
- Getter methods exist solely to support external methods that should be internal
- Refactoring one class requires updating logic in distant modules
- Duplicated logic appears because multiple classes implement similar operations on the same data

### Remediation

- Move the method to the class whose data it primarily uses
- If the method uses data from multiple classes, extract the shared logic into the data-owning class and call it
- Replace getter chains with methods that encapsulate behavior (Tell, Don't Ask)
- Eliminate trivial getters by moving the computation to the data class
- Apply the Information Expert principle: assign responsibility to the class with the information needed to fulfill it

---
description: Feature Flag/Toggle architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [deployment, design]
---
# Feature Flag/Toggle

## Recognition

How to identify this pattern in code.

### Signatures

- Conditional checks like `if feature_enabled("X")`, `is_feature_on()`, `hasFeature()`
- Feature flag configuration files (JSON/YAML with flag names and boolean/percentage values)
- `FEATURE_*` environment variables controlling behavior toggles
- SDK imports: LaunchDarkly (`ldclient`), Unleash (`unleash-client`), Flagsmith, Split
- Remote flag evaluation endpoints or polling for flag state changes
- Flag context objects passing user attributes for targeting rules

### Confidence

- **high** -- feature flag SDK initialized with flag evaluation calls gating code paths, plus a flag management config or service
- **medium** -- `FEATURE_*` env vars or config-file-driven toggles controlling conditional branches
- **low** -- simple boolean config values that enable/disable behavior but lack flag lifecycle management

## Architecture

Look for code paths gated by externally managed toggles with clean separation between flagged and unflagged behavior.

### Review Checklist

- Flags have clear ownership and a planned removal date (no permanent feature flags)
- Flag evaluation has a sensible default when the flag service is unavailable
- Code paths for both flag states are tested independently
- Flag naming convention is consistent and descriptive
- Stale flags are tracked and cleaned up regularly
- Targeting rules are reviewed for correctness (percentage rollouts, user segments)

### Anti-patterns

- Flags that never get removed, accumulating permanent conditional complexity
- Nested feature flags creating combinatorial explosion of code paths
- Using feature flags for configuration that should be in application config
- No default behavior when the flag service is unreachable

---
description: Feature Store architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [data, ml]
---
# Feature Store

## Recognition

How to identify this pattern in code.

### Signatures

- Centralized feature repository with feature definitions and metadata
- Dual serving paths: online (low-latency) and offline (batch/historical)
- Methods like `get_online_features()`, `get_historical_features()`, `apply()`
- Feature views or feature tables defining transformations from raw data to features
- Point-in-time-correct joins for training data to prevent data leakage
- Entity keys mapping features to business objects (user, item, transaction)
- Libraries: Feast, Tecton, Hopsworks, SageMaker Feature Store, Databricks Feature Store

### Confidence

- **high** — `get_online_features()`/`get_historical_features()` calls with feature view definitions and entity keys
- **medium** — centralized feature definitions with separate online and offline storage backends
- **low** — shared data transformations reused between training pipelines and serving code

## Architecture

Look for a centralized registry that serves pre-computed features consistently to both training and inference.

### Review Checklist

- Feature definitions are versioned and shared between training and serving
- Online store serves features with latency under the serving SLA
- Offline store supports point-in-time-correct joins for training data
- Feature transformations are defined once and materialized to both stores
- Entity keys are consistent across features and across online/offline paths
- Feature freshness and staleness are monitored with clear SLAs

### Anti-patterns

- Duplicating feature logic in training scripts and serving code (training-serving skew)
- No point-in-time correctness, causing future data to leak into training features
- Online store used for batch training (latency costs, missing historical data)
- Features defined ad-hoc per model with no shared registry or versioning

---
description: Fire and Forget anti-pattern
type: anti-pattern
observable: true
distributed: true
graphable: false
---
# Fire and Forget

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Publishing messages with no delivery guarantee or acknowledgment check
- `producer.send()` without awaiting acknowledgment or checking the returned future/promise
- No idempotency key on published messages
- No retry on publish failure (`try: send() except: pass`)
- `ignore_errors=True` or equivalent flag on message send calls
- No dead-letter queue or failure handling for undeliverable messages
- Async task dispatch (`celery.delay()`, `Task.Run()`) with no result tracking or error callback

### Confidence

- **high** -- message publish call has no error handling, no acknowledgment check, and no retry mechanism, confirmed by silent message loss visible in consumer-side gaps
- **medium** -- `producer.send()` is called without awaiting the result or registering an error callback, or `ignore_errors=True` is set on the send operation
- **low** -- messages are published without an idempotency key, or there is no dead-letter queue configured for the topic/queue

## Impact

Silent message loss leading to inconsistent state between services, with no visibility into what was lost.

### Symptoms

- Consumer-side counts do not match producer-side counts with no errors logged
- Downstream systems are missing data that should have been delivered via messages
- Intermittent data inconsistencies between services that are hard to reproduce
- No alerting fires when messages are lost because failures are silently swallowed
- Retry or reconciliation jobs are needed to fix state drift caused by lost messages

### Remediation

- Always await or check the acknowledgment/future returned by `producer.send()` and handle failures explicitly
- Implement the transactional outbox pattern: write messages to a database table in the same transaction as the business operation, then relay them to the broker
- Add idempotency keys to all published messages so consumers can safely handle duplicates from retries
- Configure dead-letter queues for all topics/queues and monitor them with alerts
- Add end-to-end message delivery monitoring that reconciles producer and consumer counts and alerts on divergence

See also: outbox pattern

---
description: Test Fixture / Data Builder architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [testing]
---
# Test Fixture / Data Builder

## Recognition

How to identify this pattern in code.

### Signatures

- `*Factory` or `*Builder` classes in test directories (`UserFactory`, `OrderBuilder`)
- `factory_boy` with `factory.Factory`, `factory.SubFactory`, `factory.LazyAttribute` in Python
- `faker` or `Faker` library usage for generating realistic test data
- `build()`, `create()`, `make()` methods returning fully constructed test objects
- Test data creation helpers with default values and optional overrides
- `FactoryBot.define` or `FactoryBot.create` in Ruby tests
- Builder pattern with method chaining: `.with_name()`, `.with_status()`, `.build()`

### Confidence

- **high** — Dedicated factory/builder classes with sensible defaults, overrides, and composition of nested objects
- **medium** — Helper functions that construct test data but without a consistent builder API or factory library
- **low** — Inline object construction in tests with repeated boilerplate that could benefit from a builder

## Architecture

Look for centralized, composable test data construction that keeps tests focused on the scenario rather than setup.

### Review Checklist

- Factories provide sensible defaults so tests only override the fields relevant to the scenario
- Complex object graphs use nested factories or sub-builders rather than manual wiring
- Factory definitions live in a shared test utilities module, not duplicated across test files
- Builders support both in-memory objects and persisted records (where applicable)
- Generated data is deterministic or seed-controlled for reproducible tests

### Anti-patterns

- Every test file has its own copy-pasted object construction code instead of using shared factories
- Factories with too many required parameters, forcing callers to specify irrelevant fields
- Builders that silently create side effects (database writes, API calls) when only an in-memory object is needed
- Over-reliance on random data without seeding, causing flaky tests that pass or fail non-deterministically

---
description: Flaky Tests anti-pattern
type: anti-pattern
testable: true
observable: true
graphable: false
---
# Flaky Tests

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `sleep()` or `time.sleep()` in test code to wait for conditions
- `time.time()` assertions comparing wall-clock timestamps
- Shared mutable test state (class-level variables modified across test methods)
- Tests depending on execution order (passing in sequence, failing in isolation)
- Network calls in unit tests (HTTP requests to external services without mocking)
- `@retry` or retry decorators on test methods
- Assertions on floating-point equality without tolerance
- Tests depending on file system ordering or locale settings
- Race conditions from multithreaded test fixtures

### Confidence

- **high** -- `sleep()` calls in tests combined with intermittent CI failures on the same test, or `@retry` decorators on test methods
- **medium** -- tests make real network calls or depend on shared mutable state, and CI shows occasional failures
- **low** -- tests use `time.time()` or depend on execution order, but failures have not yet been observed

## Impact

Eroded trust in CI, leading teams to ignore failures, disable tests, or merge despite red builds.

### Symptoms

- The same test passes and fails on consecutive CI runs with no code change
- Developers re-run CI pipelines hoping for green without investigating failures
- A growing list of tests marked `@skip`, `@xfail`, or `@flaky`
- CI failure notifications are routinely ignored by the team
- Test suite reliability metrics show less than 99% pass rate on unchanged code

### Remediation

- Replace `sleep()` with explicit waits or polling with timeout (e.g., `wait_for_condition()`)
- Mock all external network calls in unit tests; use contract tests for service integration
- Isolate test state: each test creates and tears down its own data, no shared mutables
- Run tests in random order (`pytest-randomly`) to surface order dependencies
- Track flaky tests with a quarantine system and fix or delete them within a sprint

---
description: Flux/Redux (Unidirectional Data Flow) architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [architectural, frontend, data]
---
# Flux/Redux (Unidirectional Data Flow)

## Recognition

How to identify this pattern in code.

### Signatures

- Central store holding application state as a single source of truth
- Actions dispatched to describe state changes (`dispatch()`, action creators)
- Reducers or mutations as pure functions transforming state in response to actions
- `store`, `actions/`, `reducers/`, `mutations/`, `slices/` directories or files
- Libraries: Redux, Vuex/Pinia, MobX (with actions), NgRx, Zustand, Recoil

### Confidence

- **high** -- Explicit store with `dispatch(action)`, reducer functions, and `connect()`/`useSelector()` bindings
- **medium** -- Centralized state management with defined mutations and unidirectional flow, but non-standard naming
- **low** -- Any pattern where UI state flows in one direction through a central container

## Architecture

Look for a unidirectional cycle: view dispatches actions, reducers update the store, store notifies the view.

### Review Checklist

- Reducers are pure functions with no side effects (no API calls, no mutations of arguments)
- Actions are serializable plain objects -- no functions or class instances as payloads
- Side effects are handled in middleware, thunks, or sagas, not in reducers or components
- Store shape is normalized -- no deeply nested duplicate data
- Selectors derive computed state rather than storing redundant copies

### Anti-patterns

- Mutating store state directly instead of dispatching actions
- Putting API calls or async logic inside reducers
- Single monolithic reducer instead of composing smaller reducers per domain
- Every component connected to the global store instead of passing props from connected parents

---
description: Flyweight architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Flyweight

## Recognition

How to identify this pattern in code.

### Signatures

- Shared immutable objects to reduce memory footprint
- Object pools keyed by intrinsic state
- `intern()` methods (string interning, symbol tables)
- String interning (`sys.intern()`, `String.intern()`)
- `__slots__` in Python to minimize per-instance memory
- Factory methods returning cached instances instead of new objects
- `WeakValueDictionary` or `WeakHashMap` for automatic eviction of unused flyweights
- Separation of intrinsic (shared) and extrinsic (context-dependent) state

### Confidence

- **high** -- Factory returning cached immutable instances keyed by intrinsic state, with extrinsic state passed in at usage time
- **medium** -- Object pool or interning mechanism that reuses instances but without explicit intrinsic/extrinsic separation
- **low** -- Caching or memoization that reduces object creation but is not structured as a flyweight

## Architecture

Look for a factory that manages shared immutable instances, separating intrinsic state (shared) from extrinsic state (caller-provided).

### Review Checklist

- Flyweight objects are truly immutable (no mutable intrinsic state)
- Extrinsic state is passed in by the caller, not stored on the flyweight
- Factory ensures identity: same intrinsic state always returns the same instance
- Memory savings are measurable and justified (pattern adds complexity)
- Thread safety of the flyweight pool is addressed in concurrent environments
- Weak references or eviction policy prevents the pool from becoming a memory leak

### Anti-patterns

- Mutable state on flyweight instances, causing shared state corruption
- Storing extrinsic state on the flyweight, defeating the sharing benefit
- Flyweight pool growing unbounded without eviction (memory leak disguised as optimization)
- Applying the pattern where object count is small (premature optimization)

---
description: Form Binding — two-way or controlled data binding between form inputs and state
type: pattern
graphable: false
abstraction: [frontend, data]
---
# Form Binding

## Recognition

How to identify this pattern in code.

### Signatures

- Controlled inputs with `value` + `onChange` handlers managing state (React)
- `react-hook-form` with `useForm`, `register`, `handleSubmit`, `Controller` (React)
- `formik` with `useFormik`, `<Formik>`, `<Field>`, `<Form>` (React)
- `v-model` directive for two-way binding on inputs, selects, textareas (Vue)
- `vee-validate` with `useForm`, `useField`, `<Form>`, `<Field>` (Vue)
- `ngModel` for template-driven forms, `FormControl`/`FormGroup`/`FormBuilder` for reactive forms (Angular)
- `bind:value` for two-way binding on form elements (Svelte)
- Zod, Yup, or Joi schemas used for form validation: `z.object()`, `yup.object().shape()`
- `zodResolver`, `yupResolver` connecting schema validation to form libraries
- Form submission handlers: `onSubmit`, `handleSubmit`, `@submit.prevent`
- Error display patterns: `errors.fieldName`, field-level error messages, touched state tracking

### Confidence

- **high** -- Form library (react-hook-form, Formik, vee-validate, Angular Reactive Forms) with schema validation, field registration, and structured error handling
- **medium** -- Framework two-way binding (v-model, ngModel, bind:value) with manual validation logic in submit handler
- **low** -- Uncontrolled form inputs read via refs or FormData at submit time, with no structured binding or validation

## Architecture

Look for a structured connection between form inputs and application state, with validation rules enforced before submission and error feedback displayed per field.

### Review Checklist

- Form state is managed by a form library or structured pattern, not scattered useState calls per field
- Validation schema is defined separately from UI and shared with backend if possible (Zod)
- Field-level errors are displayed adjacent to the relevant input, not just as a summary
- Form submission is disabled or guarded while validation errors exist
- Async validation (uniqueness checks, server-side rules) is handled without blocking the UI
- Form reset and dirty-state tracking are implemented for navigation guards and cancel actions

### Anti-patterns

- Individual `useState` for every form field instead of using a form library or reducer
- Validation only on submit, with no inline feedback as the user fills out fields
- Two-way binding on complex objects causing unexpected mutations (especially in Vue/Angular)
- No loading or disabled state on the submit button, allowing double submission
- Mixing controlled and uncontrolled inputs in the same form

---
description: Future/Promise architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [concurrency, design]
---
# Future/Promise

## Recognition

How to identify this pattern in code.

### Signatures

- Deferred computation represented as a handle to a result not yet available
- `.then()`, `await`, `.get()`, `.result()` calls on async result containers
- `Future`, `Promise`, `CompletableFuture`, `Deferred`, `Task` types
- Chaining and composition: `Promise.all()`, `asyncio.gather()`, `CompletableFuture.thenCompose()`
- Libraries: JavaScript `Promise`, Python `asyncio.Future`/`concurrent.futures.Future`, Java `CompletableFuture`, Rust `Future` trait

### Confidence

- **high** -- Explicit `Future`/`Promise` objects with `.then()` chains or `await` suspension points
- **medium** -- Callback-based async operations returning a handle that resolves later
- **low** -- Any deferred computation pattern where results are retrieved asynchronously

## Architecture

Look for async result containers that decouple task submission from result retrieval.

### Review Checklist

- Every future/promise has an error path -- `.catch()`/`except` handlers are not omitted
- Composition is used for parallel work (`Promise.all`, `asyncio.gather`) rather than sequential awaits in a loop
- Cancellation is supported and propagated through the chain
- Timeouts are applied to prevent indefinite waits on unresolved futures
- Results are consumed -- no orphaned futures whose exceptions go unobserved

### Anti-patterns

- Awaiting futures sequentially in a loop when they could run concurrently
- Swallowing rejections/exceptions with empty `.catch()` handlers
- Creating futures without ever awaiting or observing their result (fire-and-forget with no error handling)
- Mixing callback and promise styles in the same flow, losing error propagation

---
description: Game Loop architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [lifecycle, realtime]
---
# Game Loop

## Recognition

How to identify this pattern in code.

### Signatures

- Main loop structure: `while running: process_input(); update(dt); render()`
- Delta time (`dt`) calculation between frames for frame-rate independence
- Fixed timestep accumulator pattern separating physics/logic updates from rendering
- Tick rate or update rate constants (e.g., `TICK_RATE = 60`, `FIXED_DT = 1/60`)
- `requestAnimationFrame` in browser-based implementations
- Sleep or vsync calls to cap frame rate
- Interpolation between previous and current state for smooth rendering
- Separate `fixed_update()` and `update()` methods

### Confidence

- **high** — explicit `while` loop with input/update/render phases and delta time tracking
- **medium** — `requestAnimationFrame` callback with `dt` parameter and state update logic
- **low** — periodic timer or interval calling an update function with elapsed time

## Architecture

Look for a well-structured main loop with clear phase separation and proper timestep handling.

### Review Checklist

- Input processing is separated from state updates and rendering
- Fixed timestep used for deterministic simulation (physics, game logic)
- Variable timestep or interpolation used for rendering smoothness
- Delta time is capped to prevent spiral-of-death on long frames
- Loop handles pause, resume, and graceful shutdown cleanly
- Frame timing is measured accurately (high-resolution timer, not wall clock)

### Anti-patterns

- Using variable timestep for physics or game logic (non-deterministic behavior)
- No delta time cap, causing simulation explosions after a lag spike
- Mixing input handling, logic updates, and rendering in a single function
- Busy-waiting without sleep or vsync (100% CPU for no benefit)

---
description: Gateway-backends structure — single entry point routing to multiple backend services
type: structure-shape
abstraction: [architectural, api]
---
# Gateway-Backends

## Recognition

### Signatures

- API gateway (Kong, AWS API Gateway, Traefik, nginx) routing to multiple services
- BFF (Backend-for-Frontend) pattern: one gateway per client type
- Path-based routing: `/api/users/*` → user service, `/api/orders/*` → order service
- GraphQL gateway federating multiple subgraphs
- Reverse proxy with upstream configuration
- Load balancer distributing to multiple instances of the same service
- Service registry (Consul, Eureka) used by gateway for discovery
- Rate limiting, auth, and logging applied at gateway level
- `docker-compose.yml` with a gateway service and multiple backend services

### Confidence

- **high** — explicit gateway service (nginx/Kong/Traefik) with routing rules to multiple distinct backend services
- **medium** — application-level router dispatching to internal service modules (monolith acting as gateway)
- **low** — multiple services exist but no central entry point (each service exposed directly)

---
description: GitOps architectural pattern
type: pattern
distributed: true
graphable: true
abstraction: [deployment]
---
# GitOps

## Recognition

How to identify this pattern in code.

### Signatures

- Git repository as the single source of truth for infrastructure and application state
- ArgoCD `Application` CRDs pointing to git repo paths with `syncPolicy`
- Flux `GitRepository`, `Kustomization`, and `HelmRelease` CRDs
- Kustomize overlays directory structure (`base/`, `overlays/staging/`, `overlays/production/`)
- Reconciliation loop configurations (sync intervals, auto-sync, self-heal, prune)
- Declarative desired state in YAML manifests committed to git
- PR-based change workflow for infrastructure modifications

### Confidence

- **high** -- ArgoCD/Flux CRDs with auto-sync enabled, git repo structure with environment overlays, reconciliation loop actively running
- **medium** -- declarative manifests in a git repo with CI/CD applying them, but no continuous reconciliation agent
- **low** -- infrastructure YAML in git but applied manually via `kubectl apply` or scripts

## Architecture

Look for a reconciliation loop that continuously converges actual cluster state toward the desired state declared in git.

### Review Checklist

- Drift detection is active (the controller detects and corrects manual changes)
- Sync policy includes pruning of resources removed from git
- Secrets are not stored in plaintext in git (use SealedSecrets, SOPS, or external-secrets)
- Environment promotion follows a git-based workflow (PR from staging overlay to production overlay)
- Sync status and health are monitored with alerts on degraded or out-of-sync applications

### Anti-patterns

- Mixing imperative `kubectl` commands with GitOps-managed resources (causing drift fights)
- Storing secrets in plaintext in the git repository
- No sync status monitoring -- the reconciliation loop fails silently
- Single environment overlay for all stages (no separation between staging and production)

---
description: God Endpoint anti-pattern
type: anti-pattern
graphable: false
---
# God Endpoint

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Single API route handling multiple unrelated operations via an `action` or `type` parameter
- URLs like `POST /api?action=createUser&action=sendEmail` or `POST /rpc` with an operation field in the body
- Large switch/case or if-else chain on an operation type inside one handler function
- One endpoint accepting wildly different request/response shapes depending on the action
- API documentation for a single route that spans multiple pages covering unrelated operations

### Confidence

- **high** -- a single handler function dispatches to 5+ unrelated operations based on a string parameter, each with different input/output schemas
- **medium** -- one endpoint handles 3+ distinct operations via a type/action field with a switch statement
- **low** -- an endpoint has 2 operation modes with some shared logic but growing toward more

## Impact

Impossible to document, cache, rate-limit, or evolve operations independently because they share a single undifferentiated route.

### Symptoms

- API documentation is confusing because one endpoint does many unrelated things
- HTTP caching is impossible since the same URL returns different data based on the request body
- Rate limiting cannot be applied per-operation because all operations share the same route
- Authorization checks become a tangled mess of per-action permission logic inside one handler
- Monitoring and alerting cannot distinguish between healthy and failing operations since they share one metric

### Remediation

- Split each operation into its own endpoint with a distinct URL path and HTTP method
- Use RESTful resource-based URLs or well-defined RPC service methods with separate routes
- Apply the Single Responsibility Principle at the endpoint level: one route, one operation
- Implement a lightweight router or controller layer that maps actions to dedicated handler functions
- Migrate incrementally by adding new dedicated endpoints and deprecating the god endpoint with a compatibility shim

---
description: God Object/Class anti-pattern
type: anti-pattern
graphable: false
---
# God Object/Class

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Classes exceeding 1000 lines of code
- Classes with 20+ public methods
- A single class importing from nearly every package in the project
- Methods touching unrelated concerns (e.g., HTTP handling, database access, email sending, and PDF generation in one class)
- Class names containing "Manager", "Handler", "Processor", "Utils", or "Helper" that accumulate all miscellaneous logic
- Instance variables numbering 15+ covering disparate domains

### Confidence

- **high** -- class has 1000+ lines, 20+ methods, and imports from 5+ unrelated packages
- **medium** -- class has 500+ lines with methods spanning multiple domains (I/O, business logic, presentation)
- **low** -- class name is generic ("AppManager", "MainService") and growing steadily over time

## Impact

Impossible to test, modify, or understand in isolation because the class owns too many responsibilities.

### Symptoms

- Unit tests require mocking dozens of dependencies to instantiate the class
- Every feature change touches the same file, causing constant merge conflicts
- New team members cannot understand what the class is responsible for
- A bug fix in one area of the class introduces regressions in unrelated functionality
- The class is the most-changed file in git history

### Remediation

- Identify distinct responsibilities by grouping related methods and fields
- Extract each responsibility into its own class with a focused interface
- Use composition: the original class delegates to the new smaller classes
- Apply the Single Responsibility Principle as a litmus test for each extraction
- Set a hard line limit (300-400 lines) in linting to prevent regrowth

---
description: Golden Hammer anti-pattern
type: anti-pattern
graphable: false
---
# Golden Hammer

## Recognition

How to identify this anti-pattern in code.

### Signatures

- One framework or library used for everything (e.g., Celery for async tasks, cron scheduling, messaging, and orchestration simultaneously)
- Same database serving OLTP, OLAP, caching, and queuing workloads
- A single programming language used across all tiers regardless of fit (frontend, backend, CLI tooling, data pipelines, infrastructure)
- Every problem solved with the same pattern (e.g., everything is a microservice, everything is a stored procedure, everything is a queue)
- Extensive workarounds to force a tool beyond its intended use case

### Confidence

- **high** -- a single technology serves 3+ fundamentally different purposes with documented workarounds for its limitations in each
- **medium** -- architectural decisions consistently favor one tool despite documented better alternatives for specific use cases
- **low** -- team discussions default to "just use X" without evaluating alternatives

## Impact

Forces inappropriate solutions on problems, leading to poor performance, reliability issues, and excessive workaround code.

### Symptoms

- Performance problems in one workload (e.g., analytics queries) degrade another (e.g., transactional writes) because they share infrastructure
- Workaround code exceeds the actual business logic it supports
- The team cannot hire specialists because the tech stack is idiosyncratic
- Upgrading the single tool becomes high-risk because everything depends on it
- New requirements are rejected or awkwardly shoehorned because the chosen tool does not support them natively

### Remediation

- Evaluate each major capability against purpose-built alternatives using a lightweight ADR (Architecture Decision Record)
- Introduce polyglot persistence: use the right data store for each workload (RDBMS for transactions, cache for hot data, warehouse for analytics)
- Decouple workloads so they can migrate to better-fit tools independently
- Establish a technology radar that the team reviews quarterly to stay aware of appropriate tools
- Start with the highest-pain workload: migrate it first as a proof of concept

---
description: Graceful Degradation architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [resilience, lifecycle]
---
# Graceful Degradation

## Recognition

How to identify this pattern in code.

### Signatures

- Fallback responses returned when a dependency is down or slow
- Reduced functionality mode toggled by health state or feature flags
- Cached responses served as fallback when the live source is unavailable
- `try/except` or `try/catch` blocks returning a default value instead of propagating errors
- Feature flags disabling non-essential features under load
- Circuit breaker fallback handlers providing degraded responses
- Graceful error pages or partial-content responses to the client

### Confidence

- **high** -- explicit fallback paths defined per dependency with documented degraded behavior
- **medium** -- some fallback logic exists but not consistently applied across all dependencies
- **low** -- generic error handling that returns defaults but without intentional degradation strategy

## Architecture

Look for intentional fallback paths that keep the system usable when dependencies fail.

### Review Checklist

- Each non-critical dependency has a defined fallback behavior (cache, default, omit)
- Critical vs non-critical dependencies are explicitly classified
- Degraded mode is observable -- logs and metrics indicate when fallbacks activate
- Fallback responses are clearly distinguishable from normal responses (e.g., staleness indicators)
- System recovers automatically when the dependency comes back

### Anti-patterns

- All-or-nothing failure -- one dependency down takes the entire service offline
- Silent degradation where clients receive stale data without any indication
- Fallback logic that itself depends on the failing service
- No testing of degraded paths -- fallback code rots and fails when actually needed

---
description: Generic graph model covering dependency graphs, DAGs, and general graph algorithms
type: pattern
category: domain-model
abstraction: [data, algorithmic]
---
# Graph

## Recognition

How to identify this pattern in code.

### Signatures

- `Graph`, `DiGraph`, `DAG` class definitions or type aliases
- `topological_sort`, `topo_sort`, `toposort` function calls for DAG ordering
- `adjacency_list`, `adjacency_matrix`, `adj` data structures
- `BFS`, `DFS`, `breadth_first`, `depth_first` traversal implementations
- `shortest_path`, `dijkstra`, `bellman_ford`, `a_star` pathfinding algorithms
- `cycle_detect`, `has_cycle`, `is_acyclic` graph validation functions
- Python: `networkx`, `igraph`, `graphlib.TopologicalSorter` usage
- JS/TS: `graphlib`, `dagre`, `cytoscape` graph libraries
- Go: `gonum/graph`, custom `Graph` interface with `Nodes()` and `Edges()`
- Rust: `petgraph`, `Graph`, `DiGraph`, `Dfs`, `Bfs` traversal iterators
- Java: JGraphT (`org.jgrapht`), `DirectedAcyclicGraph`, `GraphWalk`

### Confidence

- **high** -- Dedicated graph library (networkx, petgraph, JGraphT) with explicit graph construction, traversal algorithms, and cycle detection or topological sorting
- **medium** -- Custom adjacency list or matrix with BFS/DFS traversal and path computation
- **low** -- Parent-child relationships forming an implicit tree or DAG without explicit graph modeling or algorithms

## Architecture

### When to use
- Dependency resolution systems (build tools, package managers, task schedulers)
- Workflow orchestration where tasks have ordering constraints
- Any domain with entities connected by directed relationships requiring traversal or ordering

### Anti-patterns
- Implicit graph relationships scattered across code without a centralized graph data structure
- Missing cycle detection in systems that assume DAG properties, causing infinite loops
- Recomputing traversals on every access instead of caching topological order or shortest paths

### Complements
- [property-graph](/concepts/property-graph) — specialized graph with typed, attributed nodes and edges
- [workflow-engine](/concepts/workflow-engine) — workflow DAGs are a common graph application
- [pipeline-filter](/concepts/pipeline-filter) — pipelines are often modeled as DAGs

## Impact

Graph algorithms determine execution order, dependency resolution, and reachability in systems that model relationships. Cycle detection failures in DAGs cause runtime hangs, and inefficient traversal algorithms become bottlenecks as graph size grows. Testing must verify graph invariants (acyclicity for DAGs, connectivity requirements) on every mutation.

---
description: GraphQL architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [api, integration]
---
# GraphQL

## Recognition

How to identify this pattern in code.

### Signatures

- Schema definition language files with `type Query {}`, `type Mutation {}`, `type Subscription {}`
- Resolver functions mapping schema fields to data fetching logic
- Single endpoint (typically `/graphql`) handling all queries and mutations
- `.graphql` or `.gql` schema files
- Libraries: `graphene` (Python), `apollo-server` (Node), `strawberry` (Python), `graphql-java`, `gqlgen` (Go)
- Query strings with selection sets: `query { user(id: 1) { name email } }`
- DataLoader pattern for batching and caching nested field resolution

### Confidence

- **high** -- SDL schema files with resolvers, single `/graphql` endpoint, query/mutation type definitions
- **medium** -- GraphQL library imported with schema construction but mixed with REST endpoints
- **low** -- single endpoint accepting JSON queries but no formal GraphQL schema or SDL files

## Architecture

Look for a well-structured schema with efficient resolver implementation and proper query complexity controls.

### Review Checklist

- Query depth and complexity limits are enforced to prevent abusive queries
- N+1 query problem is addressed with DataLoader or batching in resolvers
- Schema design follows a graph structure (connections between types) rather than mirroring REST resources
- Authentication and authorization are handled per-field or per-resolver, not just at the endpoint level
- Pagination uses cursor-based connections (Relay-style) for large collections
- Error handling follows GraphQL error specification with proper error extensions

### Anti-patterns

- No query depth or complexity limits (allows arbitrarily expensive queries)
- Resolvers making individual database calls per item without batching (N+1)
- Exposing database schema directly as GraphQL schema without an abstraction layer
- Using GraphQL for simple CRUD with no relationships (overhead without benefit)

---
description: gRPC/RPC architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [api, integration]
---
# gRPC/RPC

## Recognition

How to identify this pattern in code.

### Signatures

- `.proto` files with `service` and `rpc` declarations
- Protobuf `message` definitions for request/response types
- Generated stub files (`*_pb2.py`, `*_pb2_grpc.py`, `*.pb.go`, `*_grpc.pb.go`)
- Bidirectional streaming: `stream` keyword in `.proto` rpc definitions
- Libraries: `grpcio` (Python), `@grpc/grpc-js` (Node), `tonic` (Rust), `google.golang.org/grpc` (Go)
- Channel creation and stub instantiation in client code
- gRPC server setup with `add_servicer_to_server` or equivalent registration

### Confidence

- **high** -- `.proto` files with service definitions, generated stubs, server/client setup using gRPC libraries
- **medium** -- protobuf message definitions present but service layer uses a different transport (gRPC-Web, Twirp)
- **low** -- binary serialization in use but no `.proto` files or gRPC imports visible

## Architecture

Look for well-defined service contracts in proto files with proper error handling and streaming where appropriate.

### Review Checklist

- Proto files are versioned and backward-compatible (no renumbering or removing fields, use `reserved`)
- Deadlines/timeouts are set on all RPC calls (no unbounded waits)
- Error handling uses gRPC status codes correctly (not just `UNKNOWN` or `INTERNAL` for everything)
- Streaming RPCs have proper flow control and cancellation handling
- Proto files live in a shared location or are distributed via a proto registry
- Health checking service is implemented (`grpc.health.v1.Health`)

### Anti-patterns

- Breaking proto compatibility by renumbering or removing fields without `reserved`
- No deadlines on RPC calls (risk of hanging connections consuming resources)
- Sending large payloads over gRPC without chunking or streaming (default 4MB message limit)
- Generating client stubs in the same repo as the server instead of distributing proto files

---
description: Hardcoded Credentials anti-pattern
type: anti-pattern
testable: true
graphable: false
---
# Hardcoded Credentials

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `password = "..."` or `passwd = "..."` assigned as string literals
- `api_key = "..."` or `apikey = "..."` in source files
- `secret = "..."` or `secret_key = "..."` as inline values
- `token = "sk-..."` or other provider-prefixed token strings
- AWS access keys in source (`AKIA` prefix in string literals)
- `.env` files committed to git (present in tracked files, not in `.gitignore`)
- `private_key` as a string literal or multi-line string in source
- `Authorization: Bearer` with a literal token value in code
- Database connection strings with embedded passwords (`postgresql://user:pass@host`)

### Confidence

- **high** -- literal `AKIA` prefix, `sk-` prefix, or `private_key` block found in tracked source files
- **medium** -- variables named `password`, `secret`, or `api_key` assigned string literals
- **low** -- `.env.example` contains real-looking values, or config files have placeholder secrets that look non-random

## Impact

Credential exposure in version control, enabling unauthorized access once the repository is cloned, forked, or leaked.

### Symptoms

- Secrets visible in git history even after deletion from HEAD
- Automated scanners (GitHub secret scanning, TruffleHog) firing alerts
- Credential rotation requires code changes and redeployment
- Shared repositories expose production credentials to all contributors
- Compromised credentials lead to lateral movement across services

### Remediation

- Move all secrets to environment variables or a secrets manager (`pass`, Vault, AWS Secrets Manager)
- Add `.env`, `*.pem`, and credential files to `.gitignore`
- Run `git-secrets` or `trufflehog` as a pre-commit hook to block commits containing secrets
- Rotate any credentials that have ever appeared in version control
- Reference secrets in Kubernetes manifests as `secretKeyRef`, never as inline `value`

See also: secret-management pattern

---
description: Hardcoded URLs anti-pattern
type: anti-pattern
testable: true
graphable: false
---
# Hardcoded URLs

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `http://localhost:8080` or `http://127.0.0.1` in production code paths
- `https://api.example.com` or domain-specific string literals in source files
- IP addresses embedded directly in source code (not config)
- URLs not sourced from config files, environment variables, or service discovery
- Hardcoded port numbers in connection strings outside of configuration
- API base URLs defined as constants in application code rather than injected configuration

### Confidence

- **high** -- a URL string literal containing a hostname or IP address appears in production code (not test fixtures), and there is no corresponding config/env var override mechanism
- **medium** -- URLs are defined as module-level constants in application code rather than read from environment variables or config files
- **low** -- `localhost` or `127.0.0.1` appears in code that might only run in development, but there is no environment-specific override

## Impact

Endpoints cannot be changed without a code deploy, and the application breaks when moving between environments (dev, staging, production).

### Symptoms

- Deploying to a new environment requires code changes instead of config changes
- Staging environment accidentally hits production services (or vice versa)
- Service URL changes require coordinated code deployments across multiple repositories
- Local development requires patching hardcoded URLs or running services on specific ports
- Feature branches cannot point to isolated test instances of dependencies

### Remediation

- Move all URLs and hostnames to environment variables or config files, with sensible defaults for local development only
- Use service discovery (DNS, Consul, Kubernetes service names) instead of hardcoded addresses
- Create a centralized configuration module that reads all external endpoints from the environment at startup
- Add a linting rule or grep check in CI that flags URL-like string literals in source files (excluding tests and documentation)
- For Kubernetes deployments, use ConfigMaps or environment variable injection rather than baked-in URLs

See also: config-management pattern

---
description: Health Check architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [lifecycle, observability]
---
# Health Check

## Recognition

How to identify this pattern in code.

### Signatures

- Endpoints: `/health`, `/healthz`, `/ready`, `/readyz`, `/live`, `/livez`, `/status`
- K8s probe definitions: `livenessProbe`, `readinessProbe`, `startupProbe` in pod specs
- Dependency health aggregation (checking database, cache, message queue connectivity)
- Health status enum or response: `UP`, `DOWN`, `DEGRADED`, `STARTING`
- Spring Boot Actuator `/actuator/health` with auto-configured health indicators
- Health check libraries or frameworks with pluggable health indicator registration

### Confidence

- **high** -- separate liveness and readiness endpoints with dependency checks, K8s probes configured, health status aggregation
- **medium** -- single `/health` endpoint returning 200 OK without checking dependencies
- **low** -- root endpoint (`/`) returning a response used informally as a health signal

## Architecture

Look for separate liveness and readiness probes with appropriate dependency health checks at each level.

### Review Checklist

- Liveness probe checks only process health (is the application alive), not dependency health
- Readiness probe checks dependency connectivity (can the application serve traffic)
- Startup probe is used for slow-starting applications to prevent premature liveness failures
- Probe timeouts and intervals are tuned to avoid false positives (not too aggressive)
- Health endpoints are not exposed publicly or are protected from abuse
- Dependency checks have their own timeouts (a slow database check does not hang the health endpoint)

### Anti-patterns

- Liveness probe checking external dependencies (database down kills healthy pods, cascading failure)
- Health endpoint that performs expensive operations (heavy queries, full connection tests on every call)
- No readiness probe (traffic routed to pods before they can handle requests)
- Same endpoint and logic for both liveness and readiness (they serve different purposes)

---
description: Hexagonal architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [architectural]
---
# Hexagonal (Ports & Adapters)

## Recognition

How to identify this pattern in code.

### Signatures

- `ports/` and `adapters/` directory structure separating interface definitions from implementations
- Interfaces or protocols with a `Port` suffix (`OrderRepositoryPort`, `NotificationPort`)
- Classes with an `Adapter` suffix implementing port interfaces (`PostgresOrderRepositoryAdapter`)
- Domain layer with no framework imports (no `requests`, `boto3`, `flask`, or DB driver imports)
- Explicit separation of "driving" (inbound) and "driven" (outbound) adapters
- Dependency injection wiring adapters to ports at application startup
- In-memory adapter implementations used in tests as port substitutes

### Confidence

- **high** -- `ports/` and `adapters/` directories with `Port`-suffixed interfaces and `Adapter`-suffixed implementations, domain layer free of infrastructure imports
- **medium** -- Driving/driven adapter separation with dependency injection, but without strict naming conventions
- **low** -- Domain layer isolated from infrastructure by convention, without explicit port interfaces or adapter directory structure

## Architecture

Look for clean separation between domain logic and infrastructure.

### Review Checklist

- Ports are defined as interfaces/protocols, not concrete classes
- Adapters implement exactly one port — no multi-port adapters
- Domain layer has zero imports from infrastructure packages
- Tests use in-memory adapters, not mocks of concrete classes

### Anti-patterns

- Domain code importing `requests`, `boto3`, or DB drivers directly
- "Port" interfaces that leak infrastructure details (SQL, HTTP headers)
- Adapter logic bleeding into domain services

---
description: Hidden Side Effects anti-pattern
type: anti-pattern
graphable: false
---
# Hidden Side Effects

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Functions that look pure (no indication in name or signature) but modify global state or module-level variables
- Methods that write files, send HTTP requests, or update a database without any hint in their name
- Functions that mutate their input arguments instead of returning new values
- `@property` decorators or getters that trigger I/O, database queries, or network calls
- Constructors (`__init__`, `constructor`) that perform network calls, file writes, or other I/O
- Functions named as queries (`find`, `get`, `calculate`) that also modify caches, counters, or logs with business meaning

### Confidence

- **high** -- a function with a query-like name (get, find, calculate) performs writes to a database, file system, or external service
- **medium** -- a function mutates its input arguments in place while also returning a value, making the mutation easy to miss
- **low** -- a function modifies module-level state (counters, caches) as a secondary effect that is arguably acceptable

## Impact

Unpredictable behavior and untestable code because callers cannot reason about what a function does based on its signature alone.

### Symptoms

- Tests require elaborate setup/teardown because "read" operations leave behind state changes
- Calling a function twice produces different results because the first call mutated hidden state
- Mocking is difficult because the function reaches out to external systems unexpectedly
- Debugging reveals that values changed "on their own" -- the mutation was hidden in an unrelated function
- Parallel execution breaks because functions that appeared safe to parallelize share hidden mutable state

### Remediation

- Make side effects explicit in the function name: `fetch_and_cache_user`, `calculate_and_log_total`
- Separate queries from commands: functions that return data should not modify state (CQS principle)
- Pass dependencies explicitly rather than reaching for globals: use dependency injection
- Make @property accessors trivial -- never perform I/O or heavy computation behind a property
- Document side effects in docstrings and type hints (e.g., `-> None` for functions that mutate in place)

---
description: Hydration — transferring server-rendered state to the client for interactive rendering
type: pattern
graphable: true
abstraction: [frontend, data]
---
# Hydration

## Recognition

How to identify this pattern in code.

### Signatures

- `dehydrate(queryClient)` and `HydrationBoundary` or `Hydrate` component (TanStack Query)
- `hydrateRoot` replacing `createRoot` for server-rendered HTML (React 18+)
- `ReactDOM.hydrate` for attaching to server-rendered markup (React pre-18)
- `createSSRApp` instead of `createApp` for server-side rendered Vue applications (Vue)
- `TransferState` and `makeStateKey` for transferring state from server to client (Angular)
- `useId()` for generating stable IDs that match between server and client renders
- `__NEXT_DATA__` script tag containing serialized page props (Next.js)
- `window.__NUXT__` payload containing server-fetched state (Nuxt)
- `<script>` tags with `type="application/json"` or data attributes containing serialized state in SSR output
- Hydration mismatch warnings in console: "Text content did not match", "Hydration failed"
- `suppressHydrationWarning` prop on elements with expected mismatches (React)

### Confidence

- **high** -- Framework SSR hydration API (hydrateRoot, createSSRApp, TransferState) with serialized state embedded in HTML and client-side rehydration consuming it
- **medium** -- Server-rendered HTML with inline JSON state that client JavaScript reads on load to initialize components, but without formal hydration API
- **low** -- Any server-rendered page where client JavaScript reads embedded data attributes or hidden fields to bootstrap state

## Architecture

Look for a two-phase rendering process: server generates HTML with embedded state, client attaches event handlers and restores state without re-fetching or re-rendering from scratch.

### Review Checklist

- Server and client render the same component tree with the same data to avoid hydration mismatches
- Serialized state does not include sensitive data (auth tokens, internal IDs, PII) that should not be in HTML source
- Hydration errors are treated as bugs and fixed, not suppressed globally
- State serialization handles edge cases: undefined, Date objects, BigInt, circular references
- Hydration boundary is placed at the correct level so client-only components are excluded from server render
- Performance: serialized state payload size is monitored and kept reasonable

### Anti-patterns

- Suppressing all hydration warnings instead of fixing the root cause of server/client mismatches
- Serializing enormous data payloads into HTML, bloating document size and time-to-interactive
- Client components that immediately refetch data already available in hydrated state
- Server render depending on browser-only APIs (window, document) causing mismatch or crash
- No hydration boundary around client-only components, causing server render to fail or diverge

---
description: Ice Cream Cone anti-pattern
type: anti-pattern
graphable: false
---
# Ice Cream Cone

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `test/e2e` or `tests/integration` directory much larger than `test/unit` or `tests/unit`
- Many Selenium, Playwright, or Cypress tests with few corresponding unit tests
- Test runtime dominated by integration or end-to-end tests (CI taking 30+ minutes)
- Inverted test pyramid: more high-level tests than low-level tests
- Test configuration heavily focused on browser setup, Docker Compose, or service orchestration
- Minimal use of mocks or stubs; most tests hit real databases or services
- `conftest.py` or test fixtures primarily spinning up full application stacks

### Confidence

- **high** -- e2e test count exceeds unit test count by 2x or more, and CI runtime is dominated by integration tests
- **medium** -- test/e2e directory has more files than test/unit, or CI regularly exceeds 20 minutes due to integration tests
- **low** -- the project has integration tests but few unit tests, though the codebase may be small enough that this is intentional

## Impact

Slow CI, flaky tests, and poor fault isolation because the test suite is top-heavy with expensive, broad-scoped tests.

### Symptoms

- CI pipelines take 30+ minutes, slowing development feedback loops
- Flaky test failures are common because end-to-end tests are sensitive to timing and environment
- When a test fails, it is difficult to pinpoint the exact module or function at fault
- Developers skip running tests locally because they are too slow
- Test maintenance burden is high due to brittle UI or integration test selectors

### Remediation

- Adopt the test pyramid: many unit tests, fewer integration tests, fewest end-to-end tests
- Convert broad integration tests to focused unit tests with mocks at service boundaries
- Reserve end-to-end tests for critical user journeys only (login, checkout, core workflows)
- Set CI time budgets and track test-level timing to identify slow tests for conversion
- Introduce contract tests (Pact, Schemathesis) to replace service-to-service integration tests

---
description: Idempotent Consumer architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [data, resilience, messaging]
---
# Idempotent Consumer

## Recognition

How to identify this pattern in code.

### Signatures

- Message ID deduplication before processing
- `processed_ids` set or table tracking already-handled messages
- Check-before-process pattern (lookup then conditionally execute)
- Idempotency keys in HTTP APIs
- `Idempotency-Key` header in request/response handling
- Upsert (`INSERT ... ON CONFLICT`) instead of plain insert
- Deduplication stores with TTL expiry
- Database table named `inbox`, `processed_messages`, or `received_events`
- `message_id` column with a uniqueness constraint used for deduplication
- `INSERT ... ON CONFLICT DO NOTHING` for idempotent message recording in an inbox table
- Consumer that writes the message ID to the inbox table in the same transaction as the business logic

### Confidence

- **high** -- `processed_ids` table/set combined with message ID lookup before processing, or `Idempotency-Key` header handling with stored results
- **medium** -- Upsert patterns in message handlers, or conditional inserts gated on existence checks
- **low** -- Generic duplicate checks without explicit idempotency infrastructure

## Architecture

Look for message deduplication at the consumer boundary with persistent tracking of processed IDs.

### Review Checklist

- Deduplication store is durable (survives restarts) and not just in-memory
- TTL or cleanup strategy exists to prevent unbounded growth of processed ID sets
- Idempotency check and processing happen atomically or within the same transaction
- Duplicate detection returns the original result, not an error
- Late or redelivered messages are handled gracefully (no side-effect replay)

### Database-Backed Variant (Inbox Table)

In the inbox variant, a dedicated database table (`inbox`, `processed_messages`, or `received_events`) provides the deduplication store. A `message_id` column with a uniqueness constraint enforces dedup at the database level. The consumer writes the message ID to the inbox table in the same transaction as the business logic, guaranteeing atomicity. This pairs with at-least-once delivery semantics from the message broker (Kafka, RabbitMQ, SQS).

Key review points for the inbox variant:
- Message ID uniqueness is enforced at the database level (unique constraint or index)
- Dedup check and business logic execute in the same database transaction
- Inbox records are retained long enough to cover the broker's redelivery window
- Old inbox entries are periodically cleaned up to prevent unbounded table growth
- Processing failures do not insert into the inbox (message can be retried)

### Anti-patterns

- In-memory-only deduplication sets that lose state on restart
- Check-then-act without atomicity (race condition between duplicate check and processing)
- Unbounded growth of the processed ID store with no expiry or compaction
- Treating duplicates as errors instead of silently returning the original result
- Inbox insert committed before business logic completes (message marked as processed but work not done)
- Relying solely on the broker's exactly-once semantics instead of application-level idempotency

---
description: Immutable Infrastructure architectural pattern
type: pattern
distributed: true
graphable: true
abstraction: [deployment, infrastructure]
---
# Immutable Infrastructure

## Recognition

How to identify this pattern in code.

### Signatures

- Dockerfiles building application images with all dependencies baked in
- Packer templates (`.pkr.hcl`, `packer.json`) producing machine images (AMIs, GCE images)
- No SSH-based configuration management (no Ansible playbooks running against live servers)
- Image tags pinned to specific versions or commit SHAs, not `latest`
- Replace-not-patch deployment strategy (terminate old instances, launch new ones)
- No in-place update scripts or hot-patching mechanisms in production

### Confidence

- **high** -- image build pipeline producing versioned artifacts, deployments always replace instances with new images, no remote shell access
- **medium** -- containerized deployments with immutable image tags but occasional `kubectl exec` for debugging
- **low** -- Docker images are built but `latest` tags are used or containers are patched in place

## Architecture

Look for a build-once-deploy-everywhere pipeline where running instances are never modified after creation.

### Review Checklist

- Images are versioned with immutable tags (commit SHA or semantic version, never `latest`)
- No mechanism exists to modify running instances (no SSH, no remote exec in production)
- Configuration is injected at startup via environment variables or mounted config, not baked into the image
- Rollback means deploying a previous known-good image version, not reverting changes on a live instance
- Image build is reproducible (pinned base images, locked dependency versions)

### Anti-patterns

- Using `latest` tag allowing the same tag to reference different image contents
- SSH access to production instances for ad-hoc patching or configuration changes
- Baking environment-specific secrets or configuration into the image itself
- In-place updates via `kubectl exec` or remote script execution on running containers

---
description: Inbox architectural pattern
graphable: true
abstraction: [messaging, data, resilience]
---
# Inbox

## Recognition

How to identify this pattern in code.

### Signatures

- Database table named `inbox`, `processed_messages`, or `received_events`
- `message_id` column with a uniqueness constraint used for deduplication
- Check-before-process logic: query for existing `message_id` before handling the message
- `INSERT ... ON CONFLICT DO NOTHING` or equivalent upsert for idempotent message recording
- Consumer that writes the message ID to the inbox table in the same transaction as the business logic
- At-least-once delivery semantics from the message broker (Kafka, RabbitMQ, SQS)

### Confidence

- **high** -- Dedicated inbox table with `message_id` uniqueness constraint, dedup check before processing, and processing within a single transaction
- **medium** -- Message ID tracked in a general-purpose table or cache for deduplication, but not in the same transaction as business logic
- **low** -- Consumer code that checks "have I seen this before" using in-memory state or a cache with TTL

## Architecture

Look for idempotent message processing using a persistent deduplication table keyed on message ID.

### Review Checklist

- Message ID uniqueness is enforced at the database level (unique constraint or index)
- Dedup check and business logic execute in the same database transaction
- Inbox records are retained long enough to cover the broker's redelivery window
- Old inbox entries are periodically cleaned up to prevent unbounded table growth
- Processing failures do not insert into the inbox (message can be retried)

### Anti-patterns

- Deduplication based on in-memory sets or caches that lose state on restart
- Inbox insert committed before business logic completes (message marked as processed but work not done)
- No TTL or cleanup -- inbox table grows indefinitely
- Relying solely on the broker's exactly-once semantics instead of application-level idempotency

---
description: Inconsistent Naming anti-pattern
type: anti-pattern
graphable: false
---
# Inconsistent Naming

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Mix of camelCase and snake_case in the same file or module
- Same concept referred to by different names: `user`/`usr`/`u`, `config`/`conf`/`cfg`/`settings`
- Inconsistent pluralization: `get_users()` returns one user, `fetch_item()` returns a list
- Abbreviations used inconsistently: `repo` in one file, `repository` in another for the same thing
- Boolean variables lacking `is_`/`has_`/`should_` prefix in some places but not others
- Event names mixing tenses: `userCreated`, `deleteUser`, `onUpdatingProfile`

### Confidence

- **high** -- the same file contains both camelCase and snake_case for non-FFI code, or the same entity has 3+ different names across the codebase
- **medium** -- two modules use different names for the same domain concept (e.g., `order` vs `purchase`)
- **low** -- minor abbreviation inconsistencies across distant parts of the codebase

## Impact

Cognitive overhead increases for every reader, and text searches miss relevant code because the same concept has multiple spellings.

### Symptoms

- grep/search for a concept misses half the relevant code because of alternate names
- New contributors introduce yet another variant because they copy from different parts of the codebase
- Refactoring tools fail to catch all references because names diverge
- Code reviews repeatedly flag naming nits, wasting review cycles
- Auto-generated documentation looks incoherent with mixed conventions

### Remediation

- Establish a project glossary mapping domain concepts to their one canonical name
- Configure linters to enforce a single casing convention per language (e.g., snake_case for Python, camelCase for JavaScript)
- Run a codebase-wide rename to unify existing divergent names
- Add naming conventions to the contribution guide and enforce in CI
- Use IDE refactoring tools rather than find-and-replace to catch all references safely

---
description: Infrastructure as Code architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [infrastructure, deployment]
---
# Infrastructure as Code

## Recognition

How to identify this pattern in code.

### Signatures

- Declarative infrastructure definitions in version-controlled files
- Terraform `.tf` files with `resource`, `data`, and `module` blocks
- Pulumi programs defining infrastructure in a general-purpose language
- CloudFormation templates (`.yaml`/`.json` with `AWSTemplateFormatVersion`)
- Ansible playbooks and roles (`tasks/main.yml`, `playbook.yml`)
- `terraform plan`, `terraform apply`, `pulumi up` in CI/CD pipelines
- State files (`terraform.tfstate`, `pulumi.stack.json`)
- Resource definitions with explicit dependencies and lifecycle rules

### Confidence

- **high** -- all infrastructure defined in versioned declarative files with automated apply via CI/CD
- **medium** -- infrastructure files exist but some resources are still created manually or out of band
- **low** -- scripts that call cloud APIs imperatively but are version-controlled

## Architecture

Look for all infrastructure defined declaratively in version control with automated, reproducible provisioning.

### Review Checklist

- All infrastructure is defined in code -- no manually created resources outside the IaC scope
- State is stored remotely with locking (S3+DynamoDB, GCS, Terraform Cloud)
- Changes go through plan/review before apply -- no direct `apply` without review
- Secrets are not stored in IaC files -- referenced via secret manager or external store
- Modules are used to avoid duplication across environments
- Drift detection is in place to catch out-of-band changes

### Anti-patterns

- State file committed to git or stored locally without locking
- Hardcoded secrets or credentials in `.tf` or template files
- No plan step -- applying changes directly without previewing the diff
- Snowflake environments with copy-pasted configs instead of parameterized modules

---
description: Input Validation architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [security, api]
---
# Input Validation

## Recognition

How to identify this pattern in code.

### Signatures

- Schema validation at the API boundary before business logic executes
- `pydantic` BaseModel with field validators (Python)
- `joi` or `zod` schemas (JavaScript/TypeScript)
- `@Valid` or `@Validated` annotations (Java/Spring)
- `marshmallow` or `cerberus` schema definitions (Python)
- Request validation middleware in the HTTP pipeline
- HTML input sanitization (DOMPurify, bleach)
- SQL parameterized queries (`?` placeholders, `$1` bind parameters)

### Confidence

- **high** -- dedicated validation schemas on all API endpoints with reject-on-invalid behavior
- **medium** -- validation present on some endpoints but inconsistent coverage across the API surface
- **low** -- inline type checks or assertions scattered through business logic instead of boundary validation

## Architecture

Look for validation enforced at system boundaries with reject-early semantics.

### Review Checklist

- All external input is validated at the API boundary before reaching business logic
- Validation schemas are declarative and co-located with the endpoint definition
- Error responses include specific field-level validation messages
- String inputs are sanitized for injection (SQL, XSS, command injection)
- Numeric and collection inputs have bounds (min/max, max length)
- Validation logic is not duplicated between client and server -- server is authoritative

### Anti-patterns

- Validation scattered deep in business logic instead of at the boundary
- Trusting client-side validation as the only check
- Generic "invalid input" errors with no indication of which field or why
- String concatenation for SQL or shell commands instead of parameterization

---
description: Insecure Deserialization anti-pattern
type: anti-pattern
testable: true
graphable: false
---
# Insecure Deserialization

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `pickle.loads()` on untrusted or network-received input
- `eval()` or `exec()` used to parse data or configuration
- `yaml.load()` without `Loader=SafeLoader` (defaults to unsafe loader in older PyYAML)
- `unserialize()` in PHP on user-supplied data
- `JSON.parse()` on user input without schema validation
- `marshal.load()` or `shelve.open()` on untrusted files
- Java `ObjectInputStream.readObject()` on network streams
- `jsonpickle.decode()` on external input
- `__reduce__` or `__setstate__` methods in classes used with pickle

### Confidence

- **high** -- `pickle.loads()`, `eval()`, or `exec()` called directly on request body, file upload, or message queue payload
- **medium** -- `yaml.load()` without explicit SafeLoader, or `unserialize()` on data from a database column populated by users
- **low** -- `JSON.parse()` on external input without validation, or deserialization libraries used but input provenance is unclear

## Impact

Remote code execution through crafted payloads that exploit deserialization to run arbitrary commands on the server.

### Symptoms

- Unexpected process spawning or outbound network connections from the application
- Crash or exception traces referencing deserialization methods with malformed input
- Security scanner alerts for unsafe deserialization functions
- Unexplained file system modifications in the application directory
- Audit logs showing operations the application should not perform

### Remediation

- Replace `pickle` with JSON or MessagePack for data interchange
- Replace `yaml.load()` with `yaml.safe_load()` or `yaml.load(data, Loader=SafeLoader)`
- Never use `eval()` or `exec()` on external input; use `ast.literal_eval()` for Python literals
- Validate deserialized data against a schema (Pydantic, JSON Schema, dataclasses)
- Apply allowlist-based type checking before deserialization in Java (`ObjectInputFilter`)

---
description: Intermediate Representation (IR) architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [data, compiler]
---
# Intermediate Representation (IR)

## Recognition

How to identify this pattern in code.

### Signatures

- Lowered representation sitting between the AST (source) and final output (machine code, bytecode, target language)
- Static Single Assignment (SSA) form: each variable assigned exactly once, with phi nodes at control flow joins
- Basic blocks containing sequential instructions, connected by control flow edges
- IR passes: optimization, lowering, analysis passes that transform or inspect the IR
- `IRBuilder` or `emit()` methods constructing IR instructions from higher-level AST nodes
- Three-address code format: `result = op left right`
- Bytecode emission as a compact IR targeting a virtual machine
- Libraries/frameworks: LLVM IR, Cranelift, MLIR, WebAssembly, JVM bytecode, Python bytecode

### Confidence

- **high** — SSA-form instructions in basic blocks with optimization passes and an `IRBuilder` or `emit()` API
- **medium** — basic block graph with typed instructions, explicit control flow edges, and at least one transform pass
- **low** — flattened instruction list with opcodes emitted from an AST without structured basic blocks

## Architecture

Look for a structured intermediate form that enables optimization and analysis between parsing and code generation.

### Review Checklist

- IR is well-typed: every value and instruction carries a type, enabling type-based optimizations
- Basic blocks have a single entry point and single exit (branch/return), forming a proper CFG
- Optimization passes are composable and order-independent where possible (pass manager)
- IR-to-source mapping is preserved for debuggability (debug info, source locations)
- Lowering from AST to IR is a separate, testable phase (not interleaved with parsing)
- IR can be serialized and deserialized for caching, separate compilation, or debugging

### Anti-patterns

- AST used directly as the optimization target instead of lowering to a simpler IR first
- Optimization passes that mutate shared IR state without proper invalidation of analysis results
- No type system on the IR, allowing ill-typed instructions to reach code generation
- Monolithic lowering pass that converts AST to final output with no intermediate form

---
description: Iterator architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Iterator

## Recognition

How to identify this pattern in code.

### Signatures

- Python: `__iter__()` / `__next__()` protocol, `yield` generators, `itertools` usage
- JS/TS: `Symbol.iterator`, `next()` returning `{ value, done }`, generators with `function*`/`yield`
- Rust: `Iterator` trait with `next()` returning `Option<Item>`, `IntoIterator`, iterator adaptors
- Go: `for range` over channels, iterator functions returning `func() (T, bool)`
- Java: `Iterator<T>` interface, `Iterable<T>`, `Stream` API
- Lazy evaluation: `itertools.chain`, `map`/`filter`/`reduce` chains, `Stream.of().filter().map()`

### Confidence

- **high** -- class implementing the iterator protocol (`__iter__`/`__next__` or `Iterator` trait) with lazy element production
- **medium** -- generator function using `yield` to produce elements on demand
- **low** -- method returning a list that could be lazy but is eagerly evaluated

## Architecture

Look for lazy evaluation and separation of traversal logic from the underlying collection.

### Review Checklist

- Iterator is lazy (elements produced on demand, not pre-computed into a list)
- Iterator protocol is correctly implemented (raises `StopIteration` / returns `None` at end)
- External iteration does not expose collection internals (no index-based access to backing store)
- Iterator supports composition (map, filter, chain) without materializing intermediate collections
- Resource cleanup on early termination (generators with cleanup in `finally`, `__del__`, or context manager)

### Anti-patterns

- Eagerly loading entire dataset into memory when lazy iteration would suffice
- Iterator that mutates the underlying collection during traversal
- Missing `StopIteration` / end signal causing infinite loops
- Custom iterator reimplementing what standard library itertools already provides

---
description: Key-value domain model — simple key→value lookups with optional expiry
type: domain-model
abstraction: [data]
---
# Key-Value

## Recognition

### Signatures

- Redis, Memcached, DynamoDB, etcd, or Consul as primary data store
- Data accessed exclusively by key — no complex queries or joins
- TTL/expiry on entries
- Cache patterns: get-or-set, cache-aside, write-through
- Session storage keyed by session ID
- Feature flags keyed by flag name
- Configuration storage keyed by config path
- Atomic operations: increment, compare-and-swap, SETNX

### Confidence

- **high** — key-value store as primary data model with TTL, atomic ops, and no relational queries
- **medium** — Redis/Memcached used as cache layer alongside a relational primary store
- **low** — dictionary/map data structures used extensively in code but no external KV store

---
description: Lava Flow (Dead Code) anti-pattern
type: anti-pattern
graphable: false
---
# Lava Flow (Dead Code)

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Commented-out code blocks left in the source
- Unreachable branches (conditions that can never be true, code after unconditional returns)
- Unused imports and variables (flagged by linters but ignored)
- Comments containing `# TODO: remove`, `# HACK`, `# FIXME: delete this`, or `# no longer used`
- Functions or methods called from nowhere in the codebase
- `@deprecated` annotations with no replacement timeline or migration path
- Feature flags that were never cleaned up after rollout

### Confidence

- **high** -- functions with zero callers, commented-out code blocks exceeding 10 lines, unreachable branches confirmed by static analysis
- **medium** -- `@deprecated` without a removal date, TODO comments referencing removal, unused imports
- **low** -- code that appears to duplicate functionality elsewhere, suspiciously old unchanged files in active directories

## Impact

Increases codebase size, confuses readers about what is live, and produces false positives in grep results.

### Symptoms

- Grepping for a function name returns dead code alongside live code, slowing investigation
- New developers attempt to use deprecated APIs because they appear available
- Test coverage reports show untestable dead branches dragging down metrics
- Build times and artifact sizes grow without delivering new value
- Refactoring hesitates because nobody knows if the "unused" code is actually needed somewhere

### Remediation

- Run static analysis tools to identify unreachable code and unused symbols
- Delete commented-out code -- it lives in version control history if ever needed
- Enforce `@deprecated` annotations with a removal-by date and track them in a backlog
- Add linter rules that fail on unused imports, variables, and unreachable code
- Schedule regular dead-code sweeps as part of maintenance sprints

---
description: Layered structure — horizontal layers with dependency flowing downward
type: structure-shape
abstraction: [architectural]
---
# Layered

## Recognition

### Signatures

- Directory structure: `presentation/` or `api/` → `service/` or `domain/` → `repository/` or `data/`
- Import rules: upper layers import lower layers, never reverse
- Controller → Service → Repository class pattern
- N-tier separation: web tier, application tier, data tier
- Django apps with `views.py` → `services.py` → `models.py`
- Spring `@Controller` → `@Service` → `@Repository` annotations
- Clean Architecture rings: entities → use cases → adapters → frameworks
- Layer-enforcing lint rules or architecture test frameworks (ArchUnit, import-linter)

### Confidence

- **high** — explicit layer directories with enforced import rules (lint or architecture tests preventing upward dependencies)
- **medium** — conventional layered structure but without enforcement (some cross-layer imports exist)
- **low** — code organized by feature/module rather than layer, but individual modules internally use layers

---
description: Lazy Loading — deferring component or module loading until needed to reduce initial bundle size
type: pattern
testable: true
graphable: true
abstraction: [frontend, deployment]
---
# Lazy Loading

## Recognition

How to identify this pattern in code.

### Signatures

- `React.lazy(() => import(...))` and `<Suspense>` wrapper (React)
- `defineAsyncComponent(() => import(...))` (Vue)
- `loadChildren: () => import(...)` in route config (Angular)
- Dynamic `import()` expressions in route definitions
- Webpack magic comments (`/* webpackChunkName */`)
- Vite's automatic code splitting on dynamic imports
- `next/dynamic` (Next.js)
- Route-based splitting: each route in its own chunk

### Confidence

- **high** -- `React.lazy` or `defineAsyncComponent` with `Suspense`/loading boundary, visible chunk splitting in build output
- **medium** -- dynamic `import()` in route config but no explicit loading states
- **low** -- framework handles splitting automatically (e.g., Next.js pages) with no explicit lazy boundaries

## Architecture

Look for deferred loading of components or modules via dynamic imports, with loading state management and chunk optimization for the critical rendering path.

### Review Checklist

- Loading boundaries wrap lazy components with meaningful fallback UI (skeleton, spinner)
- Error boundaries catch failed chunk loads (network errors)
- Critical above-the-fold content is NOT lazy loaded
- Route-level splitting at minimum; component-level splitting for heavy widgets
- Preload hints for likely-needed chunks (`<link rel="prefetch">`)

### Anti-patterns

- Lazy loading everything including tiny components (overhead exceeds savings)
- No fallback UI -- user sees blank space during load
- No error handling for failed chunk loads (stale deployment, network failure)
- Splitting too granularly -- hundreds of tiny chunks increase HTTP request overhead

---
description: Leader Election architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [concurrency, resilience]
---
# Leader Election

## Recognition

How to identify this pattern in code.

### Signatures

- Leader/follower role assignment logic with election protocol
- K8s `Lease` objects used for leader election (`coordination.k8s.io/v1` API)
- etcd-based election using key TTL and compare-and-swap
- ZooKeeper sequential ephemeral nodes for election recipes
- Only-leader-writes pattern (followers redirect or reject write operations)
- Leader health monitoring with automatic re-election on failure
- Libraries: `client-go/tools/leaderelection`, `curator` (ZooKeeper), `etcd/clientv3/concurrency`

### Confidence

- **high** -- explicit leader election protocol with Lease/lock objects, leader-only execution paths, and automatic failover
- **medium** -- single-writer pattern with a lock mechanism but no formal election protocol or follower behavior
- **low** -- application runs as a single replica to avoid concurrency (implicit leader by deployment constraint)

## Architecture

Look for a correct election protocol with leader fencing and graceful failover to a follower on leader loss.

### Review Checklist

- Leader lease has a TTL and is renewed periodically (stale leaders are detected)
- Fencing tokens or epoch numbers prevent split-brain (old leader cannot act after losing leadership)
- Followers detect leader failure and trigger re-election within an acceptable time window
- Leader performs graceful handoff when shutting down (releases lease proactively)
- Election state is observable (metrics or logs indicating current leader identity and transitions)

### Anti-patterns

- No fencing mechanism allowing two nodes to believe they are leader simultaneously (split-brain)
- Leader lease TTL too long (slow failover) or too short (frequent unnecessary re-elections)
- Business logic assumes leader identity is permanent (no handling of leadership loss mid-operation)
- Using a single replica instead of proper election (no fault tolerance)

---
description: Leaky Abstraction anti-pattern
type: anti-pattern
graphable: false
---
# Leaky Abstraction

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Implementation details in interface signatures (SQL fragments in repository method names, HTTP headers in domain object fields, file paths in service interfaces)
- Callers catching implementation-specific exceptions through abstraction layers (e.g., catching `psycopg2.IntegrityError` when calling a repository method)
- Domain objects containing serialization-specific annotations (JSON tags, ORM column mappings) that tie them to a particular storage or transport mechanism
- Callers needing to know about internal state or call methods in a specific order for the abstraction to work correctly
- "Pass-through" methods that expose every parameter of the underlying implementation

### Confidence

- **high** -- SQL in repository method signatures, infrastructure exceptions leaking through domain boundaries, callers must understand the implementation to use the abstraction correctly
- **medium** -- domain objects carry ORM or serialization annotations, method parameters mirror the underlying library's API 1:1
- **low** -- abstraction works but its naming or structure hints at the implementation behind it (e.g., `RedisCache` instead of `Cache`)

## Impact

The abstraction provides no real isolation, so changes to the underlying implementation ripple through all callers.

### Symptoms

- Swapping the underlying implementation requires changing callers despite the abstraction layer
- Callers contain defensive code that handles quirks of the specific implementation behind the abstraction
- Domain model cannot be understood without knowing the database schema or API format
- Tests for higher layers break when lower-layer implementation details change
- The abstraction's interface grows to mirror the underlying library's full API surface

### Remediation

- Define interfaces in terms of domain concepts, not implementation mechanisms (e.g., `find_active_users()` not `query("SELECT * FROM users WHERE active = true")`)
- Translate implementation-specific exceptions into domain exceptions at the boundary
- Separate domain models from persistence models: map between them at the adapter layer
- Apply the Interface Segregation Principle: expose only what callers need, not everything the implementation can do
- Test the abstraction boundary: verify that callers work with any conforming implementation, not just the current one

---
description: Double-entry ledger pattern for financial data integrity
type: pattern
category: domain-model
abstraction: [data, financial]
---
# Ledger

## Recognition

How to identify this pattern in code.

### Signatures

- `debit` and `credit` columns or fields appearing in the same table/model
- `JournalEntry`, `LedgerEntry`, or `GeneralLedger` class definitions
- `balance` computed by summing debits and credits: `SUM(debit) - SUM(credit)`
- `double_entry` or `double_entry_bookkeeping` in module or function names
- Python: `hledger`, `beancount`, `ledger` library usage
- JS/TS: `medici` library, `journal` collection with debit/credit documents
- Go: `debit Amount` and `credit Amount` struct fields, `PostTransaction` methods
- Rust: `debit: Decimal`, `credit: Decimal` in transaction structs
- Java: `@Column(name = "debit")` and `@Column(name = "credit")` JPA annotations
- SQL: `GL` table prefix, `journal_entry` table, `account_id` foreign key on entries

### Confidence

- **high** -- JournalEntry or LedgerEntry class with paired debit/credit fields and a balance invariant check ensuring debits equal credits per transaction
- **medium** -- Separate debit and credit columns in a financial table with immutable insert-only entries
- **low** -- A single `amount` field with a `type` enum of debit/credit, without explicit balance verification

## Architecture

### When to use
- Financial systems requiring auditability and provable correctness
- Any domain where money moves between accounts and balances must reconcile
- Systems subject to regulatory or compliance requirements on transaction records

### Anti-patterns
- Storing only a running balance without the underlying journal entries, making reconciliation impossible
- Mutable ledger entries that can be updated in place instead of appending correcting entries
- Mixing business logic with ledger posting — the ledger should record facts, not enforce rules

### Complements
- [event-sourcing](/concepts/event-sourcing) — ledger entries are naturally append-only events
- [audit-logging](/concepts/audit-logging) — financial records require audit trails
- [saga](/concepts/saga) — multi-account transfers may need saga coordination

## Impact

A double-entry ledger provides a self-balancing system of record. When present, testing must verify the balance invariant (total debits == total credits) on every transaction, and monitoring should alert on any imbalance as a critical data integrity failure.

---
description: Lexer/Parser architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design, compiler]
---
# Lexer/Parser

## Recognition

How to identify this pattern in code.

### Signatures

- Two-phase processing: tokenization (lexer/scanner) followed by parsing into a tree structure
- `Token` type or enum with variants like `Identifier`, `Number`, `StringLiteral`, `Keyword`
- `Lexer` or `Scanner` class with `next_token()`/`scan()` methods consuming character input
- `Parser` class producing an AST from a token stream
- `peek()`, `advance()`, `expect()`, `consume()` methods on the parser
- Grammar rules encoded as recursive descent functions or parser combinators
- Libraries: ANTLR, tree-sitter, pest (Rust), PLY (Python), nom (Rust), yacc/bison, PEG.js, pyparsing

### Confidence

- **high** — `Lexer`/`Scanner` class producing `Token` values consumed by a `Parser` with `peek()`/`advance()`/`expect()` methods
- **medium** — token enum with keyword and operator variants, plus recursive functions matching grammar productions
- **low** — string splitting into labeled chunks followed by structured interpretation of the chunks

## Architecture

Look for clean separation between lexical analysis (characters to tokens) and syntactic analysis (tokens to tree).

### Review Checklist

- Lexer handles all whitespace, comments, and string escaping before tokens reach the parser
- Token types carry source location (line, column) for error reporting
- Parser methods map one-to-one to grammar productions for readability
- Error recovery produces useful messages with source location, not just "unexpected token"
- Lexer and parser are independently testable (token stream tests, parse tree tests)
- Grammar is unambiguous or ambiguities are resolved with explicit precedence rules

### Anti-patterns

- Parser operating directly on raw characters instead of a token stream (mixed concerns)
- No source location tracking, making error messages useless for users
- Deeply nested recursive descent with no precedence climbing (stack overflow on expressions)
- Grammar rules scattered across unrelated modules instead of grouped by language construct

---
description: Log and Throw anti-pattern
type: anti-pattern
graphable: false
---
# Log and Throw

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `logger.error(e); raise e` or `catch(e) { log(e); throw e; }` in the same block
- Same exception logged at multiple layers as it propagates up the call stack
- Duplicate error entries in logs for a single failure, differing only by the logging class name
- `catch` blocks that log the full stack trace and then rethrow the same exception unchanged
- Error counts in monitoring dashboards that are multiples of actual failure occurrences

### Confidence

- **high** -- a catch block both logs the exception at error level and rethrows it, and callers do the same
- **medium** -- a catch block logs the exception and rethrows, but only one layer in the call stack does this
- **low** -- a catch block logs at warn/info level and rethrows, which may be intentional for tracing

## Impact

Log noise multiplies, error counts become meaningless, and operators waste time correlating duplicate entries for the same root failure.

### Symptoms

- A single user-facing error produces 3-5 identical log entries at different stack depths
- Error rate dashboards show inflated numbers that do not match actual incident counts
- On-call engineers waste time during incidents determining whether multiple log lines represent one failure or many
- Log storage costs increase due to redundant error messages
- Alert thresholds must be set artificially high to avoid false alarms from the inflated error counts

### Remediation

- Choose one: log the error OR rethrow it, not both at the same level
- Let exceptions propagate naturally and log them once at the boundary where they are handled (top-level handler, API middleware)
- If intermediate layers need to add context, wrap the exception in a new one with additional information instead of logging
- Use structured logging with correlation IDs so a single log entry at the boundary provides full traceability
- Audit the codebase for catch-log-rethrow patterns and remove the redundant log statements

---
description: Log Spam anti-pattern
type: anti-pattern
observable: true
graphable: false
---
# Log Spam

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `logger.info()` or `logger.debug()` inside `for`/`while` loops
- Log statements in hot paths (request handlers logging every field)
- Thousands of log lines per second from a single service
- No rate limiting on log events (`logger.warning()` called unconditionally on every request)
- Log level set to DEBUG in production configuration
- Logging full request/response bodies at INFO level

### Confidence

- **high** -- log statement inside a loop body that iterates over unbounded input, confirmed by log volume metrics exceeding 1k lines/sec per pod
- **medium** -- `logger.info()` or `logger.debug()` call inside a `for`/`while` loop without a conditional guard or sampling
- **low** -- log level set to DEBUG or TRACE in a production config file, or verbose logging enabled without a feature flag

## Impact

Log storage costs explode, Loki/ELK clusters are overwhelmed, and real signals are lost in noise.

### Symptoms

- Log aggregation system (Loki, Elasticsearch) experiences ingestion lag or drops
- Log storage costs grow disproportionately to traffic
- Searching logs for a specific error takes minutes because of volume
- Alerting on log patterns fires constantly due to noise
- Disk I/O pressure on nodes running log shippers

### Remediation

- Move debug-level logging behind a conditional or feature flag, never enable unconditionally in production
- Use structured logging with sampling for high-frequency events (`log every Nth` or probabilistic sampling)
- Replace per-iteration logging with a summary log after the loop (`processed N items in Xms`)
- Set appropriate log levels per environment: ERROR/WARN in production, DEBUG only in development
- Add rate limiting to log emitters for known high-volume paths

---
description: Long Polling architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [integration]
---
# Long Polling

## Recognition

How to identify this pattern in code.

### Signatures

- Client sends HTTP request, server holds it open until data is available or timeout expires
- Immediate re-request loop after receiving a response or timeout
- `timeout` parameter on server-side request handling (30s, 60s typical)
- Polling loop with configurable delay or immediate retry
- `setTimeout` or `setInterval` wrapping fetch/XHR calls on the client
- Fallback logic from WebSocket or SSE to long polling
- `ETag` or `If-None-Match` headers for change detection
- `304 Not Modified` responses when no new data is available

### Confidence

- **high** -- Server explicitly holds requests with a timeout, client immediately re-requests on completion
- **medium** -- Polling loop with a delay that adjusts based on server response
- **low** -- Periodic HTTP requests without explicit hold-and-wait semantics (may be simple polling)

## Architecture

Look for correct request lifecycle with timeout handling and efficient re-request logic.

### Review Checklist

- Server-side timeout is configured and does not hold connections indefinitely
- Client re-requests immediately after receiving data or a timeout response
- Error handling includes backoff to avoid hammering the server on failures
- Server can detect and clean up abandoned long-poll connections
- Response includes a version token or cursor so the client requests only new data

### Anti-patterns

- No timeout on the server side -- connections held open forever if no data arrives
- Fixed-interval polling disguised as long polling (missing the hold-until-data-available behavior)
- No backoff on errors -- client floods server with retries during outages
- Using long polling when WebSocket or SSE is available and supported by the client

---
description: Long Transactions anti-pattern
type: anti-pattern
observable: true
graphable: false
---
# Long Transactions

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Database transaction wrapping HTTP calls or external API calls
- `BEGIN` with no matching `COMMIT` for extended periods (visible in `pg_stat_activity` or slow query logs)
- `@transaction.atomic` or `@Transactional` around slow operations (file I/O, network requests, queue publishing)
- Lock wait timeouts appearing in application logs
- Transaction isolation level set to SERIALIZABLE without justification
- Connection checkout duration metrics showing long hold times

### Confidence

- **high** -- a database transaction block contains an HTTP request, external API call, or `sleep()`, confirmed by lock wait timeouts or connection pool exhaustion in production
- **medium** -- `@transaction.atomic` or `with transaction:` wraps a block that includes non-database I/O such as file writes, message publishing, or email sending
- **low** -- transaction boundaries span an entire request handler rather than being scoped to the specific database operations that require atomicity

## Impact

Connection pool exhaustion, deadlocks, and blocked queries that cascade into application-wide slowdowns.

### Symptoms

- Database connection pool is frequently exhausted under moderate load
- Deadlock errors appear in application or database logs
- Other queries are blocked waiting for locks held by long-running transactions
- Application latency spikes correlate with external service slowdowns (because the transaction holds while waiting)
- `idle in transaction` connections accumulate in the database

### Remediation

- Move external calls (HTTP, message publishing, file I/O) outside the transaction boundary
- Scope transactions to the minimum set of database operations that require atomicity
- Use the outbox pattern for operations that need both a database write and a message publish
- Set statement and idle-in-transaction timeouts at the database level (`idle_in_transaction_session_timeout`)
- Monitor transaction duration and alert on transactions exceeding a threshold (e.g., 5 seconds)

---
description: LRU Cache architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [data, infrastructure]
---
# LRU Cache

## Recognition

How to identify this pattern in code.

### Signatures

- `@lru_cache` or `functools.lru_cache` decorator in Python
- `LinkedHashMap` with `accessOrder=true` in Java
- `maxsize` or `capacity` parameter limiting cache entries
- Eviction of least-recently-used entry when cache is full
- Cache hit/miss tracking (`cache_info()`, hit rate metrics)
- `LRUCache`, `LruCache` class names or doubly-linked list + hash map combination
- `@Cacheable` with eviction policy in Spring
- Node.js `lru-cache` or `quick-lru` packages

### Confidence

- **high** -- Bounded cache with explicit LRU eviction, `maxsize` configuration, and hit/miss tracking
- **medium** -- `@lru_cache` decorator or `LinkedHashMap` usage without explicit eviction monitoring
- **low** -- Dictionary/map used as a cache with manual size checks that may implement LRU

## Architecture

Look for correct bounded caching with O(1) lookup and eviction, and appropriate cache invalidation.

### Review Checklist

- `maxsize` is tuned for the workload -- not set arbitrarily or left at defaults
- Cache keys are deterministic and produce consistent hashes for equivalent inputs
- Cache invalidation strategy exists (TTL, explicit invalidation, or versioned keys)
- Hit/miss ratio is tracked and observable via metrics or logging
- Mutable objects are not cached without defensive copies (aliasing bugs)
- Thread safety is addressed for concurrent access (thread-safe wrapper or per-thread caches)

### Anti-patterns

- Unbounded cache masquerading as LRU (missing `maxsize`, grows until OOM)
- Caching mutable objects that callers later modify (corrupted cache entries)
- No invalidation strategy -- stale data served indefinitely
- Using LRU cache for items with uniform access frequency (no temporal locality to exploit)

---
description: Magic Numbers/Strings anti-pattern
type: anti-pattern
graphable: false
---
# Magic Numbers/Strings

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Hardcoded numeric values with no explanation (`if count > 42`)
- Timeout or delay values inline with no named constant (`sleep(3.5)`)
- Array indices used as business logic (`data[7]` to mean "the address field")
- String literals used as identifiers or keys across multiple files without a shared definition
- Conditional thresholds with no documentation of why that specific value was chosen

### Confidence

- **high** -- numeric literals appear in business logic conditionals or configurations with no accompanying constant name or comment
- **medium** -- inline numeric values in function calls (timeouts, retries, sizes) without named constants
- **low** -- a single hardcoded value in a localized context that could reasonably be extracted but is not yet duplicated

## Impact

Unreadable code where the intent behind values is lost, making consistent changes across the codebase error-prone.

### Symptoms

- Developers cannot understand why a specific number was chosen without git archaeology
- Changing a business rule threshold requires finding and updating the same number in multiple locations
- Bugs arise from updating the value in one place but missing another occurrence
- Code reviews cannot assess correctness because the meaning of the number is opaque
- Tests embed the same magic values, creating brittle assertions coupled to unexplained constants

### Remediation

- Extract every non-obvious literal into a named constant with a descriptive name (`MAX_RETRY_ATTEMPTS = 3`)
- Group related constants in a dedicated configuration module or constants file
- Add a brief comment or docstring explaining the rationale when the value itself is not self-evident
- Use configuration files or environment variables for values that may differ across environments
- Add linting rules that flag raw numeric and string literals in conditional expressions and function arguments

---
description: MapReduce architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [data, concurrency]
---
# MapReduce

## Recognition

How to identify this pattern in code.

### Signatures

- Parallel map phase followed by a reduce/aggregate phase
- `map()` and `reduce()` applied over distributed or partitioned data
- Hadoop-style jobs with Mapper and Reducer classes
- Spark RDDs, `groupByKey()`, `reduceByKey()`, `aggregateByKey()`
- Batch computation frameworks splitting work into map and combine steps
- Shuffle/sort phase between map and reduce
- Partitioned input data with parallel worker execution

### Confidence

- **high** -- Explicit MapReduce job definition with separate Mapper and Reducer implementations, or Spark transformations ending in an action
- **medium** -- Data partitioned across workers with a map phase followed by aggregation, even without framework-specific APIs
- **low** -- A `map()` followed by `reduce()` on local data without distribution or parallelism

## Architecture

Look for correct data partitioning, idempotent map functions, and an associative/commutative reduce operation.

### Review Checklist

- Map function is pure and stateless -- same input always produces the same intermediate key-value pairs
- Reduce function is associative and commutative where required (combiner correctness)
- Data partitioning strategy avoids skew (no single reducer overwhelmed by a hot key)
- Intermediate data (shuffle) has bounded size or spill-to-disk strategy
- Job is idempotent -- re-running produces identical results
- Failure of individual map or reduce tasks triggers retry, not full job restart

### Anti-patterns

- Stateful map functions that depend on processing order or accumulate cross-record state
- All data funneled to a single reducer (defeats parallelism)
- No combiner when one is possible (unnecessary shuffle volume)
- Reduce logic that is not associative, producing different results depending on partition grouping

---
description: Materialized View architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [data]
---
# Materialized View

## Recognition

How to identify this pattern in code.

### Signatures

- `CREATE MATERIALIZED VIEW` in database migrations or schema definitions
- Pre-computed query results stored as denormalized tables or cache entries
- Refresh schedules: `REFRESH MATERIALIZED VIEW`, cron-triggered rebuild jobs
- Denormalized read models or projection tables in CQRS architectures
- View rebuild or refresh logic triggered by source data changes (event-driven or scheduled)
- Redis/Memcached entries populated from complex joins and served as flat lookups
- `CONCURRENTLY` refresh option to avoid locking during rebuilds

### Confidence

- **high** -- `CREATE MATERIALIZED VIEW` with a scheduled or event-driven refresh mechanism
- **medium** -- Denormalized projection tables populated by background workers from normalized source data
- **low** -- Cache layer storing computed aggregations that are periodically invalidated and rebuilt

## Architecture

Look for a clear separation between the source of truth and the materialized read model, with a defined refresh strategy.

### Review Checklist

- Source of truth and materialized view are clearly separated with a defined refresh mechanism
- Refresh strategy (scheduled, event-driven, or on-demand) is appropriate for the staleness tolerance
- Concurrent refresh is used where available to avoid blocking reads during rebuilds
- Monitoring tracks refresh duration, staleness age, and failure rate
- Fallback behavior is defined for when the view is stale or refresh fails (serve stale, query source, error)
- Indexes on the materialized view are optimized for the read queries it serves

### Anti-patterns

- No refresh mechanism, causing the materialized view to go stale indefinitely after initial creation
- Refreshing synchronously in the request path, adding latency to user-facing reads
- No monitoring on staleness, so consumers unknowingly serve outdated data
- Materialized view used as the source of truth with no way to rebuild from original data

---
description: Mediator architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design, integration]
---
# Mediator

## Recognition

How to identify this pattern in code.

### Signatures

- Central coordinator class: `Mediator`, `EventBus`, `Dispatcher`, `Hub`, `Broker`
- Components communicate through the mediator, never directly referencing each other
- Methods: `send()`, `publish()`, `dispatch()`, `notify()` on a central object
- Request/response mediation: `mediatr` (C#), `mediator-py`, command/query dispatching
- Python: `mediator` pattern with `handle()` registry, event bus with typed handlers
- JS/TS: centralized event bus, message broker classes, Angular services mediating components
- Go: hub struct that routes messages between registered participants

### Confidence

- **high** -- central mediator object with registered components that communicate exclusively through it
- **medium** -- event bus with publish/subscribe where the bus is the only coupling between components
- **low** -- shared service that multiple components depend on for coordination

## Architecture

Look for reduced coupling: components know the mediator, not each other.

### Review Checklist

- Components have no direct references to other components (only to the mediator)
- Mediator logic is coordination only, not business logic (thin mediator)
- Communication contracts (message types) are well-defined
- Mediator does not become a god object accumulating all coordination logic
- Error in one component's handler does not break mediation for others

### Anti-patterns

- God mediator that contains business logic instead of just routing messages
- Components bypassing the mediator for "convenience" (breaking the pattern)
- Mediator with implicit ordering dependencies between handlers
- Untyped message passing where handler registration is stringly typed

---
description: Memento architectural pattern
type: pattern
testable: true
graphable: false
abstraction: [design]
---
# Memento

## Recognition

How to identify this pattern in code.

### Signatures

- `save_state()` / `restore_state()` method pairs
- `createMemento()` / `setMemento()` on originator objects
- `undo_stack` / `redo_stack` data structures
- `deepcopy()` for state snapshots
- `Command` + state history in editors
- Caretaker class managing a list of mementos
- Serialized state checkpoints for rollback

### Confidence

- **high** -- Originator with `createMemento()`/`setMemento()` and a caretaker managing a stack of opaque state snapshots
- **medium** -- Undo/redo stack storing serialized state snapshots with restore capability
- **low** -- State serialization for persistence that resembles memento but lacks the undo/restore workflow

## Architecture

Look for an originator that creates opaque state snapshots managed by a caretaker for undo/restore operations.

### Review Checklist

- Memento is opaque to the caretaker (no direct access to internal state)
- Memory usage is bounded (limited history depth or incremental snapshots)
- Restore operation returns the originator to a fully valid state
- Concurrent access to the memento stack is synchronized if applicable
- Large state objects use incremental or compressed snapshots to control memory

### Anti-patterns

- Caretaker reaching into the memento to read or modify internal state
- Unbounded memento history consuming excessive memory
- Memento capturing references to external mutable objects instead of copying state
- Restoring state without validating that the memento is compatible with the current version

---
description: Memory Leak anti-pattern
type: anti-pattern
observable: true
graphable: false
---
# Memory Leak

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Event listeners never removed (`addEventListener` without corresponding `removeEventListener`)
- Growing dicts, lists, or caches in long-running processes without bounds or eviction
- Unclosed file handles, database connections, or network sockets (missing `close()`, `with`, or `using`)
- `__del__` relying on garbage collector timing for cleanup of external resources
- Circular references preventing garbage collection in reference-counted runtimes
- Global or module-level collections that accumulate entries over the process lifetime
- Timers or intervals (`setInterval`) that are never cleared

### Confidence

- **high** -- process RSS memory grows monotonically over hours/days under constant load, confirmed by heap dumps showing accumulation of specific object types
- **medium** -- event listeners are registered in a setup function but never deregistered, or a dict/list grows in a loop without bounds or TTL
- **low** -- resources are opened without a context manager or try-finally block, or `__del__` is used for cleanup of non-trivial resources

## Impact

OOM crashes in production, gradual performance degradation, and unpredictable restarts under sustained load.

### Symptoms

- Container or process memory usage grows steadily over time without recovering
- OOM kills appear in container orchestrator logs (Kubernetes OOMKilled)
- Garbage collection pauses become longer and more frequent
- Application response times degrade gradually after deployment until restart
- Heap dumps show unexpected retention of objects that should have been collected

### Remediation

- Use context managers (`with`, `using`, `try-finally`) for all resource acquisition to guarantee cleanup
- Remove event listeners in the corresponding teardown/unmount lifecycle (e.g., `useEffect` cleanup, `componentWillUnmount`)
- Bound all in-memory caches with a max size and TTL eviction policy (e.g., `functools.lru_cache`, `cachetools.TTLCache`)
- Profile memory in staging with tools like `tracemalloc`, Chrome DevTools heap snapshots, or `pprof` to detect leaks before production
- Avoid circular references or break them with `weakref` where the language runtime uses reference counting

---
description: Message Queue architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [messaging, infrastructure]
---
# Message Queue

## Recognition

How to identify this pattern in code.

### Signatures

- Point-to-point messaging: each message consumed by exactly one consumer
- Queue declarations with `queue_declare()`, `create_queue()`, or queue name configuration
- Acknowledgment/nack: `ack()`, `nack()`, `reject()`, visibility timeout
- Worker processes consuming from named queues
- Libraries: RabbitMQ, AWS SQS, Celery task queues, Bull/BullMQ, Sidekiq
- `@task` or `@job` decorators dispatching work to a queue
- Message serialization: JSON payloads, protobuf, or pickle

### Confidence

- **high** -- named queue with explicit produce/consume, ack/nack, and single-delivery semantics
- **medium** -- task decorator dispatching to a background worker framework
- **low** -- in-process job queue or thread pool with a task list

## Architecture

Look for point-to-point message delivery with explicit acknowledgment ensuring each message is processed once.

### Review Checklist

- Messages are acknowledged only after successful processing (not before)
- Failed messages are retried with backoff before being dead-lettered
- Message payload is self-contained (consumer does not need to fetch additional context)
- Queue depth is monitored and alerts fire on sustained growth
- Consumer idempotency handles redelivered messages after ack timeout
- Poison messages are detected and routed to a dead-letter queue

### Anti-patterns

- Acknowledging messages before processing completes (data loss on crash)
- Unbounded retries without a dead-letter destination (infinite retry loops)
- Large payloads in the message body instead of a reference to external storage
- No visibility timeout tuning, causing duplicate processing under load

---
description: Metric Cardinality Explosion anti-pattern
type: anti-pattern
observable: true
graphable: false
---
# Metric Cardinality Explosion

## Recognition

How to identify this anti-pattern in code.

### Signatures

- User ID, request ID, URL path, or email used as Prometheus label values
- Unbounded label cardinality on Counter, Histogram, or Gauge metrics
- `labels=["user_id"]` or `labels=["request_id"]` on metric definitions
- Metric names generated dynamically (`f"request_{endpoint}_total"`)
- Labels derived from user input, query parameters, or request paths without normalization
- Prometheus scrape duration increasing over time

### Confidence

- **high** -- a metric label is populated from user-supplied or request-specific data (user ID, session ID, full URL path), confirmed by `prometheus_tsdb_head_series` growing unboundedly
- **medium** -- label values come from a set that grows with traffic (e.g., raw URL paths, email addresses) rather than a fixed enumeration
- **low** -- metric definition includes a label whose cardinality is not documented or bounded, or dynamic string formatting is used in metric names

## Impact

Prometheus runs out of memory, queries time out, and storage costs explode from millions of unique time series.

### Symptoms

- Prometheus OOM kills or restarts under normal traffic
- `prometheus_tsdb_head_series` count grows without bound
- PromQL queries on affected metrics time out or return partial results
- Grafana dashboards using high-cardinality metrics fail to load
- TSDB compaction takes progressively longer

### Remediation

- Use only bounded, low-cardinality values as metric labels (HTTP method, status code, service name)
- Replace user/request IDs in labels with bucketed or hashed groupings if segmentation is needed
- Add a linting rule or CI check that rejects metric definitions with known high-cardinality label names
- Use recording rules to pre-aggregate high-cardinality metrics into lower-cardinality summaries
- Audit existing metrics with `topk` by label value count and remediate any exceeding a threshold (e.g., 1000 unique values)

---
description: Metrics Instrumentation architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [observability]
---
# Metrics Instrumentation

## Recognition

How to identify this pattern in code.

### Signatures

- Prometheus client usage: `prometheus_client` (Python), `prom-client` (Node), `prometheus/client_golang` (Go)
- Metric type classes: `Counter`, `Gauge`, `Histogram`, `Summary`
- Metric registration: `register()`, `MustRegister()`, `new Counter({})`, `@metrics.counter()`
- `/metrics` endpoint exposed via HTTP for scraping
- Micrometer (Java/Spring): `MeterRegistry`, `@Timed`, `Counter.builder()`
- Label/tag definitions on metric declarations: `labels=["method", "status"]`, `ConstLabels`
- Histogram bucket configuration: `buckets=[.01, .05, .1, .5, 1, 5]`

### Confidence

- **high** -- Prometheus client imported, metric types registered, and `/metrics` endpoint exposed
- **medium** -- metric library in dependencies and some counters declared but no histogram or `/metrics` endpoint
- **low** -- custom numeric tracking (incrementing counters in code) without a metrics library

## Architecture

Look for well-named metrics with appropriate types, consistent labels, and a scrape-ready endpoint.

### Review Checklist

- Metric names follow the convention: `<namespace>_<subsystem>_<name>_<unit>` (e.g., `http_requests_total`, `request_duration_seconds`)
- Correct metric type for each measurement: counters for totals, gauges for current values, histograms for distributions
- Label cardinality is bounded -- no user IDs, request IDs, or unbounded strings as label values
- Histogram buckets are tuned to the expected distribution, not left at defaults
- All metrics are registered at startup, not created on-the-fly per request
- A `/metrics` endpoint is exposed and returns Prometheus exposition format

### Anti-patterns

- High-cardinality labels that cause metric explosion (e.g., `user_id`, `url_path` with path parameters)
- Using gauges where counters are appropriate (losing monotonicity breaks rate calculations)
- Metrics created inside request handlers instead of registered once at module level
- No histogram for latency measurements -- only averages with no percentile visibility

---
description: Micro-Frontend architectural pattern
type: pattern
testable: true
distributed: true
graphable: true
abstraction: [architectural, frontend, deployment]
---
# Micro-Frontend

## Recognition

How to identify this pattern in code.

### Signatures

- Independently deployable frontend modules owned by separate teams
- Webpack 5 `ModuleFederationPlugin` with `remotes`, `exposes`, `shared` in config
- `single-spa` `registerApplication()` / `start()` for route-based micro-app loading
- `import-map-overrides` for local development against deployed micro-frontends
- `SystemJS` loader for dynamic module loading
- Shell/host application loading remote micro-apps at runtime
- Iframe isolation, Web Components, or shadow DOM boundaries between modules
- Tools: Webpack Module Federation, single-spa, Bit, Piral, import maps

### Confidence

- **high** -- Webpack Module Federation config or single-spa route registration loading separately deployed frontends
- **medium** -- Independent frontend apps composed at build time or via iframe embedding with a shared shell
- **low** -- Any frontend split across separately maintained packages with some form of runtime composition

## Architecture

Look for independently built and deployed frontend modules composed into a unified application by a shell.

### Review Checklist

- Shared dependencies (React, Angular) are loaded once, not duplicated per micro-frontend
- Module boundaries are enforced -- no direct imports between micro-frontends
- Routing is coordinated by the shell, not duplicated across modules
- Styling is scoped per module (CSS modules, shadow DOM, or naming conventions) to prevent leaks
- Failure in one micro-frontend does not crash the entire application (error boundaries)
- Shared state between modules is minimal and uses a defined contract (events, shared store)

### Anti-patterns

- Micro-frontends sharing a database or global state store (coupling through the back door)
- Duplicating large framework bundles in every micro-frontend
- Tight deployment coupling -- all micro-frontends must deploy together
- No contract or versioning for shared APIs between modules

---
description: Microservices architectural pattern
type: pattern
graphable: true
abstraction: [architectural]
---
# Microservices

## Recognition

How to identify this pattern in code.

### Signatures

- Multiple independently deployable services, each with its own Dockerfile or build target
- Service-per-directory repo layout or monorepo with explicit service boundaries (`services/`, `apps/`)
- Separate Kubernetes Deployments, docker-compose services, or serverless stacks per service
- Inter-service communication via HTTP/REST, gRPC, or async messaging (Kafka, RabbitMQ, NATS)
- `docker-compose.yml` with multiple service definitions and internal networking
- Per-service database or schema ownership (no shared tables across services)
- API contracts defined via OpenAPI specs, protobuf definitions, or AsyncAPI schemas

### Confidence

- **high** -- Multiple services with independent Dockerfiles, separate deployments, and inter-service HTTP/gRPC calls
- **medium** -- Monorepo with service directories and shared CI but separate build targets
- **low** -- Multiple entry points in a single repo with some network calls between them

## Architecture

Look for proper service boundaries, independent deployability, and well-defined inter-service contracts.

### Review Checklist

- Each service owns its data store and does not share database tables with other services
- Inter-service communication uses explicit contracts (protobuf, OpenAPI) not ad-hoc HTTP calls
- Services can be deployed, scaled, and rolled back independently
- Failure in one service does not cascade to others (circuit breakers, timeouts, retries in place)
- Service discovery mechanism exists (DNS, service mesh, registry)
- Distributed tracing and correlation IDs propagate across service boundaries

### Anti-patterns

- Shared database across services (distributed monolith disguised as microservices)
- Synchronous call chains spanning three or more services for a single user request
- Services that cannot be deployed without coordinating releases of other services
- No contract testing between services, relying on integration environments to catch breaks

---
description: Middleware — request/response pipeline interceptors for cross-cutting concerns
type: pattern
graphable: true
abstraction: [integration, lifecycle]
---
# Middleware

## Recognition

How to identify this pattern in code.

### Signatures

- `app.use()` with function signature `(req, res, next)` (Express)
- `middleware.ts` or `middleware.js` at project root with `NextRequest`/`NextResponse` (Next.js)
- `defineNuxtRouteMiddleware` or files in `middleware/` directory (Nuxt)
- Django `MIDDLEWARE` setting with classes implementing `__call__` or `process_request`/`process_response`
- FastAPI/Starlette `@app.middleware("http")` or `BaseHTTPMiddleware` subclass
- Koa middleware with `async (ctx, next)` signature and `app.use()`
- `@Injectable()` with `NestMiddleware` interface implementing `use(req, res, next)` (NestJS)
- Redux middleware with `store => next => action` curried signature
- Axios interceptors: `axios.interceptors.request.use()`, `axios.interceptors.response.use()`
- ASP.NET `IMiddleware` or `app.Use()` / `app.UseMiddleware<T>()`
- Pipeline ordering: middleware registered in sequence with explicit ordering dependency

### Confidence

- **high** -- Framework middleware API with `next()` call forwarding to the next handler in a pipeline, registered via `app.use()` or configuration array
- **medium** -- Interceptor or hook that wraps requests/responses with cross-cutting logic but is not called "middleware" or does not use a formal pipeline API
- **low** -- Decorator or wrapper function that adds behavior around a handler but without a composable pipeline or `next()` mechanism

## Architecture

Look for a composable pipeline of handlers that each process a request or action, optionally transform it, and forward to the next handler in the chain.

### Review Checklist

- Middleware execution order is intentional and documented (auth before route handlers, logging early, error handling last)
- Each middleware has a single cross-cutting concern (not combining auth + logging + rate limiting in one)
- `next()` is always called or the response is explicitly terminated -- no silent drops
- Error-handling middleware is placed at the end of the pipeline to catch upstream failures
- Middleware does not mutate shared state in a way that creates coupling between unrelated middleware
- Performance-sensitive middleware (rate limiting, caching) is placed early to short-circuit expensive downstream work

### Anti-patterns

- Middleware that swallows errors without calling next(err) or returning an error response
- Ordering-dependent middleware with no documentation about why the order matters
- God middleware that handles auth, logging, validation, and transformation in a single function
- Middleware that modifies the request/response object in ways that downstream handlers do not expect
- Applying middleware globally when it is only needed on specific routes or endpoints

---
description: Misleading Names anti-pattern
type: anti-pattern
graphable: false
---
# Misleading Names

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `get*` methods that mutate state or have side effects (database writes, cache invalidation, HTTP calls)
- `is*` or `has*` functions returning non-boolean values (strings, integers, objects)
- `create*` that returns an existing object from cache or lookup instead of constructing a new one
- `validate()` methods that also save, send, or transform data beyond validation
- `check*` functions that silently fix the problem they detect
- `find*` methods that create records when none are found (find-or-create hidden behind a find name)

### Confidence

- **high** -- a `get*` method contains INSERT/UPDATE statements, HTTP calls, or file writes
- **medium** -- a method named for one action (validate, check, find) also performs a second unrelated action
- **low** -- method names use vague verbs (handle, process, do) that could mean anything

## Impact

Readers assume wrong behavior from the name, leading to unintended side effects, double writes, and bugs that survive code review because the name looked correct.

### Symptoms

- Calling a getter triggers unexpected state changes or performance degradation
- Code reviewers approve dangerous calls because the method name sounds safe
- Developers duplicate logic because they do not realize a misnamed method already does what they need
- Tests pass in isolation but fail in sequence because a "read" method mutated shared state
- Debug sessions are prolonged because side effects hide behind innocent-looking names

### Remediation

- Rename methods to reflect all their behavior: `getOrCreateUser`, `validateAndSave`, `ensureExists`
- Split methods that do multiple things: separate `validate()` from `save()`
- Enforce naming conventions in code review checklists: getters must be pure, `is*` must return boolean
- Add linting rules that flag `get*` methods containing write operations
- Document side effects in docstrings when renaming is not immediately feasible

---
description: Missing Log Context anti-pattern
type: anti-pattern
observable: true
graphable: false
---
# Missing Log Context

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Log messages with no request ID or correlation ID attached
- Bare `logger.error("failed")` with no structured fields or exception info
- No `structlog.bind()`, `MDC.put()`, or equivalent context binding at request entry
- Impossible to trace a single request across multiple log lines
- Log messages that omit the operation, entity, or input that caused the failure
- No middleware or decorator that injects trace/request IDs into the logging context

### Confidence

- **high** -- error log lines contain only a message string with no structured fields, and there is no request-scoped context binding anywhere in the request lifecycle
- **medium** -- some log calls include context but others in the same service do not, leading to gaps when correlating across calls
- **low** -- logging framework is configured but individual log statements omit key identifiers like entity IDs or operation names

## Impact

Debugging requires guesswork, and incident resolution takes significantly longer because logs cannot be correlated.

### Symptoms

- On-call engineers cannot trace a user-reported error to a specific request
- Log searches return ambiguous results matching multiple unrelated events
- Correlating logs across microservices requires manual timestamp alignment
- Post-incident reviews cite "insufficient logging" as a contributing factor
- Distributed tracing tools show gaps where log context was not propagated

### Remediation

- Add middleware or a request interceptor that binds a request ID and correlation ID to every log entry for the request lifecycle
- Use structured logging (structlog, logfmt, JSON logging) so every log line includes machine-parseable context fields
- Require a minimum set of context fields on all log calls: request ID, operation name, and relevant entity IDs
- Propagate trace context (W3C Trace Context, X-Request-ID) across service boundaries and bind it to the logger
- Add a linting rule that flags bare `logger.error("string")` calls without structured arguments

See also: structured-logging, correlation-id patterns

---
description: Model Registry architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [lifecycle, ml]
---
# Model Registry

## Recognition

How to identify this pattern in code.

### Signatures

- Versioned model storage with unique model names and version numbers
- Model metadata: metrics, parameters, training data lineage, artifact paths
- Stage transitions: `staging` -> `production` -> `archived`
- Methods like `log_model()`, `register_model()`, `load_model()`, `transition_model_version_stage()`
- Model artifact storage (serialized weights, ONNX exports, container images)
- Model lineage tracking: which data, code, and config produced each version
- Libraries: MLflow Model Registry, Weights & Biases, SageMaker Model Registry, Vertex AI Model Registry, Neptune

### Confidence

- **high** — `log_model()`/`register_model()` calls with versioned stage transitions and artifact storage
- **medium** — versioned model artifacts with metadata (metrics, parameters) stored alongside them
- **low** — model files saved with version numbers in filenames or directory structure

## Architecture

Look for a central catalog that versions, tracks, and governs model lifecycle from training through production.

### Review Checklist

- Every model version records its training metrics, parameters, and data lineage
- Stage transitions (staging to production) require explicit approval or automated validation
- Model artifacts are immutable once registered; new versions are created, not overwritten
- Loading a model by name resolves to the correct version for the target stage
- Registry integrates with CI/CD for automated model validation before promotion
- Retired models are archived, not deleted, preserving audit history

### Anti-patterns

- Overwriting model files in place with no version history
- No recorded link between a model version and its training data or code
- Promoting models to production without validation gates or metric checks
- Storing models only on local filesystem with no central registry

---
description: Modular Monolith architectural pattern
type: pattern
graphable: true
abstraction: [architectural]
---
# Modular Monolith

## Recognition

How to identify this pattern in code.

### Signatures

- Single deployable unit with internal module boundaries (`modules/`, `packages/`, `domains/`)
- Explicit module interfaces or public API surfaces with restricted cross-module imports
- Inter-module communication through defined contracts, events, or mediator -- not direct class imports
- Module-level dependency rules enforced by linting, architecture tests, or build constraints
- Shared kernel or common module for cross-cutting types used by multiple modules
- Single Dockerfile or deployment artifact containing all modules

### Confidence

- **high** -- Single deployment with enforced module boundaries, explicit public APIs per module, and architecture tests preventing cross-boundary imports
- **medium** -- Directory structure with `modules/` or `packages/` and some import restrictions but no enforcement tooling
- **low** -- Monolith with logical grouping by feature directory but no formal boundary enforcement

## Architecture

Look for strong module boundaries within a single deployable, with communication through contracts not direct coupling.

### Review Checklist

- Each module exposes a well-defined public API and hides internal implementation details
- Cross-module dependencies flow in one direction or through shared abstractions
- Architecture tests or lint rules enforce module boundary violations at build time
- Inter-module communication uses events, mediator, or interfaces -- not direct internal class references
- Database tables are logically partitioned by module even if they share a physical database

### Anti-patterns

- Modules importing internal classes from other modules, bypassing the public API
- Circular dependencies between modules that prevent independent reasoning about each
- No enforcement mechanism -- boundaries exist in documentation only and erode over time
- All modules sharing a single god-object or global state that couples them implicitly

---
description: Monad/Railway-Oriented Programming architectural pattern
type: pattern
testable: true
graphable: false
abstraction: [design, error-handling]
---
# Monad/Railway-Oriented Programming

## Recognition

How to identify this pattern in code.

### Signatures

- `bind()`, `flatMap()`, `>>=`, `and_then()`, `chain()` methods for monadic composition
- `do` notation (Haskell), for-comprehensions (Scala)
- `Maybe` / `Option` chaining with `map()` and `bind()`/`flatMap()`
- `IO` monad for sequencing side effects
- `returns` library `flow()` for composing monadic pipelines (Python)
- Libraries: `fp-ts` (TypeScript), `cats`/`zio` (Scala), `dry-monads` (Ruby)

> For `Result`/`Either` as error handling, see result-type. This pattern focuses on monadic composition (bind/chain) across any monad, not just error types.

### Confidence

- **high** -- Explicit monadic types composed via `bind`/`flatMap`/`>>=` with `do` notation or for-comprehensions, and library usage (returns, fp-ts, cats)
- **medium** -- `Option`/`Maybe` used consistently with `map`/`flatMap` chaining but no broader monadic composition
- **low** -- Container types with `map()` but no `bind`/`flatMap`, or ad-hoc chaining without formal monadic structure

## Architecture

Look for chained operations on container types that propagate failure automatically without explicit branching.

### Review Checklist

- Success and failure paths are explicit types, not exceptions or null checks
- Operations compose via `bind`/`flatMap`, not nested if-else or try-catch
- Error types carry enough context to diagnose failures at the end of the chain
- The "happy path" reads as a clean pipeline without interleaved error handling
- Side effects are pushed to the edges, keeping the chain pure
- Terminal handling (fold/match/unwrap) happens at the boundary, not mid-chain

### Anti-patterns

- Unwrapping (`unwrap()`, `get()`, `!`) in the middle of a chain, defeating the safety guarantee
- Mixing exceptions and monadic error handling in the same code path
- Overly nested `flatMap` calls instead of using for-comprehensions or do-notation
- Using monadic types for simple cases where a plain if-else would be clearer

---
description: Mutual TLS architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [security, infrastructure]
---
# Mutual TLS

## Recognition

How to identify this pattern in code.

### Signatures

- Client certificate configuration (`--cert`, `--key` flags, `tls.Certificate` structs)
- Server requiring client certs: `ssl_verify_client on` (nginx), `tls.Config{ClientAuth: tls.RequireAndVerifyClientCert}` (Go)
- CA bundle configuration for validating client certificates (`ClientCAs`, `ssl_client_certificate`)
- X.509 client certificate parsing and subject/SAN extraction from verified connections
- Certificate chain validation with intermediate CAs
- Service-to-service certificate provisioning (SPIFFE, cert-manager, Vault PKI)
- TLS termination configuration distinguishing between external TLS and internal mTLS
- Libraries: `crypto/tls` (Go), `ssl` (Python), `tls` (Node), OpenSSL bindings

### Confidence

- **high** -- Server configured to require and verify client certificates, CA bundle loaded, and client services present certificates with subject/SAN-based identity
- **medium** -- TLS configuration with client certificate fields present but `ClientAuth` set to optional or verification mode unclear
- **low** -- Certificate files referenced in config but no explicit mutual verification (could be standard one-way TLS)

## Architecture

Look for bidirectional certificate verification where both client and server authenticate each other via X.509 certificates.

### Review Checklist

- Server requires client certificates (not optional/request-only mode)
- CA bundle is scoped narrowly (only trusted CAs for expected clients, not the system CA store)
- Certificate identity (CN or SAN) is checked after TLS handshake for authorization decisions
- Certificates have reasonable validity periods with automated rotation before expiry
- Certificate revocation is handled (CRL or OCSP stapling)
- Plaintext fallback is impossible (TLS is enforced, not optional)

### Anti-patterns

- Using the system-wide CA store to validate client certificates (any publicly-trusted cert would pass)
- No certificate rotation -- long-lived certificates with manual renewal processes
- Skipping client identity verification after handshake (mTLS authenticates but code never checks who)
- Mixing mTLS and non-mTLS traffic on the same port without clear enforcement boundaries

---
description: Multi-tenant isolation pattern for shared infrastructure
type: pattern
category: domain-model
abstraction: [architectural, data]
---
# Multi-Tenant

## Recognition

How to identify this pattern in code.

### Signatures

- `tenant_id`, `organization_id`, `org_id` columns present on most or all database tables
- `tenant_context`, `TenantContext`, `current_tenant` middleware or context objects
- `tenant_scope`, `with_tenant` decorators or context managers that filter queries by tenant
- Row-level security policies: `CREATE POLICY ... USING (tenant_id = current_setting('app.tenant_id'))`
- Schema-per-tenant: `CREATE SCHEMA tenant_abc`, `SET search_path TO tenant_abc`
- Python: `django-tenants`, `django-multitenant`, tenant middleware setting `request.tenant`
- JS/TS: `tenant_id` in JWT claims, middleware extracting tenant from subdomain or header
- Go: `tenantID` in context (`context.WithValue`), per-tenant database connection selection
- Rust: `tenant_id` field in request extensions, middleware extracting tenant from auth token
- Java: `@TenantId` annotation, Hibernate multi-tenancy config, `TenantIdentifierResolver`

### Confidence

- **high** -- tenant_id column on all data tables with row-level security or automatic query scoping via middleware, plus per-tenant configuration
- **medium** -- tenant_id in JWT/auth context with manual query filtering in repositories
- **low** -- Organization-level grouping without strict query-level isolation or security policies

## Architecture

### When to use
- SaaS platforms serving multiple customers on shared infrastructure
- Systems where data isolation between organizations is a security and compliance requirement
- Platforms needing per-tenant configuration, feature flags, or usage limits

### Anti-patterns
- Forgetting tenant filters on queries, causing cross-tenant data leakage
- Tenant isolation only at the API layer without database-level enforcement (row-level security)
- Shared caches without tenant-scoped keys, allowing one tenant's data to be served to another

### Complements
- [rbac](/concepts/rbac) — tenant isolation works alongside role-based access within a tenant
- [rate-limiting](/concepts/rate-limiting) — per-tenant rate limits prevent noisy neighbor problems
- [sharding](/concepts/sharding) — large tenants may require dedicated shards for performance isolation

## Impact

Multi-tenancy is a cross-cutting concern that must be enforced at every data access path. A single missing tenant filter is a security vulnerability. Testing must include cross-tenant isolation verification, and monitoring should track per-tenant resource consumption to detect noisy neighbors.

---
description: Model-View-Controller architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [architectural, frontend]
---
# Model-View-Controller

## Recognition

How to identify this pattern in code.

### Signatures

- Separate `models/`, `views/`, `controllers/` directories or class suffixes (`UserController`, `UserModel`)
- Controllers handling HTTP input, delegating to models, selecting views
- Models managing data access and business logic, no rendering or request handling
- Views/templates rendering output from model data, no business logic
- Frameworks: Django (MTV variant), Rails, Spring MVC, ASP.NET MVC, Laravel

### Confidence

- **high** -- Framework-enforced MVC structure with distinct model, view, and controller layers
- **medium** -- Clear separation of data/logic/presentation across files but no formal MVC framework
- **low** -- Some separation of concerns between data handling and rendering, but boundaries are blurred

## Architecture

Look for strict separation between data (model), presentation (view), and input handling (controller).

### Review Checklist

- Controllers are thin -- delegate to models/services, do not contain business logic
- Models have no knowledge of views or HTTP layer
- Views contain only presentation logic -- no database queries or business rules
- Input validation happens at the controller or a dedicated validation layer, not scattered across all three

### Anti-patterns

- Fat controllers containing business logic, database queries, and response formatting
- Views executing database queries or mutating model state
- Models importing view or controller modules (circular dependency)
- Skipping the controller and calling models directly from route definitions

---
description: Model-View-ViewModel architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [architectural, frontend]
---
# Model-View-ViewModel

## Recognition

How to identify this pattern in code.

### Signatures

- ViewModel classes exposing observable properties that the view binds to
- Two-way data binding between view and ViewModel (`@observable`, `@computed`, `@Binding`)
- `ViewModel` suffix on classes (`UserViewModel`, `SettingsViewModel`)
- Commands or actions exposed as ViewModel methods, invoked by the view
- Frameworks: WPF/XAML, SwiftUI, Android ViewModel/LiveData, Knockout.js, Vue (Composition API)

### Confidence

- **high** -- ViewModel classes with `@observable`/`@Published` properties and declarative view bindings
- **medium** -- Reactive state objects driving UI updates without direct DOM manipulation, but no formal ViewModel naming
- **low** -- Any pattern where a non-model object mediates between data and view with some reactivity

## Architecture

Look for a ViewModel layer providing observable state that views bind to declaratively.

### Review Checklist

- ViewModels contain no view-specific code (no UI imports, no layout logic)
- Data binding is declarative, not manually synchronized in imperative code
- ViewModel state is the single source of truth for the view -- no parallel state in the view layer
- ViewModels are testable in isolation without instantiating views
- Disposal/cleanup of subscriptions when the view is destroyed

### Anti-patterns

- ViewModel directly manipulating DOM elements or UI widgets
- Two-way binding on complex objects causing unintended cascading updates
- ViewModel holding a reference to the view (breaking the decoupling)
- Observable properties with no cleanup, leaking subscriptions on navigation

---
description: N+1 Queries anti-pattern
type: anti-pattern
observable: true
graphable: false
---
# N+1 Queries

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Database query inside a loop (`for item in items: item.related.load()`)
- Missing `prefetch_related`/`includes`/`JOIN` on ORM queries that access related objects
- ORM lazy loading triggered during iteration over a collection
- SQL log showing repeated identical queries with different IDs
- Data access layer returning parent objects without eagerly loading children that callers always need

### Confidence

- **high** -- SQL logs show N identical SELECT statements differing only by a foreign key value within a single request
- **medium** -- loop body accesses a relationship attribute on an ORM model without a prior prefetch or join
- **low** -- ORM query fetches a list without `select_related`/`includes` and the result is passed to a template or serializer

## Impact

Linear query explosion that overwhelms the database as dataset size grows.

### Symptoms

- Request latency scales linearly with the number of records
- Database CPU and connection count spike under normal load
- Slow query logs fill with trivially simple SELECTs
- Application appears fast in development (small dataset) but crawls in production
- Database connection pool exhaustion under moderate concurrency

### Remediation

- Use eager loading (`prefetch_related`, `includes`, `joinedload`) on all queries where related data will be accessed
- Batch-fetch related records in a single query using `WHERE id IN (...)` instead of looping
- Add a query counter in tests that asserts a maximum number of queries per endpoint
- Introduce a data loader or batch loader pattern for GraphQL or similar aggregation layers
- Profile with query logging enabled in staging to catch regressions before production

See also: batch-loader pattern (remediation)

---
description: Null Object architectural pattern
type: pattern
testable: true
graphable: false
abstraction: [design]
---
# Null Object

## Recognition

How to identify this pattern in code.

### Signatures

- No-op implementations of interfaces: `NullLogger`, `NoOpCache`, `NullMetrics`
- `NoOp*` or `Null*` or `Noop*` class prefixes implementing a production interface
- Default objects that satisfy an interface contract but perform no work
- Absence of `if x is None` / `if x == null` guard checks at call sites
- Dependency injection frameworks wiring null objects as defaults when no real implementation is configured
- `DevNull*` or `Blackhole*` implementations for sinks (writers, loggers, event emitters)

### Confidence

- **high** — Explicit null object classes implementing the same interface as their real counterparts, injected via DI or used as defaults
- **medium** — Default parameter values that are no-op lambdas or empty objects (e.g., `logger=lambda *a: None`)
- **low** — Scattered `or default` / `?? fallback` expressions that approximate null object behavior inline

## Architecture

Look for polymorphic no-op implementations that eliminate null checks by providing safe default behavior.

### Review Checklist

- Null objects implement the full interface contract, not just the methods currently called
- Null objects are clearly named to signal their intent (prefix with `Null`, `NoOp`, or `Noop`)
- Call sites depend on the interface, never checking which implementation (real vs null) they received
- Null objects are stateless and safe to share as singletons
- Logging or metrics null objects optionally support a debug mode that records calls for testing

### Anti-patterns

- Null objects that silently swallow errors that should be surfaced (hiding real failures)
- Partial null implementations that throw `NotImplementedError` on some methods
- Using null objects where an Optional/Maybe type would be more appropriate (when absence itself is meaningful)
- Null objects with side effects or mutable state that break the expectation of inert behavior

---
description: OAuth2/OpenID Connect architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [security]
---
# OAuth2/OpenID Connect

## Recognition

How to identify this pattern in code.

### Signatures

- Authorization code flow endpoints: `/authorize`, `/token`, `/callback`
- Configuration fields: `client_id`, `client_secret`, `redirect_uri`, `scope`
- JWT validation logic parsing `id_token` or `access_token` with signature verification
- Bearer token extraction from `Authorization` header
- OIDC discovery endpoint: `/.well-known/openid-configuration`
- Libraries: `authlib`, `passport` (Node), `jose`, `python-jose`, `next-auth`, `oauthlib`
- Token refresh logic with `refresh_token` grant type

### Confidence

- **high** -- authorization code flow with `/authorize` and `/token` endpoints, JWT validation, and OIDC discovery URL configured
- **medium** -- `client_id`/`client_secret` in config with bearer token middleware but flow details unclear
- **low** -- JWT parsing present but no OAuth flow visible (could be custom auth)

## Architecture

Look for correct implementation of the OAuth2 authorization flow with proper token validation and secure credential handling.

### Review Checklist

- Authorization code flow is used (not implicit flow) for server-side applications
- Token validation checks signature, expiry, issuer, and audience claims
- Client secrets are stored securely (not hardcoded in source, use env vars or secret stores)
- PKCE is used for public clients (SPAs, mobile apps) that cannot keep a client secret
- Refresh tokens are stored securely and rotated on use
- Scopes follow least-privilege principle

### Anti-patterns

- Using implicit flow for new applications (deprecated in OAuth 2.1)
- Skipping token signature verification or not validating issuer/audience claims
- Storing tokens in localStorage (vulnerable to XSS) instead of httpOnly cookies
- Hardcoding client secrets in source code or frontend bundles

---
description: Object Pool architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design, infrastructure]
---
# Object Pool

## Recognition

How to identify this pattern in code.

### Signatures

- Methods named `acquire()`, `release()`, `borrow()`, `return_to_pool()`, `get()`, `put()`
- Pool size configuration: `max_size`, `min_idle`, `max_idle`, `pool_size`
- Connection pool classes: `ConnectionPool`, `ThreadPool`, `WorkerPool`
- Python: `asyncio.Queue` used as a pool, `multiprocessing.Pool`, `concurrent.futures.*Executor`
- Java: `ExecutorService`, `HikariCP`, `Commons Pool`
- Go: `sync.Pool`, buffered channels used as pools

### Confidence

- **high** -- class with `acquire()`/`release()` pair, pool size limits, and resource reuse tracking
- **medium** -- connection pool library configuration (HikariCP, pgBouncer, `asyncpg.create_pool`)
- **low** -- pre-allocated array of objects with index-based checkout

## Architecture

Look for correct lifecycle management: acquire, use, release, and handling of stale or broken resources.

### Review Checklist

- Resources are always returned to the pool (try/finally or context manager)
- Pool handles stale or broken resources (validation on acquire, eviction on error)
- Maximum pool size prevents unbounded resource consumption
- Timeout on acquire prevents indefinite blocking when pool is exhausted
- Pool shutdown drains and closes all resources cleanly

### Anti-patterns

- Acquired resources not returned on error paths (resource leak)
- No health check on pooled objects -- stale connections handed to callers
- Unbounded pool growth (no max size) defeating the purpose of pooling
- Pool used for cheap-to-create objects where allocation is faster than pool overhead

---
description: Observer/Event Emitter architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design, messaging]
---
# Observer

## Recognition

How to identify this pattern in code.

### Signatures

- Methods named `subscribe()`, `on()`, `addListener()`, `register()`, `attach()`
- Emission methods: `emit()`, `notify()`, `publish()`, `dispatch()`, `fire()`
- Callback/handler registration with event names or types
- Python: `blinker` signals, `pyee.EventEmitter`, `asyncio` event patterns
- JS/TS: `EventEmitter`, `addEventListener`, RxJS `Observable.subscribe()`, custom event bus
- Go: channel-based pub/sub, callback slices
- Java: `java.util.Observer` (deprecated), Spring `ApplicationEvent`, Guava `EventBus`

### Confidence

- **high** -- explicit subscribe/emit pair with named events and registered handlers
- **medium** -- callback list maintained and iterated on state change
- **low** -- single callback parameter passed to a function (basic inversion of control)

## Architecture

Look for correct lifecycle management of subscriptions and defined event contracts.

### Review Checklist

- Subscriptions are cleaned up (unsubscribe on teardown to prevent memory leaks)
- Event contracts are defined (typed events, not arbitrary string keys with untyped payloads)
- Error in one observer does not prevent notification of remaining observers
- Ordering guarantees are documented (or explicitly unordered)
- No circular notification chains (observer A notifies B which notifies A)

### Anti-patterns

- Forgotten unsubscribe causing memory leaks or ghost handlers
- Observers mutating the event/subject during notification (action at a distance)
- String-based event names with no type safety on payloads
- Synchronous observer chain blocking the emitter when async would be appropriate

See also: pub-sub (inter-process variant)

---
description: Optimistic Locking architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [data, concurrency]
---
# Optimistic Locking

## Recognition

How to identify this pattern in code.

### Signatures

- `version` column or field on database entities, incremented on each update
- `@Version` annotation (JPA/Hibernate), `lock_version` (Rails), `__v` (Mongoose)
- `ETag` response header paired with `If-Match` conditional request header
- `UPDATE ... WHERE version = ?` or `UPDATE ... WHERE updated_at = ?` conditional writes
- `StaleObjectError` (Rails), `OptimisticLockException` (JPA), `VersionError` exception handling
- CAS (compare-and-swap) operations in distributed stores (Redis `WATCH`/`MULTI`, DynamoDB conditional expressions)
- `ConditionalCheckFailedException` (DynamoDB), `cas` parameter in Consul/etcd

### Confidence

- **high** -- Version column with conditional `UPDATE ... WHERE version = ?` and explicit conflict exception handling
- **medium** -- ETag/If-Match headers on API endpoints or `@Version` annotation present on entities
- **low** -- Timestamp-based conflict detection (`updated_at` comparison) without explicit version tracking

## Architecture

Look for version-based conflict detection on writes with clear retry or conflict resolution strategy.

### Review Checklist

- Every mutable entity has a version field that is atomically incremented on update
- Write operations use conditional updates that fail if the version has changed since the read
- Conflict handling is explicit: retry with fresh data, merge, or surface the conflict to the user
- Read-modify-write cycles are as short as possible to minimize the conflict window
- API layer surfaces version information (ETag/If-Match) so clients can participate in conflict detection
- High-contention entities have been identified and optimistic locking is appropriate for their write frequency

### Anti-patterns

- Silently overwriting data on conflict (last-write-wins) without detecting the version mismatch
- Infinite retry loops on conflict without backoff or a maximum retry count
- Using optimistic locking on high-contention resources where most writes will conflict and retry
- Checking the version in application code instead of the database WHERE clause (race condition)

---
description: Optimistic Update — immediately reflecting expected state changes in the UI before server confirmation
type: pattern
testable: true
graphable: true
abstraction: [frontend, data, resilience]
---
# Optimistic Update

## Recognition

How to identify this pattern in code.

### Signatures

- `onMutate` / `onError` / `onSettled` callbacks in TanStack Query mutations
- `optimisticResponse` in Apollo Client mutations
- Manual state rollback on error (`previousData` pattern)
- `useSWRMutation` with `optimisticData` option
- Zustand/Redux: update store immediately, revert on API failure
- UI shows success state before server response, reverts on failure

### Confidence

- **high** -- mutation with `onMutate` setting cache/store + `onError` rolling back to previous state
- **medium** -- immediate UI update on action but no explicit rollback mechanism
- **low** -- fire-and-forget mutations that update UI without waiting (may not be intentionally optimistic)

## Architecture

Look for a mutation flow that updates client-side state immediately upon user action, captures previous state for rollback, and reconciles with the server response on success or failure.

### Review Checklist

- Previous state is captured before the optimistic update for rollback
- Error handler reverts to the captured state
- Success handler reconciles server response with optimistic state (server is source of truth)
- User receives feedback on rollback (toast, error message -- not silent revert)
- Optimistic updates are only applied for low-risk mutations (add to cart: yes, payment: no)

### Anti-patterns

- No rollback mechanism -- optimistic state persists even after server failure
- Optimistic updates on critical operations (payments, deletes) where false positives are harmful
- Race conditions -- multiple optimistic updates to the same entity without sequencing
- Silent rollback -- user doesn't know their action failed

---
description: Outbox architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [messaging, data, resilience]
---
# Outbox

## Recognition

How to identify this pattern in code.

### Signatures

- Database table named `outbox`, `outbox_events`, or `pending_events`
- Events written to the outbox table in the same transaction as the business state change
- Separate process or thread that polls the outbox table and publishes events to a message broker
- `published` / `processed` boolean flag or `published_at` timestamp column on outbox rows
- CDC (Change Data Capture) configuration reading from the outbox table (e.g., Debezium connector)
- Transaction boundaries that include both the domain write and the outbox insert

### Confidence

- **high** -- Outbox table with a publisher process, events written in the same transaction as state changes, and a `published` flag for tracking
- **medium** -- Events stored in a database table alongside business data, but the publishing mechanism is unclear or inline
- **low** -- After-commit hooks that publish events to a broker without an intermediate table (no durability guarantee)

## Architecture

Look for events persisted to a database table atomically with state changes, then relayed to a message broker by a separate process.

### Review Checklist

- Outbox insert and business state change happen in the same database transaction
- A dedicated publisher process polls or streams from the outbox table
- Published events are marked or deleted to prevent re-publishing
- Publisher handles duplicate delivery gracefully (consumers must be idempotent)
- Outbox table has an index on the unpublished/pending status for efficient polling
- Stale unpublished events are monitored and alerted on

### Anti-patterns

- Publishing events directly to the broker inside the business transaction (dual-write problem)
- No tracking of published status -- events are re-sent on every poll cycle
- Outbox table grows unbounded because published rows are never cleaned up
- Publisher and business logic share the same process with no isolation

---
description: Over/Under-Fetching anti-pattern
type: anti-pattern
graphable: false
---
# Over/Under-Fetching

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Returning entire database rows or full object graphs when the caller needs one or two fields (over-fetching)
- Multiple sequential API calls required to assemble the data for a single view (under-fetching)
- `/users` endpoint returning 50 fields when the UI displays 3
- `SELECT *` queries where only a few columns are used
- Client-side code filtering or reshaping API responses because the server returns too much or the wrong shape
- N+1 API call patterns: fetch a list, then fetch details for each item individually

### Confidence

- **high** -- an endpoint returns the full database model with 20+ fields and the primary consumer uses 3 of them, or a single page requires 5+ sequential API calls
- **medium** -- `SELECT *` is used in queries where a subset of columns would suffice
- **low** -- an endpoint returns a few extra fields beyond what the primary consumer needs (minor over-fetch)

## Impact

Wasted bandwidth, poor performance, and increased latency from either transferring unused data or making too many round-trips to assemble needed data.

### Symptoms

- API response payloads are disproportionately large relative to what the client renders
- Page load requires a waterfall of sequential API calls visible in the network tab
- Mobile clients consume excessive bandwidth and battery because of bloated responses
- Backend performance degrades under load because every request queries and serializes unnecessary data
- Clients maintain complex data-assembly logic that belongs on the server

### Remediation

- Design purpose-built endpoints or views that return exactly what each consumer needs (BFF pattern)
- Support field selection via query parameters (`?fields=id,name,email`) or GraphQL
- Replace N+1 API call patterns with batch endpoints or compound resources
- Use database projections: `SELECT id, name, email` instead of `SELECT *`
- Profile actual API usage to identify endpoints where response size and call count can be optimized

---
description: Pagination architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [data, api]
---
# Pagination

## Recognition

How to identify this pattern in code.

### Signatures

- `limit`/`offset` query parameters or `LIMIT ? OFFSET ?` in SQL queries
- Cursor-based pagination with `next_cursor`, `after`, `before` parameters
- `page`/`per_page` or `page`/`page_size` request parameters
- `Link` response header with `rel=next`, `rel=prev`, `rel=first`, `rel=last`
- `has_more`, `has_next_page` boolean flag in response payloads
- Keyset pagination using `WHERE id > ? ORDER BY id LIMIT ?`
- `totalCount`, `pageInfo`, `edges`/`nodes` in GraphQL connection pattern (Relay spec)

### Confidence

- **high** -- Cursor-based pagination with `pageInfo`/`has_next_page` or keyset pagination with stable ordering
- **medium** -- `limit`/`offset` parameters in API with total count and page metadata in response
- **low** -- SQL queries with `LIMIT` but no pagination metadata returned to the caller

## Architecture

Look for the right pagination strategy for the data size and access pattern, with stable ordering guarantees.

### Review Checklist

- Pagination strategy matches the use case: offset for small datasets, cursor/keyset for large or real-time data
- Results are ordered by a stable, unique key to prevent duplicates and missed records across pages
- Response includes pagination metadata (total count or has_more flag, next cursor or page link)
- Default and maximum page sizes are enforced to prevent clients requesting unbounded result sets
- Cursor values are opaque to clients and resistant to tampering (base64-encoded, signed, or encrypted)
- Database queries use appropriate indexes to support the pagination ordering efficiently

### Anti-patterns

- Using `OFFSET` on large datasets where deep pages cause full table scans (offset 100000)
- No stable sort order, causing records to shift between pages as data changes
- Exposing raw database IDs or internal state as cursor values that clients can manipulate
- Missing maximum page size limit, allowing a single request to fetch the entire dataset

---
description: Pipeline/Filter architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design, data]
---
# Pipeline/Filter

## Recognition

How to identify this pattern in code.

### Signatures

- Ordered chain of transform functions where output of one feeds input of the next
- Pipe operators (`|>`, `|`, `>>`) composing stages
- Functions named `pipeline()`, `pipe()`, `compose()`, or `chain()`
- Filter chains with `addFilter()`, `addStage()`, or `addStep()`
- Data flowing through sequential stages in a defined order
- Unix-style composition: small single-purpose transforms piped together
- Functional pipeline libraries (`ramda`, `lodash/fp`, `transducers`)

### Confidence

- **high** -- Explicit `pipeline()` or `pipe()` call chaining multiple transform functions with typed stage interfaces
- **medium** -- Sequential function composition with data flowing left-to-right or top-to-bottom through stages
- **low** -- Array of functions applied in order, or a series of map/filter calls without a named pipeline abstraction

## Architecture

Look for each stage being a pure transform with a uniform interface and no coupling between non-adjacent stages.

### Review Checklist

- Each filter/stage has a uniform interface (same input/output shape or a common protocol)
- Stages are independently testable -- no hidden state shared between stages
- Pipeline order is explicit and configurable, not hardcoded in scattered locations
- Error handling is defined per-stage or at the pipeline level, not silently swallowed mid-chain
- Stages are reusable across different pipelines without modification
- Back-pressure or buffering strategy exists when stages have different throughput rates

### Anti-patterns

- Stages that reach into other stages' internal state instead of communicating through the pipe
- Monolithic transform that does everything in one function disguised as a "pipeline"
- No error propagation -- a failing stage silently passes corrupt data downstream
- Tightly coupled stage ordering where inserting or removing a stage breaks the chain

---
description: Pipeline stages structure — components arranged as sequential processing stages
type: structure-shape
abstraction: [architectural, data]
---
# Pipeline Stages

## Recognition

### Signatures

- Components named `Stage`, `Step`, `Phase`, `Processor` with sequential numbering or ordering
- Unix-pipe-style composition: output of stage N is input of stage N+1
- Compiler passes: lexer → parser → AST → optimizer → codegen
- Image processing: decode → resize → filter → encode
- CI/CD pipeline stages: build → test → deploy
- Middleware chains where each middleware processes and passes to next
- `Pipeline` class that composes `Stage` instances in order
- scikit-learn `Pipeline` with sequential transformers

### Confidence

- **high** — explicit pipeline class composing named stages with defined input/output contracts between stages
- **medium** — sequential function calls where each output feeds the next, but without formal pipeline structure
- **low** — code that processes data in steps but steps are not modular or reorderable

---
description: Plugin host structure — core system with pluggable extensions via defined interfaces
type: structure-shape
abstraction: [architectural, design]
---
# Plugin Host

## Recognition

### Signatures

- Plugin interface or abstract base class that extensions implement
- Plugin discovery: scanning directories, entry points, or registries
- Python `entry_points` in `pyproject.toml` or `setup.py`
- VS Code extension API: `vscode.extensions`, `activate()` function
- WordPress hooks: `add_action()`, `add_filter()`
- Webpack plugins implementing `apply(compiler)` interface
- Babel/ESLint plugin config arrays
- Dynamic import/loading of plugin modules at runtime
- Plugin lifecycle: register → initialize → activate → deactivate
- Configuration-driven feature enablement

### Confidence

- **high** — defined plugin interface with discovery mechanism, lifecycle management, and multiple third-party plugins
- **medium** — extension points via interfaces/hooks but plugins are internal, not third-party
- **low** — configurable behavior via strategy pattern or dependency injection but no formal plugin system

---
description: Plugin architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Plugin Architecture

## Recognition

How to identify this pattern in code.

### Signatures

- Plugin registry classes or dictionaries mapping plugin names to implementations
- Dynamic registration at startup via discovery or scanning
- `register_plugin()` / `load_plugins()` functions managing plugin lifecycle
- Python `setup.cfg` or `pyproject.toml` `entry_points` defining plugin hooks
- `pluggy` hook specifications and implementations (`@hookimpl`, `@hookspec`)
- Plugin directories scanned at startup for auto-discovery (`plugins/`, `extensions/`)
- `PluginManager` class coordinating plugin registration, initialization, and teardown
- Plugin interface or base class that all plugins must implement

### Confidence

- **high** -- `PluginManager` with `register_plugin()`/`load_plugins()`, or `pluggy` hook specs with entry points configuration
- **medium** -- Plugin directory scanning at startup with a plugin registry, but without a formal plugin interface
- **low** -- Dynamic module loading or extension directories without explicit registration or lifecycle management

## Architecture

Look for a stable plugin interface with discovery/registration and no core modifications needed.

### Review Checklist

- Plugin interface is well-defined and versioned — plugins depend on it, not on core internals
- Registration happens at startup via a registry — no hardcoded plugin lists
- Core functions without any plugins loaded (graceful degradation)
- Plugin lifecycle is managed (init, start, stop) — no orphaned resources

### Anti-patterns

- Plugins importing core internals beyond the published API surface
- No versioning on the plugin interface — core changes break all plugins silently
- Plugin registration order creates hidden dependencies between plugins

---
description: Pokemon Exception anti-pattern
type: anti-pattern
graphable: false
---
# Pokemon Exception

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `except:` or `except Exception:` catching everything in Python
- `catch(Exception e)` or `catch(Throwable t)` without filtering in Java
- `catch(...)` in C++
- `rescue => e` with no specific exception class in Ruby
- Bare `catch {}` blocks in C# or JavaScript swallowing all errors
- Catching `KeyboardInterrupt`, `SystemExit`, or `OutOfMemoryError` accidentally because the catch is too broad

### Confidence

- **high** -- bare `except:` or `catch(Exception)` with no re-raise, combined with a pass/empty block or generic logging
- **medium** -- broad catch exists but logs the error and continues execution without filtering exception types
- **low** -- catch-all exists but re-raises after cleanup (may be intentional)

## Impact

Masks real errors, prevents clean shutdown on signals, and makes debugging nearly impossible because failures are silently swallowed.

### Symptoms

- Application hangs or behaves incorrectly but no errors appear in logs
- Ctrl+C or SIGTERM fails to stop the process because KeyboardInterrupt is caught
- Corrupted state persists because exceptions that should have rolled back transactions were swallowed
- Developers add increasingly desperate logging because they cannot find where errors go
- Production incidents take hours to diagnose because the real exception was eaten

### Remediation

- Catch only the specific exceptions you know how to handle: `except ValueError` not `except Exception`
- Always re-raise exceptions you cannot fully handle: `except Exception: log(); raise`
- Never catch `BaseException` in Python or `Throwable` in Java unless implementing a top-level error boundary
- Use a top-level exception handler (middleware, main loop) for truly unexpected errors, not scattered catch-alls
- Add linting rules (e.g., pylint `broad-except`, SonarQube rules) to flag overly broad catches in CI

---
description: Polling flow — periodic check for state changes or new work
type: flow-shape
abstraction: [integration, lifecycle]
---
# Polling

## Recognition

### Signatures

- `setInterval()` or `setTimeout()` with recurring fetch/check
- Cron jobs or k8s CronJobs that run periodically
- `while True: sleep(N); check()` loops
- Database polling: `SELECT * FROM jobs WHERE status = 'pending' LIMIT N`
- SQS `ReceiveMessage` with `WaitTimeSeconds` (long polling)
- File system watchers checking for new files in a directory
- Health check loops: periodically hitting `/healthz` endpoints
- Polling-based leader election: periodic attempts to acquire a lock
- `last_checked_at` or `cursor` columns tracking polling position

### Confidence

- **high** — explicit periodic loop with configurable interval, idempotent processing, and cursor tracking
- **medium** — cron job or timer-based check without idempotency guarantees
- **low** — ad-hoc `sleep()` loops without structured polling pattern

---
description: Premature Optimization anti-pattern
type: anti-pattern
graphable: false
---
# Premature Optimization

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Caching layer introduced before measuring whether latency is actually a problem
- Denormalized tables or materialized views created before hitting scale thresholds
- Complex data structures (tries, bloom filters, skip lists) used for small datasets that fit comfortably in a linear scan
- Hand-rolled serialization or binary protocols for "performance" instead of standard JSON/protobuf
- Micro-benchmarks driving architecture decisions without production traffic profiles

### Confidence

- **high** -- complex optimization infrastructure exists but profiling data shows the optimized path accounts for less than 5% of total latency
- **medium** -- caching, denormalization, or custom data structures present with no accompanying benchmarks or load test results
- **low** -- comments referencing "performance" or "efficiency" on code that handles low-traffic paths or small datasets

## Impact

Unnecessary complexity added without proven need, increasing maintenance cost while delivering negligible benefit.

### Symptoms

- Code is harder to understand because of optimization layers that obscure intent
- Bugs hide in custom serialization or caching invalidation logic
- New features require working around optimization constraints that were never necessary
- Team spends time maintaining cache coherency for data that changes rarely and loads in milliseconds without caching
- Architecture is rigid because premature optimization locked in early design decisions

### Remediation

- Measure first: profile production workloads before introducing any optimization
- Start with the simplest correct implementation and optimize only proven bottlenecks
- Remove caching layers, denormalized tables, or custom data structures that lack supporting performance data
- Document the performance requirement that justifies each optimization with concrete numbers
- Use standard library data structures and serialization formats unless benchmarks prove them insufficient

---
description: Primitive Obsession anti-pattern
type: anti-pattern
graphable: false
---
# Primitive Obsession

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Email addresses, phone numbers, money amounts, or URLs represented as plain strings
- Currency amounts stored as float or double with no currency code attached
- Coordinates passed as bare tuples or two separate float parameters
- Domain concepts (order ID, user ID, SKU) typed as generic `str` or `int` with no dedicated wrapper
- Validation logic for the same primitive scattered across multiple callers instead of centralized
- Functions accepting `(str, str, int, str)` where each string means something different

### Confidence

- **high** -- the same validation regex for an email or phone appears in 3+ different locations, each operating on a raw string
- **medium** -- money calculations use float arithmetic with ad-hoc rounding scattered across business logic
- **low** -- function signatures use generic types (string, int) for domain concepts but validation is at least centralized

## Impact

No encapsulation of domain rules; validation is repeated everywhere, inconsistently, and invalid values slip through the cracks.

### Symptoms

- The same regex or validation check is copy-pasted across multiple modules
- Invalid values (negative prices, malformed emails) make it into the database
- Functions accept wrong arguments with no type error: user ID passed where order ID was expected
- Arithmetic on money produces floating-point rounding errors
- Refactoring a format change (e.g., phone number format) requires touching dozens of files

### Remediation

- Create value objects or newtypes for each domain concept: `Email`, `Money`, `UserId`, `PhoneNumber`
- Put all validation and parsing in the constructor so invalid instances cannot exist
- Use the type system to prevent mixing up same-typed primitives: `UserId(int)` vs `OrderId(int)`
- Replace float money with a decimal type or integer-cents representation with currency code
- Centralize formatting and comparison logic in the value object rather than in callers

---
description: Producer-Consumer architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [concurrency, messaging]
---
# Producer-Consumer

## Recognition

How to identify this pattern in code.

### Signatures

- Shared queue or buffer between producer and consumer threads/processes
- `put()`/`get()` or `enqueue()`/`dequeue()` calls on a shared data structure
- Bounded buffers with capacity limits, blocking on full/empty conditions
- Worker threads or processes consuming items from a queue in a loop
- Go typed `chan` with `range` over channel for consumer loops
- Java `BlockingQueue` `put()` / `take()` for bounded producer-consumer
- Python `multiprocessing.JoinableQueue` for cross-process work queues
- Rust `crossbeam-channel` for multi-producer multi-consumer channels
- Libraries: Python `queue.Queue`, `asyncio.Queue`, Java `BlockingQueue`, Go channels

### Confidence

- **high** -- Explicit producer threads writing to a shared `Queue` with consumer threads reading from it
- **medium** -- Async tasks feeding into a queue-like buffer consumed by separate coroutines or workers
- **low** -- Any pipeline where one component generates work and another processes it, even without a formal queue

## Architecture

Look for a shared buffer decoupling the rate of production from the rate of consumption.

### Review Checklist

- Queue is bounded to prevent unbounded memory growth under load
- Producers handle queue-full conditions (block, drop, or backpressure)
- Consumers handle empty queue gracefully (block or poll with timeout)
- Poison pill or shutdown signal exists for clean termination
- Error handling in consumers does not silently drop items

### Anti-patterns

- Unbounded queue that grows without limit when consumers fall behind
- Producer and consumer tightly coupled (direct function calls instead of queue)
- No shutdown mechanism -- threads/processes left dangling on exit
- Swallowing exceptions in the consumer loop, losing failed items permanently

---
description: Prop Drilling anti-pattern
type: anti-pattern
graphable: false
---
# Prop Drilling

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Same prop passed through 5+ component layers unchanged
- Intermediate components accepting and forwarding props they do not use in their own render logic
- "Tunneling" data through the component tree to reach a deeply nested child
- Component signatures with many props that are just pass-through for children
- Adding a new prop to a leaf component requires modifying every ancestor in the chain
- Props named identically across a chain of parent-child components with no transformation

### Confidence

- **high** -- a prop is threaded through 5 or more component levels, with intermediate components only forwarding it to children and never reading it, confirmed by tracing the prop through the component tree
- **medium** -- intermediate components accept props they do not reference in their own JSX/template, only passing them down via spread or explicit forwarding
- **low** -- a component's prop list includes several items that seem unrelated to its own responsibility, suggesting it is acting as a pass-through

## Impact

Fragile component hierarchy where adding, removing, or renaming a prop requires changes across many files, making refactoring painful.

### Symptoms

- Adding a feature to a leaf component requires modifying 5+ intermediate component files
- Intermediate components have bloated prop interfaces full of pass-through data
- Renaming a prop cascades into changes across many unrelated components
- Component reuse is difficult because components carry implicit dependencies on their position in the tree
- TypeScript or PropTypes definitions grow large with props the component itself does not use

### Remediation

- Use React Context, Vue provide/inject, or Angular services to make shared state available to deeply nested components without threading through intermediaries
- Adopt a state management library (Redux, Zustand, Pinia) for cross-cutting data that many components need
- Apply the composition pattern: pass children as props or slots so intermediate components do not need to know about leaf component data
- Restructure the component tree to flatten unnecessary nesting and reduce the depth data must travel
- Use the render props or compound component pattern to co-locate data requirements with the components that use them

---
description: Property graph model with typed nodes and edges carrying attributes
type: pattern
category: domain-model
abstraction: [data, graph]
---
# Property Graph

## Recognition

How to identify this pattern in code.

### Signatures

- `Node` and `Edge` or `Vertex` and `Relationship` class definitions with property maps
- Neo4j driver imports (`neo4j`, `py2neo`) or Cypher query strings (`MATCH (n)-[r]->(m)`)
- Gremlin traversal API: `g.V()`, `g.E()`, `addV()`, `addE()`, `has()`, `out()`, `in()`
- Python: `networkx.Graph`, `networkx.DiGraph` with `node[attr]` and `edge[attr]` access
- JS/TS: `neo4j-driver` package, `session.run('MATCH ...')` calls
- Go: `neo4j-go-driver`, custom `Node` and `Edge` structs with `Properties map[string]interface{}`
- Rust: `petgraph` with `NodeWeight` and `EdgeWeight` generics
- Java: `org.neo4j.driver`, TinkerPop `Graph` and `Traversal` interfaces
- `adjacency` list or matrix representations with per-node/per-edge metadata

### Confidence

- **high** -- Neo4j/Gremlin client with Cypher or Gremlin traversal queries, or Node/Edge classes with typed properties and relationship types
- **medium** -- networkx or petgraph usage with attributed nodes and edges for domain modeling
- **low** -- Adjacency list with basic metadata but no explicit graph schema or typed relationships

## Architecture

### When to use
- Domains with rich, many-to-many relationships where traversal depth matters (knowledge graphs, social networks, fraud detection)
- When query patterns involve multi-hop traversals, shortest paths, or pattern matching across relationships
- Schema-flexible environments where new relationship types emerge frequently

### Anti-patterns
- Using a property graph for simple tabular data that would be better served by a relational model
- Unbounded traversals without depth limits, causing query timeouts on large graphs
- Treating the graph as a document store by cramming all data into node properties instead of modeling relationships

### Complements
- [graph](/concepts/graph) — property graph is a specialized form of the generic graph model
- [social-graph](/concepts/social-graph) — social networks are a common property graph application
- [search-index](/concepts/search-index) — graph data often needs full-text search over node properties

## Impact

A property graph model fundamentally shapes query patterns and performance characteristics. Traversal-heavy workloads scale differently than relational joins, requiring specialized indexing, query profiling, and capacity planning around graph density and traversal depth.

---
description: Property-Based Testing architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [testing]
---
# Property-Based Testing

## Recognition

How to identify this pattern in code.

### Signatures

- `@given` decorator with `hypothesis` strategies in Python tests
- `hypothesis.strategies` imports (`st.integers()`, `st.text()`, `st.lists()`)
- `QuickCheck` and `Arbitrary` instances in Haskell tests
- `fast-check` or `jsverify` imports in JavaScript/TypeScript tests
- `@Property` annotations with `jqwik` in Java tests
- Strategy-based input generation (`st.builds()`, `fc.record()`, custom strategy composition)
- Shrinking on failure: test output shows minimized counterexamples

### Confidence

- **high** — `@given` or equivalent decorator with strategy composition, and tests assert invariants rather than specific input/output pairs
- **medium** — Property testing library imported but tests use fixed seeds or narrow strategies that behave like example-based tests
- **low** — Randomized test data generation (e.g., `random.randint` in a loop) without a property testing framework or shrinking

## Architecture

Look for tests that assert universal properties (invariants) over generated inputs rather than checking specific examples.

### Review Checklist

- Properties express genuine invariants (idempotency, round-trip, commutativity) not just "does not throw"
- Custom strategies model the actual domain constraints (valid email formats, bounded integers, non-empty lists)
- Shrinking is enabled so failures produce minimal reproducible counterexamples
- Test database or seed is logged for reproducibility when a property fails
- Stateful property tests cover sequences of operations where applicable

### Anti-patterns

- Writing property tests that only assert the function does not crash, without checking meaningful output properties
- Overly constrained strategies that reduce to a handful of fixed inputs, defeating the purpose of generation
- Ignoring shrunk counterexamples and debugging against the original large input
- No CI integration for property tests because they are "too slow" -- use smaller example counts with periodic full runs

---
description: Prototype architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Prototype

## Recognition

How to identify this pattern in code.

### Signatures

- Creating objects by cloning existing instances rather than constructing from scratch
- `clone()` methods on domain objects
- `copy()` / `deepcopy()` (Python `copy` module)
- `Object.assign()` or spread operator (`{...obj}`) for object creation from templates
- Prototype chains in JavaScript (`Object.create()`)
- Prototype registry or catalog of pre-configured instances
- `Cloneable` interface (Java)

### Confidence

- **high** -- Explicit `clone()` method with a prototype registry that returns copies of pre-configured template objects
- **medium** -- `deepcopy()` or spread-based cloning used to create variants of a base configuration or template
- **low** -- Generic object copying without a clear prototype/template intent (could be defensive copying)

## Architecture

Look for pre-configured template objects that are cloned to create new instances, avoiding costly construction.

### Review Checklist

- Deep copy vs shallow copy semantics are explicitly chosen and documented
- Mutable nested objects are deep-copied to prevent shared-state bugs
- Prototype registry is initialized with valid, complete template objects
- Clone method maintains class invariants (cloned object is in a valid state)
- Circular references in the object graph are handled during cloning

### Anti-patterns

- Shallow copy of objects with mutable nested state, causing unintended sharing
- Clone method that skips initialization logic required by the class contract
- Using prototype pattern when a simple constructor or factory would suffice
- No prototype registry, requiring callers to manage their own template instances

---
description: Proxy architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Proxy

## Recognition

How to identify this pattern in code.

### Signatures

- Class implementing the same interface as the real object but controlling access to it
- Lazy loading proxies that defer object creation until first use
- Caching proxies that return stored results for repeated calls
- Protection proxies that check permissions before delegating
- Classes named `*Proxy`, `Virtual*`, `Remote*`, `Lazy*`
- Virtual proxy for expensive objects (large images, database connections)
- Remote proxies hiding network communication behind a local interface

### Confidence

- **high** -- Class with the same interface as the subject that holds a reference to the real object and conditionally delegates calls
- **medium** -- Lazy initialization wrapper or access-control gate that defers to an underlying implementation
- **low** -- Simple wrapper that delegates all calls without adding any access control, caching, or lazy behavior

## Architecture

Look for the proxy providing transparent access control without leaking its presence to the client.

### Review Checklist

- Proxy implements the exact same interface as the real subject
- Client code is unaware whether it holds a proxy or the real object
- Proxy responsibility is singular: access control, lazy loading, caching, or remote access -- not all at once
- Lazy proxies handle initialization thread-safely in concurrent environments
- Caching proxies define clear invalidation strategy

### Anti-patterns

- Proxy that exposes additional methods not on the real subject's interface (breaks substitutability)
- Caching proxy with no invalidation -- stale data served indefinitely
- Protection proxy that duplicates authorization logic already handled elsewhere
- Proxy chains where multiple proxies wrap each other without clear purpose

See also: decorator

---
description: Publish-Subscribe architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [messaging, integration]
---
# Publish-Subscribe

## Recognition

How to identify this pattern in code.

### Signatures

- Topic or channel-based messaging: `publish(topic, message)`, `subscribe(topic, handler)`
- Fan-out delivery: all subscribers receive every message on a topic
- Topic declarations, channel names, or subject strings in configuration
- Libraries: Redis Pub/Sub, NATS subjects, Google Pub/Sub, AWS SNS, MQTT, Kafka topics
- Event emitters with `on(event_name, callback)` or `addEventListener` patterns
- Subscription management: subscribe, unsubscribe, subscription filters

### Confidence

- **high** -- explicit topic-based publish with multiple independent subscribers receiving every message
- **medium** -- event emitter pattern with named events and multiple listeners
- **low** -- broadcast mechanism where components receive notifications but routing is implicit

## Architecture

Look for decoupled producers and consumers communicating through named topics with fan-out delivery semantics.

### Review Checklist

- Subscribers are idempotent (duplicate delivery is handled gracefully)
- Topic naming convention is consistent and documented
- Subscriber failures do not block other subscribers on the same topic
- Message ordering guarantees are understood and match requirements
- Backpressure handling exists for slow subscribers

### Anti-patterns

- Using pub/sub for point-to-point messaging where only one consumer should process each message
- Subscribers with side effects that break when receiving duplicate messages
- Topic explosion: creating a new topic per entity instead of using message filtering
- No monitoring of subscriber lag or dropped messages

See also: observer (in-process variant)

---
description: Race Condition anti-pattern
type: anti-pattern
testable: true
graphable: false
---
# Race Condition

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Unsynchronized read-modify-write on shared mutable state (`count = count + 1` without a lock)
- Missing locks or mutexes around shared mutable data accessed by multiple threads or goroutines
- Check-then-act without atomicity (`if not exists(key): create(key)`)
- `if not exists then create` pattern without locking or compare-and-swap
- Concurrent map or dictionary access without a mutex or concurrent-safe data structure

### Confidence

- **high** -- shared mutable state is read and written by multiple threads/goroutines with no synchronization primitive in scope
- **medium** -- check-then-act pattern on shared resources without atomic operations or locks visible in the same function
- **low** -- global or module-level mutable variables accessed from functions that could plausibly be called concurrently

## Impact

Intermittent, hard-to-reproduce bugs that corrupt data and erode trust in the system.

### Symptoms

- Tests pass locally but fail intermittently in CI under parallel execution
- Data inconsistencies appear in production with no corresponding error logs
- Duplicate records created from concurrent requests that both passed a uniqueness check
- Counter values are lower than expected after concurrent increments
- Debugging is nearly impossible because the bug disappears under observation (Heisenbugs)

### Remediation

- Protect shared mutable state with a mutex, lock, or synchronized block appropriate to the language
- Use atomic operations (compare-and-swap, atomic increment) for simple counters and flags
- Replace check-then-act with atomic upsert operations (`INSERT ... ON CONFLICT`, `putIfAbsent`)
- Use concurrent-safe data structures (ConcurrentHashMap, sync.Map) instead of locking around standard collections
- Add race detector tools to CI (Go race detector, ThreadSanitizer) to catch races before production

---
description: Rate Limiting/Throttling architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [security, resilience]
---
# Rate Limiting/Throttling

## Recognition

How to identify this pattern in code.

### Signatures

- Request counters per client/IP with time window tracking
- Algorithm implementations: sliding window, token bucket, leaky bucket, fixed window
- HTTP `429 Too Many Requests` response status code
- Response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`
- Libraries: `ratelimit` (Python), `express-rate-limit` (Node), `rack-attack` (Ruby)
- Redis-based counters with TTL for distributed rate limiting (`INCR` + `EXPIRE`, `SETNX`)
- Nginx `limit_req` / `limit_conn` directives in configuration

### Confidence

- **high** -- rate limit middleware with configurable thresholds, 429 responses with rate limit headers, and a counter store (Redis/in-memory)
- **medium** -- request counting logic or throttle decorators present but no standard rate limit headers returned
- **low** -- delays or sleep calls injected to slow down processing (naive throttling without proper rate limiting)

## Architecture

Look for consistent enforcement at the API gateway or middleware layer with configurable limits per client or endpoint.

### Review Checklist

- Rate limits are applied at the correct granularity (per user, per API key, per IP, per endpoint)
- Distributed deployments share rate limit state (Redis or equivalent) to prevent per-instance limits
- Rate limit responses include standard headers so clients can self-throttle
- Different tiers or endpoints have appropriate limits (auth endpoints stricter, read endpoints more lenient)
- Rate limiting is applied before expensive operations (not after processing the request)

### Anti-patterns

- Per-instance rate limiting in a multi-replica deployment (each replica allows the full limit)
- No rate limit headers in responses (clients cannot adapt their request rate)
- Applying the same limit to all endpoints regardless of cost or sensitivity
- Rate limiting only by IP (breaks for clients behind NAT or shared proxies)

---
description: Role-Based Access Control architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [security]
---
# Role-Based Access Control

## Recognition

How to identify this pattern in code.

### Signatures

- Role definitions with associated permissions (`admin`, `editor`, `viewer`)
- Permission checks: `has_role()`, `has_permission()`, `@requires_role`, `authorize()`
- Middleware or decorators enforcing role requirements on routes or actions
- Role-permission mapping tables in database schemas or config files
- K8s RBAC: `Role`, `ClusterRole`, `RoleBinding`, `ClusterRoleBinding` manifests
- User-role assignment logic or admin interfaces for role management

### Confidence

- **high** -- role-permission mapping table, middleware enforcing role checks on endpoints, and role assignment to users/groups
- **medium** -- role-based conditionals in code (`if user.role == "admin"`) but no formal permission model
- **low** -- user types or levels that loosely map to access tiers without explicit role-permission structure

## Architecture

Look for a clean separation between role definitions, permission assignments, and enforcement points.

### Review Checklist

- Roles follow least-privilege principle (no overly broad `superadmin` that bypasses all checks)
- Permission checks happen at the enforcement layer (middleware/guard), not scattered through business logic
- Role hierarchy is explicit if it exists (admin inherits editor permissions by declaration, not by duplicating them)
- Default role for new users is the most restrictive
- Role changes take effect immediately (no stale cached role data)
- K8s RBAC: namespace-scoped Roles preferred over ClusterRoles where possible

### Anti-patterns

- Hardcoding role names in business logic instead of checking permissions
- God role that bypasses all authorization checks
- Checking roles at the UI layer but not enforcing on the API (cosmetic-only access control)
- Role explosion with one role per user instead of composable permission sets

---
description: Reactive Store — client-side state container with reactive subscriptions
type: pattern
graphable: true
abstraction: [frontend, data]
---
# Reactive Store

## Recognition

How to identify this pattern in code.

### Signatures

- `zustand` with `create()`, selector hooks, `set`/`get` state functions (React)
- `@reduxjs/toolkit` with `createSlice`, `configureStore`, `useSelector`, `useDispatch` (React)
- `redux` with `createStore`, `combineReducers`, `connect`, action creators (React)
- `pinia` with `defineStore`, `storeToRefs`, option or setup store syntax (Vue)
- `vuex` with `createStore`, `mapState`, `mapGetters`, `mutations`, `actions` (Vue)
- `@ngrx/store` with `StoreModule`, `createReducer`, `createSelector`, `select` (Angular)
- `svelte/store` with `writable`, `readable`, `derived`, `$store` auto-subscription syntax (Svelte)
- `jotai` with `atom`, `useAtom`, `useAtomValue`, `useSetAtom` (React)
- `recoil` with `atom`, `selector`, `useRecoilState`, `useRecoilValue` (React)
- `mobx` with `makeAutoObservable`, `observer`, `action`, `computed` (React)
- Store persistence middleware: `persist`, `createJSONStorage`, localStorage/sessionStorage integration
- Devtools integration: `redux-devtools`, `__REDUX_DEVTOOLS_EXTENSION__`

### Confidence

- **high** -- Dedicated state management library with store creation, typed selectors, and reactive subscriptions driving UI updates
- **medium** -- Centralized state object with manual subscription or context-based reactivity, but no formal store library
- **low** -- Module-level variables or singletons shared across components with ad-hoc change notification

## Architecture

Look for a centralized state container that components subscribe to reactively, with well-defined mutation paths and selector-based reads.

### Review Checklist

- Store is segmented by domain (slices, modules, or atoms) rather than a single monolithic object
- State mutations go through defined actions or setters, never direct object mutation
- Selectors derive computed values instead of duplicating state
- Subscriptions are scoped so components only re-render when their selected slice changes
- Async operations (API calls) are separated from synchronous state updates
- Persistence and hydration are handled by middleware, not ad-hoc serialization in components

### Anti-patterns

- Storing server-fetched data in a client store instead of using a server-state library (TanStack Query, SWR)
- Every component subscribing to the entire store instead of selecting specific slices
- Duplicating derived data in the store instead of computing it with selectors
- Mixing UI state (modal open, tab index) and domain state (user, cart) in the same store slice
- No devtools integration, making state changes opaque during development

---
description: Reactor/Event Loop architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [concurrency, architectural]
---
# Reactor/Event Loop

## Recognition

How to identify this pattern in code.

### Signatures

- Single-threaded event loop dispatching I/O events to registered handlers
- Non-blocking I/O with callbacks, promises, or `async`/`await` syntax
- System calls: `select()`, `epoll()`, `kqueue()`, `IOCP`
- `asyncio.run()`, `loop.run_forever()`, event emitters, or `on('event', handler)`
- Libraries: Python `asyncio`/`twisted`, `libuv` (Node.js), Rust `tokio`/`mio`, Java NIO/Netty

### Confidence

- **high** -- Explicit event loop with `async def`/`await`, registered I/O handlers, and non-blocking socket operations
- **medium** -- Callback-based I/O handling without explicit loop management (Node.js default runtime model)
- **low** -- Any non-blocking I/O with event notification, even without a formal reactor abstraction

## Architecture

Look for a single-threaded event loop multiplexing I/O across many connections without blocking.

### Review Checklist

- No blocking calls inside the event loop (file I/O, DNS, CPU-heavy work offloaded to thread pool)
- Callback chains or async functions handle errors at each step, not just the top level
- Connection lifecycle is managed (timeouts, cleanup on disconnect)
- Backpressure is applied when write buffers fill up
- Graceful shutdown drains in-flight events before stopping the loop

### Anti-patterns

- Blocking the event loop with synchronous I/O or CPU-bound computation
- Deeply nested callback chains without error propagation (callback hell)
- Spawning a new event loop per request instead of multiplexing on one loop
- Ignoring backpressure -- writing faster than the socket can drain

---
description: Read-Through Cache architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [data]
---
# Read-Through Cache

## Recognition

How to identify this pattern in code.

### Signatures

- Cache that loads from the backing source automatically on miss (vs cache-aside where the caller loads)
- Cache-as-data-source pattern where callers only interact with the cache
- `CacheLoader` interface implementations
- Guava `LoadingCache` or `CacheBuilder.newBuilder().build(loader)`
- Caffeine `Caffeine.newBuilder().build(loader)`
- `@Cacheable` annotation with implicit load-on-miss behavior
- Cache provider configured with a read-through loader function

### Confidence

- **high** -- `CacheLoader` or `LoadingCache` with explicit loader function, or cache configured as the sole data access layer
- **medium** -- `@Cacheable` annotations where the framework handles loading transparently
- **low** -- Manual cache-aside code where the load logic is tightly coupled to the cache check (looks like read-through but is caller-managed)

## Architecture

Look for a cache layer that transparently loads data from the source on a miss, hiding the backing store from callers.

### Review Checklist

- Loader function handles source failures gracefully (no caching of error responses)
- Cache eviction policy matches data volatility (TTL appropriate for freshness requirements)
- Bulk loading is supported for batch access patterns, not just single-key lookups
- Cache warming strategy exists for cold starts to avoid a thundering herd on first access
- Null/missing values are handled explicitly (negative caching or passthrough)

### Anti-patterns

- Caching error responses or exceptions from the loader, serving stale errors to subsequent callers
- No TTL or eviction, causing the cache to serve stale data indefinitely
- Caller bypassing the cache to hit the source directly, defeating the read-through contract
- Loader function with side effects beyond data retrieval

---
description: Read-Write Lock architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [concurrency]
---
# Read-Write Lock

## Recognition

How to identify this pattern in code.

### Signatures

- Separate lock acquisition for read vs write operations
- Multiple concurrent readers allowed, exclusive access for writers
- `RLock`, `RWMutex`, `ReadWriteLock`, `shared_lock`/`unique_lock`
- `acquire_read()`/`acquire_write()` or `r_lock()`/`w_lock()` method pairs
- Libraries: Go `sync.RWMutex`, Java `ReentrantReadWriteLock`, Rust `std::sync::RwLock`, C++ `std::shared_mutex`
- Python has no stdlib RWLock; use `readerwriterlock` package or custom implementation

### Confidence

- **high** -- Explicit `RWMutex` or `ReadWriteLock` with distinct read/write acquisition paths
- **medium** -- Custom lock implementation distinguishing between shared and exclusive access
- **low** -- Any locking scheme where reads are treated differently from writes, even with a regular mutex

## Architecture

Look for shared resources protected by a lock that permits concurrent reads but serializes writes.

### Review Checklist

- Write starvation is addressed (writers eventually acquire the lock even under heavy read load)
- Lock scope is minimal -- held only for the duration of the critical section
- Upgrade from read lock to write lock is either atomic or explicitly disallowed (no deadlock risk)
- Lock acquisition has a timeout to prevent indefinite blocking

### Anti-patterns

- Using a read-write lock where a simple mutex would suffice (premature optimization)
- Holding the write lock during I/O or network calls (long lock hold times starve readers)
- Nested lock acquisition without consistent ordering (deadlock risk)
- Read lock acquired but the code path mutates shared state

---
description: Refresh-Ahead Cache architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [data, resilience]
---
# Refresh-Ahead Cache

## Recognition

How to identify this pattern in code.

### Signatures

- Proactive cache refresh before TTL expiry
- Background refresh threads or async reload tasks
- `refreshAfterWrite` configuration (Caffeine, Guava)
- Probabilistic early expiration (cache entries refreshed before nominal TTL)
- Cache warming on startup or scheduled pre-population
- Separate refresh executor or thread pool for async reloads
- Entries served stale while refresh is in progress

### Confidence

- **high** -- `refreshAfterWrite` with an async reload function, or explicit background thread refreshing entries before expiry
- **medium** -- Scheduled cache warming jobs that periodically repopulate hot keys
- **low** -- Short TTLs with frequent cache misses that approximate refresh-ahead behavior without explicit implementation

## Architecture

Look for a cache that proactively refreshes entries before they expire, ensuring callers always get a cache hit.

### Review Checklist

- Refresh executes asynchronously and does not block the caller serving the stale value
- Refresh thread pool is bounded to prevent resource exhaustion under heavy load
- Failed refreshes keep the existing cached value rather than evicting it
- Only hot keys are refreshed (cold keys are allowed to expire normally)
- Refresh interval is shorter than TTL to guarantee overlap

### Anti-patterns

- Synchronous refresh that blocks callers, negating the latency benefit
- Refreshing all cached keys regardless of access frequency (wasted resources)
- No fallback when the refresh source is unavailable, causing cache entries to expire with no replacement
- Unbounded refresh thread pool that can saturate the backing data source

---
description: Registry domain model — entities with lifecycle states, metadata, and lookups
type: domain-model
abstraction: [data]
---
# Registry

## Recognition

### Signatures

- Entity classes with `status`/`state` fields and defined lifecycle transitions
- CRUD operations as the primary API surface
- Unique identifiers (UUID, slug, email) used for lookups
- Metadata/tags/labels attached to entities
- Soft delete (status=archived/deleted) rather than hard delete
- Search/filter by multiple fields
- Audit fields (created_at, updated_at, created_by)
- Entity relationships: one-to-many, many-to-many via join tables
- CRM-like patterns: contacts → companies → interactions

### Confidence

- **high** — entities with explicit lifecycle states, CRUD API, unique identifiers, and audit trail
- **medium** — standard CRUD with status fields but no defined state machine
- **low** — simple database tables with basic CRUD but no lifecycle or metadata patterns

---
description: Reinventing the Wheel anti-pattern
type: anti-pattern
graphable: false
---
# Reinventing the Wheel

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Custom JSON parser when `json.loads()` or equivalent exists
- Custom HTTP client wrapping raw sockets instead of using `requests`, `httpx`, or `fetch`
- Custom retry logic reimplementing exponential backoff instead of using `tenacity`, `resilience4j`, or similar
- Custom logging framework instead of the language's standard logging library
- Hand-rolled ORM or query builder instead of using established libraries
- Reimplemented standard library functions (custom `deepcopy`, `uuid`, `base64`, string formatting)

### Confidence

- **high** -- a module reimplements functionality that is available in the standard library or a widely-adopted, well-maintained library, and the custom version lacks edge case handling present in the established solution
- **medium** -- a utility module provides functionality (retry, caching, validation) that overlaps significantly with a popular library already in the project's dependency tree
- **low** -- a helper function reimplements a small piece of standard library functionality, possibly for a legitimate reason (performance, reduced dependencies) but without documentation of the rationale

## Impact

Bugs in already-solved problems, ongoing maintenance burden, and missing edge cases that battle-tested libraries handle correctly.

### Symptoms

- Custom implementations break on edge cases (Unicode, timezone, encoding) that standard libraries handle
- Team members spend time maintaining infrastructure code instead of business logic
- Security vulnerabilities in custom crypto, parsing, or serialization code
- New developers are confused by bespoke utilities instead of recognizable standard patterns
- Bug reports trace back to reimplemented functionality rather than business logic

### Remediation

- Audit utility and infrastructure code for overlap with standard library or well-established packages
- Replace custom implementations with standard libraries, documenting any edge cases that motivated the original code
- If a custom implementation is justified (performance, zero-dependency constraint), document the rationale and add comprehensive tests covering known edge cases
- Add dependency review to the design phase: before writing a utility, check if a maintained solution exists
- Create a "build vs. buy" decision log for infrastructure components so the rationale is preserved

---
description: Repository architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design, data]
---
# Repository

## Recognition

How to identify this pattern in code.

### Signatures

- Classes ending in `Repository` or `Repo` (e.g., `UserRepository`, `OrderRepo`)
- CRUD methods: `find()`, `find_by_id()`, `save()`, `delete()`, `list()`
- Interface or abstract base class defining data access contract
- Domain objects have no knowledge of storage mechanism
- SQLAlchemy repository classes wrapping session queries
- Spring Data `@Repository` annotation or `JpaRepository` interface
- Separate `repositories/` directory or module

### Confidence

- **high** -- classes named `*Repository` with CRUD methods that accept and return domain objects
- **medium** -- data access abstracted behind an interface but not explicitly named Repository
- **low** -- service layer delegates to a class that wraps raw queries

## Architecture

Look for clean separation between domain logic and data access with a consistent query interface.

### Review Checklist

- Repository returns domain objects, not raw database rows or ORM models
- Repository interface is defined independent of the storage implementation
- Query logic lives inside the repository, not leaked into services or controllers
- Repositories are injected as dependencies, not instantiated inline
- Bulk operations and pagination are handled without bypassing the repository

### Anti-patterns

- Repository methods that return ORM-specific objects (leaking persistence concerns)
- Fat repositories with business logic mixed into query methods
- One repository per table instead of per aggregate root
- Bypassing the repository with direct queries elsewhere in the codebase

---
description: Request path flow — synchronous request through a handler chain with response
type: flow-shape
abstraction: [api, integration]
---
# Request Path

## Recognition

### Signatures

- HTTP route handler calling a service layer which calls a repository/data layer
- Middleware chain: auth → validation → handler → response serialization
- Express `app.get()` → controller → service → repository chain
- FastAPI `@app.get()` → dependency injection → service → ORM
- Spring `@RestController` → `@Service` → `@Repository`
- Go `http.HandleFunc` → handler → service → store
- Request/response DTOs at API boundary, domain models internally
- Error handling middleware that catches and formats responses

### Confidence

- **high** — clear layered handler chain: route → middleware → controller → service → repository → database, with DTOs at boundaries
- **medium** — handler calls service which calls database, but without clean layering or DTOs
- **low** — handler directly queries database with no service layer

---
description: Request-Reply architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [messaging, integration]
---
# Request-Reply

## Recognition

How to identify this pattern in code.

### Signatures

- Correlation ID linking request messages to their responses
- Reply-to queue or topic specified in message headers
- Temporary or exclusive response queues created per requester
- RPC-over-messaging: `call()`, `rpc()`, or `request()` methods that block or return futures
- NATS request-reply: `nc.request(subject, payload, timeout)`
- RabbitMQ RPC: `reply_to` and `correlation_id` properties on AMQP messages
- Timeout configuration for waiting on the reply

### Confidence

- **high** -- correlation ID plus reply-to destination with timeout handling
- **medium** -- message exchange where producer blocks waiting for a response on a known topic
- **low** -- fire-and-forget publish followed by a separate poll for results

## Architecture

Look for synchronous request-response semantics implemented over an asynchronous messaging layer using correlation IDs and reply destinations.

### Review Checklist

- Every request includes a unique correlation ID and a reply-to destination
- Timeout is enforced on the requester side with clear error handling on expiry
- Temporary reply queues are cleaned up after the response is received or timeout fires
- Correlation ID is propagated through any intermediate services for traceability
- Responder handles duplicate requests idempotently

### Anti-patterns

- Missing timeout on the request side (blocking forever on a lost reply)
- Reply queues not cleaned up, leaking resources on the broker
- Using request-reply where fire-and-forget or pub-sub would be simpler
- Correlation ID collisions from non-unique ID generation

---
description: REST API architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [api, integration]
---
# REST API

## Recognition

How to identify this pattern in code.

### Signatures

- HTTP methods mapped to CRUD operations (GET=read, POST=create, PUT/PATCH=update, DELETE=delete)
- Resource-based URL paths: `/users`, `/users/123`, `/users/123/orders`
- HTTP status codes used semantically (200, 201, 204, 400, 404, 409, 422)
- JSON request/response bodies with content-type `application/json`
- OpenAPI/Swagger specification files (`openapi.yaml`, `swagger.json`)
- HATEOAS links in responses (`_links`, `href`)
- Versioning in URL path (`/v1/`, `/v2/`) or headers (`Accept: application/vnd.api.v1+json`)

### Confidence

- **high** -- resource-based URLs with correct HTTP method semantics, OpenAPI spec, proper status codes
- **medium** -- JSON API with URL patterns that suggest resources but methods may be overloaded (POST for everything)
- **low** -- HTTP endpoints returning JSON but URLs are action-based (`/getUser`, `/createOrder`) rather than resource-based

## Architecture

Look for resource-oriented URL design with correct HTTP method semantics and meaningful status codes.

### Review Checklist

- URLs represent resources (nouns), not actions (verbs)
- HTTP methods match their intended semantics (GET is safe and idempotent, PUT is idempotent)
- Status codes are used correctly (not 200 for everything with error details in the body)
- Pagination is implemented for list endpoints (cursor-based or offset/limit)
- API versioning strategy is consistent across all endpoints
- Error responses follow a consistent format with actionable messages

### Anti-patterns

- Using POST for all operations regardless of intent (RPC-over-HTTP)
- Returning 200 OK for error conditions with error details only in the response body
- Deeply nested resource URLs beyond two levels (`/a/1/b/2/c/3/d/4`)
- No pagination on list endpoints that can return unbounded results

---
description: Result/Either Type architectural pattern
type: pattern
testable: true
graphable: false
abstraction: [design, error-handling]
---
# Result/Either Type

## Recognition

How to identify this pattern in code.

### Signatures

- `Result<T, E>`, `Ok()`, `Err()` in Rust code
- `Either<L, R>`, `Left()`, `Right()` from fp-ts, Arrow (Kotlin), or Cats (Scala)
- `match` or `fold` on result types to handle success and failure branches
- No exception throwing for expected/recoverable failures
- Railway-oriented programming: chained `.map()`, `.flatMap()`, `.and_then()` on results
- Custom `Result` or `Outcome` classes with `is_ok()` / `is_err()` methods in Python or TypeScript
- `returns` library in Python with `Result`, `Success`, `Failure`

### Confidence

- **high** — Consistent use of `Result`/`Either` across module boundaries, with `match`/`fold` at call sites and no exceptions for domain errors
- **medium** — Result type used in some modules but exceptions still thrown in others for the same category of errors
- **low** — Functions returning tuples like `(value, error)` or nullable error fields without a formal result type

## Architecture

Look for explicit error paths encoded in return types rather than exception-based control flow for expected failures.

### Review Checklist

- Domain errors are represented as typed variants in the error channel, not generic strings or exception classes
- Result types are propagated through the call chain, not unwrapped immediately at each layer
- Error mapping transforms low-level errors into domain-appropriate errors at boundary crossings
- The `match`/`fold` at the top level handles all error variants exhaustively
- Unexpected errors (panics, runtime exceptions) are still handled separately from typed result errors

### Anti-patterns

- Wrapping every possible error in a Result including panics and programming bugs that should crash
- Calling `.unwrap()` or `.get()` everywhere, discarding the error channel and defeating the purpose
- Mixing Result returns and exception throwing for the same class of errors within a module
- Deeply nested `match` blocks instead of composing results with `map`/`flatMap` chains

---
description: Retry architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [resilience, integration]
---
# Retry with Backoff

## Recognition

How to identify this pattern in code.

### Signatures

- `tenacity` imports and decorators in Python (`@retry`, `wait_exponential`, `stop_after_attempt`)
- `polly` policies in .NET (`Policy.Handle<Exception>().WaitAndRetryAsync()`)
- `resilience4j-retry` configuration in Java (`RetryConfig`, `RetryRegistry`)
- `retry` package usage in Go (`retry.Do()`, `retry.Attempts()`)
- `backoff` decorator with exponential delay configuration (`@backoff.on_exception`)
- `max_retries` configuration parameters on client or operation config
- `retry_on_exception` predicates distinguishing retryable from non-retryable errors
- Dead letter queue routing on retry exhaustion (`DLQ`, `dead_letter`)

### Confidence

- **high** -- Library-specific imports (`tenacity`, `polly`, `resilience4j-retry`) with exponential backoff configuration and max retry bounds
- **medium** -- `max_retries` and `retry_on_exception` logic with dead letter queue on exhaustion, but using custom retry loops instead of a library
- **low** -- Simple retry loops with fixed delays or unbounded retries, without explicit backoff or DLQ handling

## Architecture

Look for bounded retries with exponential backoff, jitter, and a dead-letter path.

### Review Checklist

- Max retry count is configured and bounded — no infinite retry loops
- Backoff is exponential with jitter (not fixed delay — avoids thundering herd)
- Retryable vs. non-retryable errors are distinguished (don't retry 400s)
- Dead-letter queue or equivalent captures permanently failed operations
- Retry state is observable (metrics on attempt count and DLQ depth)

### Anti-patterns

- Fixed-delay retries — all clients retry simultaneously after an outage
- Retrying non-idempotent operations without deduplication
- No max retry limit — stuck requests consume resources indefinitely
- Silent discard of failed operations (no dead-letter, no alert)

---
description: Ring Buffer architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [data, concurrency]
---
# Ring Buffer

## Recognition

How to identify this pattern in code.

### Signatures

- Fixed-size circular buffer with head and tail pointers (or read/write indices)
- Wrap-around logic using modulo arithmetic (`index % capacity`)
- `collections.deque(maxlen=N)` in Python
- Lock-free SPSC (single-producer single-consumer) or MPSC queue implementations
- Overwrite-oldest policy when buffer is full (no blocking, no resize)
- `RingBuffer`, `CircularBuffer`, `CircularQueue` class names
- Pre-allocated array with fixed capacity and no dynamic growth
- Used in logging pipelines, audio processing, network I/O buffers, LMAX Disruptor

### Confidence

- **high** -- Fixed-size buffer with modulo wrap-around, head/tail pointers, and overwrite-on-full semantics
- **medium** -- `deque(maxlen=N)` or bounded queue with FIFO eviction but no explicit ring structure
- **low** -- Fixed-size array with manual index management that may be a ring buffer

## Architecture

Look for correct bounded buffer semantics with wrap-around indexing and clear full/empty distinction.

### Review Checklist

- Buffer capacity is fixed at construction and never resized
- Full vs empty state is distinguishable (not ambiguous when head equals tail)
- Wrap-around uses modulo or bitwise AND (power-of-two sizing)
- Thread safety is addressed: either single-threaded use, lock-free atomics, or explicit locking
- Overwrite policy is intentional and documented (data loss is expected and acceptable)
- Read and write operations are O(1)

### Anti-patterns

- Resizing the buffer dynamically (defeats the purpose of bounded memory)
- No distinction between full and empty states when head equals tail
- Using a ring buffer where an unbounded queue is needed (silent data loss)
- Locking on every read/write in a hot path where a lock-free design is required

---
description: Route Guard — conditional access control on route navigation
type: pattern
graphable: true
abstraction: [frontend, security]
---
# Route Guard

## Recognition

How to identify this pattern in code.

### Signatures

- `clientLoader` or `loader` returning `redirect()` based on auth state (React Router)
- `beforeRouteEnter`, `beforeEach`, `beforeRouteLeave` navigation guards (Vue Router)
- `CanActivate`, `CanDeactivate`, `CanLoad` guard interfaces and `canActivate` route property (Angular)
- `handle` hook in `hooks.server.ts` checking session before resolving (SvelteKit)
- `middleware/` directory with named middleware functions checking auth (Nuxt)
- Next.js `middleware.ts` with `NextResponse.redirect` or `NextResponse.rewrite`
- Higher-order components or wrapper components checking auth state and redirecting (`<ProtectedRoute>`, `<AuthGuard>`)
- Token or session checks before allowing navigation: `isAuthenticated`, `hasRole`, `checkPermission`
- Redirect to login page with return URL parameter on guard failure

### Confidence

- **high** -- Framework navigation guard API (beforeEach, CanActivate, middleware) with explicit auth check, role verification, and redirect on failure
- **medium** -- Wrapper component or layout that conditionally renders children based on auth state, with redirect side effect
- **low** -- Ad-hoc auth check inside a page component's mount lifecycle that navigates away on failure

## Architecture

Look for a centralized or per-route gate that evaluates access conditions before rendering the target view, with well-defined redirect behavior on denial.

### Review Checklist

- Guard logic is centralized or composable, not duplicated across individual page components
- Auth state is checked against a reliable source (token validation, session API) not just local storage
- Failed guards redirect to an appropriate destination (login page, 403 page) with return URL preserved
- Guards handle loading/pending auth state gracefully (show loading, not flash of protected content)
- Role and permission checks are granular enough for the application's access model
- Guards cover both initial page load and client-side navigation

### Anti-patterns

- Checking auth only on client-side navigation but not on direct URL access (server-side gap)
- Flash of protected content before the guard redirects (guard runs after render, not before)
- Hardcoded role strings scattered across guard implementations instead of a permissions abstraction
- Guards that silently fail, leaving the user on a broken or empty page instead of redirecting
- Duplicating guard logic in every page component instead of using route-level or layout-level guards

---
description: Router — URL-based navigation and view switching
type: pattern
graphable: true
abstraction: [frontend, integration]
---
# Router

## Recognition

How to identify this pattern in code.

### Signatures

- `react-router-dom` with `BrowserRouter`, `Routes`, `Route`, `useNavigate`, `useParams` (React)
- `vue-router` with `createRouter`, `RouterView`, `RouterLink`, `useRoute`, `useRouter` (Vue)
- `@angular/router` with `RouterModule`, `ActivatedRoute`, `Router`, route configuration arrays (Angular)
- SvelteKit file-based routing with `+page.svelte`, `+layout.svelte`, `$app/navigation` imports
- `next/router` or `next/navigation` with `useRouter`, `usePathname`, `useSearchParams` (Next.js)
- Nuxt file-based routing with `pages/` directory convention, `NuxtLink`, `navigateTo`
- Route definition objects with `path`, `element`/`component`, `children` properties
- Path parameters (`:id`, `[id]`, `{id}`), wildcard routes, catch-all segments
- Nested route configurations with `Outlet`, `RouterView`, or `router-outlet` placeholders
- Programmatic navigation: `navigate()`, `router.push()`, `router.navigate()`

### Confidence

- **high** -- Framework router library imported with route definitions mapping URL paths to components, navigation hooks, and parameter extraction
- **medium** -- URL-based conditional rendering that switches displayed content based on `window.location` or hash fragments, but without a formal router library
- **low** -- Manual `history.pushState` or hash-change listeners that update view state without structured route definitions

## Architecture

Look for a declarative mapping between URL paths and component trees, with support for nested layouts, parameter extraction, and programmatic navigation.

### Review Checklist

- Routes are defined declaratively in a central configuration, not scattered across components
- Nested routes use layout components to avoid re-rendering shared UI on navigation
- Route parameters are validated or typed before use in data fetching
- Navigation guards or loaders handle auth checks and data prefetching before rendering
- 404 and error routes are explicitly defined with appropriate fallback UI
- Code splitting is applied per route to avoid loading the entire app upfront

### Anti-patterns

- Defining routes inline across multiple files with no central route manifest
- Fetching data inside components after mount instead of using route-level loaders or guards
- Using string concatenation to build URLs instead of typed route helpers or path utilities
- Nested routes that re-fetch parent data because layout boundaries are not configured
- Catch-all routes that silently swallow navigation errors instead of showing meaningful feedback

---
description: Rule engine pattern for declarative business logic evaluation
type: pattern
category: domain-model
abstraction: [design, logic]
---
# Rule Engine

## Recognition

How to identify this pattern in code.

### Signatures

- `Rule`, `Condition`, `Action` class hierarchy or interfaces
- `decision_table` or `DecisionTable` data structures mapping conditions to outcomes
- `evaluate()`, `execute_rules()`, `fire_rules()` methods on engine or context objects
- `rule_engine`, `RuleEngine`, `BusinessRule` class or module names
- Python: `business-rules`, `durable-rules`, `rule-engine` library imports
- JS/TS: `json-rules-engine`, `nools`, rule definition objects with `conditions` and `event` keys
- Go: `grule-rule-engine`, `gorules`, custom rule evaluation with `Predicate` functions
- Rust: `zen-engine`, custom rule trait with `evaluate(&self, context: &Context) -> bool`
- Java: Drools imports (`org.kie`, `org.drools`), `@Rule` annotations, `KieSession` usage
- `predicate`, `when`, `then`, `priority`, `salience` keywords in rule definitions

### Confidence

- **high** -- Dedicated rule engine library (Drools, json-rules-engine, grule) with declarative rule definitions, evaluation context, and priority/salience ordering
- **medium** -- Custom Rule/Condition/Action classes with an evaluate loop and decision tables stored externally
- **low** -- Chain of if/else statements implementing business logic that could be expressed as rules but lacks a formal engine

## Architecture

### When to use
- Complex business logic that changes frequently and should be managed by non-developers
- Decision-heavy domains (insurance underwriting, loan approval, pricing engines) with many conditional paths
- Systems where rules need to be auditable, testable in isolation, and hot-reloadable without deployment

### Anti-patterns
- Embedding rule logic in application code instead of externalizing it, making changes require deployments
- No defined evaluation order, causing rule conflicts and non-deterministic outcomes
- Rules with side effects that modify shared state, making composition unpredictable

### Complements
- [strategy](/concepts/strategy) — rules often delegate to strategy implementations for their actions
- [specification](/concepts/specification) — specification pattern formalizes the condition side of rules
- [feature-flag](/concepts/feature-flag) — rule engines sometimes subsume feature flag logic

## Impact

A rule engine separates business logic from application code, enabling rapid policy changes but introducing a secondary execution model that must be tested, versioned, and monitored independently. Rule evaluation performance and conflict resolution become critical operational concerns.

---
description: Saga Orchestrator architectural pattern
graphable: true
abstraction: [messaging, integration]
---
# Saga Orchestrator

## Recognition

How to identify this pattern in code.

### Signatures

- Central coordinator class managing a sequence of saga steps (`SagaOrchestrator`, `SagaManager`, `SagaCoordinator`)
- Step sequence definition with forward action and compensating action per step
- Compensating actions that undo completed steps on failure
- Step status tracking (pending, completed, failed, compensated)
- Saga state machine persisted to a database or event store
- Distinct from choreography-based saga -- one service drives the flow, not distributed event reactions

### Confidence

- **high** -- dedicated orchestrator class with step definitions, compensation logic, and persisted saga state
- **medium** -- sequential service calls with rollback logic but no formal saga abstraction or state tracking
- **low** -- multi-service workflow with some error handling but no compensating actions or saga terminology

## Architecture

Look for a central coordinator driving distributed transactions through explicit steps with compensations.

### Review Checklist

- Every forward step has a corresponding compensating action defined
- Saga state is persisted so that recovery can resume or compensate after a crash
- Step execution is idempotent -- retrying a step does not cause duplicate side effects
- Compensation is executed in reverse order of completed steps
- The orchestrator handles partial failure -- it does not leave the system in an inconsistent state
- Timeouts are defined per step to prevent indefinite blocking

### Anti-patterns

- Missing compensation for one or more steps -- partial failure leaves inconsistent state
- Saga state kept only in memory -- a process crash loses the transaction progress
- Non-idempotent steps that produce duplicates on retry
- Orchestrator tightly coupled to step implementations instead of calling them through interfaces

---
description: Saga architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [integration, resilience]
---
# Saga

## Recognition

How to identify this pattern in code.

### Signatures

- `Temporal` workflow definitions with activity sequences and compensation logic
- `MassTransit` saga state machines (`MassTransitStateMachine`, `SagaStateMachineInstance`)
- `NServiceBus` saga classes (`Saga<TSagaData>`, `IAmStartedByMessages`)
- Axon saga annotations (`@SagaEventHandler`, `@StartSaga`, `@EndSaga`)
- Compensating transaction methods paired with forward steps
- `SagaStep` classes or interfaces with `execute()` and `compensate()` methods
- Step status tracking (pending, completed, compensating, compensated)
- Saga state persistence to a database or durable store
- Central coordinator class managing a sequence of saga steps (`SagaOrchestrator`, `SagaManager`, `SagaCoordinator`)
- Distinct from choreography-based saga -- one service drives the flow, not distributed event reactions

### Confidence

- **high** -- Framework-specific saga imports (Temporal, MassTransit, NServiceBus, Axon) with compensating transaction definitions and step state tracking
- **medium** -- `SagaStep` with `compensate()` methods and saga state persistence, but using a custom coordinator instead of a framework
- **low** -- Multi-step distributed operations with manual rollback logic but no formal saga orchestration or step state tracking

## Architecture

Look for correct compensation logic and failure handling across distributed steps.

### Review Checklist

- Each step has a corresponding compensating action
- Compensation is idempotent (safe to retry on partial failure)
- Saga coordinator tracks step state (pending, completed, compensated)
- Timeout handling exists for steps that may hang

### Orchestration Variant

In the orchestration variant, a central coordinator class (`SagaOrchestrator`, `SagaManager`, `SagaCoordinator`) drives the distributed transaction through an explicit sequence of steps. Each step defines a forward action and a compensating action. The orchestrator persists saga state so that recovery can resume or compensate after a crash. Compensation is executed in reverse order of completed steps. This is distinct from choreography-based saga where distributed event reactions drive the flow -- here one service owns the entire sequence.

Key review points for the orchestration variant:
- Saga state is persisted (not in-memory only) so a process crash does not lose transaction progress
- Step execution is idempotent -- retrying a step does not cause duplicate side effects
- The orchestrator handles partial failure without leaving the system in an inconsistent state
- The orchestrator calls steps through interfaces rather than being tightly coupled to implementations

### Anti-patterns

- Missing compensation for one or more steps (partial rollback)
- Compensating actions that can themselves fail without retry
- Using sagas where a simple two-phase operation would suffice
- Saga state kept only in memory -- a process crash loses the transaction progress
- Non-idempotent steps that produce duplicates on retry
- Orchestrator tightly coupled to step implementations instead of calling them through interfaces

---
description: Scatter-gather flow — request dispatched to multiple services, responses aggregated
type: flow-shape
abstraction: [integration]
---
# Scatter-Gather

## Recognition

### Signatures

- Parallel HTTP calls to multiple backends with results merged
- `Promise.all([serviceA.get(), serviceB.get(), serviceC.get()])`
- `asyncio.gather(fetch_prices(), fetch_inventory(), fetch_reviews())`
- Go `errgroup` dispatching concurrent requests to multiple services
- API gateway aggregating responses from multiple microservices
- Search federation: query sent to multiple indices, results ranked and merged
- Price comparison: same query to multiple providers, best result selected
- Timeout handling: return partial results if some services are slow
- GraphQL resolvers fetching from multiple data sources concurrently

### Confidence

- **high** — explicit parallel dispatch to N services with structured aggregation, timeout handling, and partial result support
- **medium** — parallel calls to multiple services but results merged ad-hoc without timeout or partial result handling
- **low** — sequential calls to multiple services that could be parallelized but aren't

---
description: Cron/Scheduler architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [lifecycle]
---
# Cron/Scheduler

## Recognition

How to identify this pattern in code.

### Signatures

- Cron expressions in config files or decorators (`"0 */5 * * *"`, `@crontab`)
- `APScheduler`, `schedule`, `celery.beat`, `node-cron`, `Quartz` library imports
- `@scheduled`, `@periodic_task`, `@cron` decorators on functions
- Kubernetes `CronJob` resources in manifests
- Periodic task registration at application startup
- Time-based trigger configuration in YAML, JSON, or environment variables
- Functions named `*_job`, `*_task`, `run_periodic_*`, `scheduled_*`

### Confidence

- **high** -- Cron expressions with a scheduler library, registered periodic tasks, and explicit job lifecycle management
- **medium** -- Kubernetes CronJob manifests or `time.sleep` loops with periodic execution, but no formal scheduler library
- **low** -- Manual `setInterval` / `time.sleep` polling without any scheduler framework or cron expression

## Architecture

Look for time-based triggers that invoke tasks on a recurring schedule with proper lifecycle management.

### Review Checklist

- Schedules are configurable (not hardcoded cron strings buried in code)
- Overlapping executions are handled (skip if previous run is still active, or queue)
- Failed jobs have retry logic or dead-letter handling
- Job execution is observable (start/end logging, duration metrics)
- Timezone handling is explicit and consistent across all schedules
- Graceful shutdown waits for in-progress jobs to complete

### Anti-patterns

- Hardcoded sleep loops used instead of a scheduler library
- No overlap protection -- long-running jobs stack up on each trigger
- Silent failure -- jobs fail without logging, alerting, or retry
- Schedule drift from using relative delays (`sleep(300)`) instead of wall-clock cron expressions

---
description: Schema-on-Read anti-pattern
type: anti-pattern
testable: true
graphable: false
---
# Schema-on-Read

## Recognition

How to identify this anti-pattern in code.

### Signatures

- JSON blobs stored in database columns without a defined schema
- `data["field"]` or `data.get("field")` access patterns with no prior validation
- `JSONB` columns accessed with string keys scattered throughout the codebase
- No Pydantic model, dataclass, or TypedDict used to deserialize JSON data
- `**kwargs` or `dict` passed through multiple layers without type narrowing
- API responses consumed as raw dicts without schema validation
- Configuration loaded from JSON/YAML and accessed with string keys directly
- Migration-free schema changes: new fields added to JSON blobs with no versioning

### Confidence

- **high** -- `JSONB` or `JSON` columns accessed via string keys in 10+ locations with no validation model, and `KeyError` exceptions in production logs
- **medium** -- JSON data consumed as raw dicts without Pydantic/dataclass deserialization, but no production errors yet
- **low** -- a few `data["key"]` accesses without validation, or dynamic config loaded from JSON without a schema

## Impact

Runtime KeyError exceptions, no type safety at boundaries, and schema drift as producers and consumers evolve independently.

### Symptoms

- `KeyError` or `TypeError` exceptions in production when accessing JSON fields
- Developers must read database contents to understand the structure of stored data
- Different parts of the codebase assume different shapes for the same JSON data
- Adding a new field requires searching all consumers to update their access patterns
- No IDE autocompletion or type checking for data extracted from JSON columns

### Remediation

- Define Pydantic models, dataclasses, or TypedDicts for all JSON structures at system boundaries
- Validate JSON data on read from the database or API, rejecting or defaulting missing fields
- Use JSON Schema or OpenAPI specifications to document and enforce the expected shape
- Add migration scripts or versioning when the JSON schema evolves
- Replace string-key access with typed attribute access through validated models

---
description: Search and inverted index pattern for full-text retrieval
type: pattern
category: domain-model
abstraction: [data, search]
---
# Search Index

## Recognition

How to identify this pattern in code.

### Signatures

- Elasticsearch client usage: `Elasticsearch()`, `client.index()`, `client.search()`, index mappings
- Solr configuration: `solrconfig.xml`, `schema.xml`, `SolrClient` or `SolrQuery` usage
- Meilisearch client: `meilisearch`, `client.index('...')`, `search()` calls
- Typesense client: `typesense`, collection schema definitions, `search_parameters`
- Python: `whoosh.index`, `tantivy` bindings, `haystack` search backend
- JS/TS: `@elastic/elasticsearch`, `meilisearch`, `typesense` package imports
- Go: `bleve` index creation, `olivere/elastic` client, `tantivy-go` bindings
- Rust: `tantivy::Index`, `tantivy::schema::Schema`, `IndexWriter` and `IndexReader`
- `analyzer`, `tokenizer`, `filter` configuration in index settings
- `inverted_index`, `index_name`, `mapping`, `field_type: text` declarations

### Confidence

- **high** -- Elasticsearch/Solr/Meilisearch client with index mappings, analyzers, and search queries with relevance scoring
- **medium** -- Tantivy or Whoosh index with custom tokenizers and full-text query parsing
- **low** -- SQL `LIKE '%term%'` queries or basic `tsvector` usage without dedicated search infrastructure

## Architecture

### When to use
- Full-text search across large document collections with relevance ranking
- Faceted navigation and filtering (e-commerce, catalogs, content platforms)
- Autocomplete, typeahead, and fuzzy matching requirements

### Anti-patterns
- Using the search index as the primary data store instead of syncing from a source of truth
- Not handling index lag — search results may be stale relative to the primary database
- Over-indexing every field, leading to bloated indices and slow write throughput

### Complements
- [cqrs](/concepts/cqrs) — search index often serves as the read model in a CQRS architecture
- [change-data-capture](/concepts/change-data-capture) — CDC feeds keep search indices in sync with the primary store
- [pagination](/concepts/pagination) — search results require cursor or offset-based pagination

## Impact

Search indices introduce an eventually-consistent read path that must be kept in sync with the authoritative data store. Monitoring must track index lag, query latency percentiles, and indexing throughput to ensure search quality does not degrade silently.

---
description: Secret Management architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [security, infrastructure]
---
# Secret Management

## Recognition

How to identify this pattern in code.

### Signatures

- Vault integration (`hashicorp/vault`, `vault` CLI, `VAULT_ADDR`)
- Sealed secrets or external-secrets operator in Kubernetes
- `pass` store for credential management (`pass insert`, `pass show`)
- KMS integration (AWS KMS, GCP KMS, Azure Key Vault)
- `secretKeyRef` in K8s manifests referencing Secret objects
- Never-hardcoded credentials with rotation policies
- Secret scanning in CI (`gitleaks`, `trufflehog`, `detect-secrets`)
- `.env` files in `.gitignore` with template `.env.example` checked in

### Confidence

- **high** -- Dedicated secret store integration (Vault, external-secrets operator, `pass`) with rotation and audit logging
- **medium** -- Secrets in environment variables or K8s Secrets, not hardcoded but without a dedicated secret management system
- **low** -- Secrets in config files that are gitignored, with no formal rotation or access auditing

## Architecture

Look for secrets never committed to version control, accessed through a dedicated store, with rotation and audit capabilities.

### Review Checklist

- No secrets are hardcoded in source code, manifests, or config files checked into version control
- Secrets are sourced from a dedicated store (`pass`, Vault, external-secrets) at deploy time or runtime
- Secret rotation is possible without code changes or redeployment
- Access to secrets is auditable (who accessed what and when)
- Secret references in manifests use `secretKeyRef`, never inline `value`
- CI/CD pipelines do not log or expose secret values in build output

### Anti-patterns

- Secrets committed to git, even in "private" repositories (they persist in history forever)
- Shared secrets across environments (production credentials in staging)
- No rotation -- secrets unchanged since initial setup with no process to rotate them
- Secrets passed as command-line arguments (visible in process listings and shell history)

---
description: Select Star anti-pattern
type: anti-pattern
testable: true
observable: true
graphable: false
---
# Select Star

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `SELECT *` in production queries or raw SQL strings
- ORM loading full objects when only one or two fields are needed
- `Model.objects.all()` without `.values()`, `.only()`, or `.defer()`
- `findAll()` or `find({})` without a projection parameter
- Repository methods returning full entity objects for list/summary endpoints
- No column-level selection in query builders (`knex('table').select()` with no arguments)

### Confidence

- **high** -- `SELECT *` appears in a production query path confirmed by slow query logs or query plans showing full table scans with unnecessary columns
- **medium** -- ORM queryset fetches all fields and the consuming code only accesses 1-2 attributes, or `Model.objects.all()` is used without field restriction
- **low** -- repository method returns full model objects and callers serialize only a subset of fields

## Impact

Unnecessary data transfer over the wire, slower queries, and wasted application memory from materializing unused columns.

### Symptoms

- Query response payloads are significantly larger than what the caller actually uses
- Database I/O is higher than expected for the application's access patterns
- Memory usage spikes when loading large result sets with wide rows
- Network latency between application and database is elevated under load
- Index-only scans are not used because the query requests all columns

### Remediation

- Replace `SELECT *` with explicit column lists in all production queries
- Use `.only()`, `.values()`, or `.defer()` in ORM queries to fetch only needed fields
- Add projections to NoSQL queries (`find({}, {field1: 1, field2: 1})`)
- Create dedicated read models or DTOs for list/summary endpoints that only query required columns
- Add a query review step or linting rule that flags `SELECT *` outside of ad-hoc/debug contexts

---
description: Server Prefetch — fetching data on the server before client rendering
type: pattern
graphable: true
abstraction: [frontend, data]
---
# Server Prefetch

## Recognition

How to identify this pattern in code.

### Signatures

- `loader` functions with `queryClient.prefetchQuery` and `dehydrate` (React Router + TanStack Query)
- `getServerSideProps` returning `{ props }` for per-request server data (Next.js Pages Router)
- `getStaticProps` with optional `revalidate` for ISR (Next.js Pages Router)
- Server Components with direct `await` on data fetches, no client hooks (Next.js App Router)
- `useAsyncData` and `useFetch` composables executing on the server during SSR (Nuxt)
- `load` function in `+page.server.ts` or `+page.ts` (SvelteKit)
- `resolve` guards in route configuration fetching data before component activation (Angular)
- `prefetchQuery`, `ensureQueryData` called outside component lifecycle for cache priming
- `HydrationBoundary` or `DehydratedState` props passing serialized query cache to the client
- `__NEXT_DATA__` or inline `<script>` tags containing serialized server state in HTML

### Confidence

- **high** -- Framework-specific server data function (loader, getServerSideProps, load) with explicit cache dehydration and client hydration boundary
- **medium** -- Data fetched in a server context and passed to client components via props or serialized state, but without formal hydration utilities
- **low** -- API calls made in server middleware or route handlers where the result is injected into the page but without structured cache management

## Architecture

Look for data fetching that runs on the server during the request lifecycle, with results serialized into the response and rehydrated on the client to avoid redundant fetches.

### Review Checklist

- Server-fetched data is serialized in a format the client cache can consume (dehydrated state)
- Hydration boundary is placed so the client does not refetch data that was already loaded on the server
- Error handling covers server fetch failures with appropriate fallback or error page
- Cache keys are consistent between server prefetch and client-side queries
- Sensitive data (tokens, internal IDs) is not leaked through serialized state in the HTML
- Stale-while-revalidate or cache TTL is configured to balance freshness and performance

### Anti-patterns

- Prefetching on the server but also triggering the same fetch on client mount (double fetch)
- Serializing the entire server response into HTML instead of only the data the page needs
- No error boundary around hydration, causing full-page crashes on deserialization failure
- Using server prefetch for user-specific data on statically generated pages (cache poisoning)
- Mismatched cache keys between server and client causing hydration misses

---
description: Server-Sent Events architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [infrastructure, integration]
---
# Server-Sent Events (SSE)

## Recognition

How to identify this pattern in code.

### Signatures

- `Content-Type: text/event-stream` response header
- `EventSource` constructor on the client side
- Lines prefixed with `data:`, `event:`, `id:`, or `retry:` in the response stream
- HTTP streaming response with `Transfer-Encoding: chunked` or `Connection: keep-alive`
- `@SseEmitter` or `SseEmitter` in Spring, `StreamingResponse` in FastAPI/Starlette
- `res.write()` in a long-lived Node HTTP response with `text/event-stream`
- `Last-Event-ID` header for resuming missed events
- `onmessage`, `onopen`, `onerror` event listeners on `EventSource`

### Confidence

- **high** -- `text/event-stream` content type with `data:` prefixed lines and `EventSource` client
- **medium** -- HTTP streaming response with event-like formatting but no explicit `EventSource` usage
- **low** -- Long-lived HTTP response that pushes data without standard SSE framing

## Architecture

Look for correct one-way server push with proper event framing and automatic reconnection.

### Review Checklist

- Response uses `text/event-stream` content type and follows the SSE wire format
- Events include `id:` fields so clients can resume via `Last-Event-ID` after reconnection
- `retry:` field is set to a reasonable reconnection interval
- Server handles client disconnection gracefully (detects closed connection, cleans up resources)
- Named event types (`event:` field) are used to multiplex different message kinds on one stream
- Connection count is bounded -- server tracks and limits concurrent SSE clients

### Anti-patterns

- Missing `id:` fields making resume-after-disconnect impossible
- Buffering the entire response instead of streaming (defeats the purpose of SSE)
- Using SSE for bidirectional communication instead of switching to WebSocket
- No connection cleanup when clients disconnect silently

---
description: Serverless / FaaS architectural pattern
type: pattern
graphable: true
abstraction: [architectural, deployment]
---
# Serverless / FaaS

## Recognition

How to identify this pattern in code.

### Signatures

- Lambda handler functions: `handler(event, context)`, `exports.handler`, `def lambda_handler`
- Cloud Functions entry points: `@functions_framework.http`, `@app.route` with Lambda integration
- Infrastructure-as-code: `serverless.yml`, `template.yaml` (SAM), `cdk.Stack` with Lambda constructs
- Cold start mitigation: provisioned concurrency config, connection pooling outside handler, lazy initialization
- Stateless request handlers with no local filesystem or in-memory state between invocations
- API Gateway + Lambda integration patterns, event source mappings (SQS, S3, DynamoDB Streams)
- Step Functions or Durable Functions for orchestrating multi-step workflows

### Confidence

- **high** -- `serverless.yml` or SAM template with Lambda function definitions and API Gateway triggers
- **medium** -- Stateless handler functions with event/context signatures and cloud provider SDK usage
- **low** -- Small isolated functions invoked by HTTP with no persistent process, but no explicit FaaS framework

## Architecture

Look for stateless, event-driven handlers with external state management and awareness of cold start and execution limits.

### Review Checklist

- Handlers are stateless -- no in-memory state carried between invocations
- Connections to databases and external services are initialized outside the handler (reused across warm invocations)
- Cold start impact is understood and mitigated for latency-sensitive paths
- Function timeout, memory, and concurrency limits are explicitly configured per function
- Idempotency is handled for event-driven triggers (SQS, streams) since at-least-once delivery is the norm
- Observability is in place: structured logging, distributed tracing with X-Ray or equivalent

### Anti-patterns

- Storing state in global variables expecting it to persist reliably across invocations
- Long-running functions approaching the execution timeout limit instead of decomposing into steps
- Ignoring cold start latency for synchronous user-facing endpoints
- Deploying monolithic handlers that bundle unrelated logic into a single function

---
description: Service Discovery architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [infrastructure, integration]
---
# Service Discovery

## Recognition

How to identify this pattern in code.

### Signatures

- Service registry with registration and lookup APIs
- DNS-based discovery (`consul`, `eureka`, CoreDNS, K8s Service + DNS)
- `nslookup`, `dig`, or DNS resolution for service endpoints
- Service mesh with automatic endpoint discovery (Istio, Linkerd)
- Client-side discovery with load balancer (Ribbon, gRPC name resolution)
- Server-side discovery with reverse proxy or API gateway routing
- Health-checked service registration with TTL or heartbeat

### Confidence

- **high** -- Explicit service registry integration (Consul agent, Eureka client) or K8s Service resources with DNS-based resolution
- **medium** -- Environment variables or config pointing to service endpoints with health checking, but no formal registry
- **low** -- Hardcoded hostnames or IP addresses in config files with no dynamic resolution

## Architecture

Look for services registering themselves on startup and consumers resolving endpoints dynamically rather than using static addresses.

### Review Checklist

- Services register on startup and deregister on graceful shutdown
- Health checks are configured so unhealthy instances are removed from the registry
- Consumers resolve endpoints through the registry, not hardcoded addresses
- Stale registrations are cleaned up via TTL or lease expiry
- Discovery mechanism handles network partitions gracefully (cached endpoints, fallback)
- Load balancing strategy is defined (round-robin, least-connections, consistent hashing)

### Anti-patterns

- Hardcoded service addresses that require config changes and redeployment to update
- No health checking -- dead instances remain in the registry and receive traffic
- Registration without deregistration -- registry fills with stale entries over time
- Single point of failure in the discovery infrastructure with no fallback

---
description: Service Manager architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [lifecycle]
---
# Service Manager

## Recognition

How to identify this pattern in code.

### Signatures

- Signal handlers registering for graceful shutdown (`signal.signal(signal.SIGTERM, handler)`)
- Health endpoints exposed at `/healthz` and `/readyz` paths
- `livenessProbe` and `readinessProbe` configuration in Kubernetes pod specs
- `ServiceManager` class coordinating startup, readiness, and shutdown phases
- `orchestrator` imports or orchestration-layer integration for lifecycle reporting
- Process lifecycle management with explicit state transitions (starting, ready, draining, stopped)
- Graceful shutdown logic draining in-flight requests and flushing buffers before exit
- `terminationGracePeriodSeconds` configuration in pod specs

### Confidence

- **high** -- `ServiceManager` class with SIGTERM signal handlers, `/healthz`+`/readyz` endpoints, and `livenessProbe`/`readinessProbe` in K8s specs
- **medium** -- Signal handlers with graceful shutdown drain logic and health endpoints, but without a dedicated manager class
- **low** -- Health check endpoints or liveness probes present without explicit shutdown handling or lifecycle state management

## Architecture

Look for clean lifecycle phases: startup completes before serving, shutdown drains before closing.

### Review Checklist

- Startup validates config and dependencies before marking ready
- Health checks run periodically and report to orchestrator (liveness + readiness)
- Shutdown handles SIGTERM gracefully — drains in-flight requests, flushes buffers
- Startup failures produce clear error messages and exit with non-zero code
- No traffic served until readiness is explicitly signaled

### Anti-patterns

- Serving traffic before dependencies are connected (premature readiness)
- Shutdown kills in-flight requests without draining (data loss)
- Health check always returns healthy regardless of actual state
- No distinction between liveness and readiness probes

---
description: Service Mesh architectural pattern
type: pattern
observable: true
distributed: true
graphable: true
abstraction: [infrastructure, integration]
---
# Service Mesh

## Recognition

How to identify this pattern in code.

### Signatures

- Sidecar proxy containers: Envoy, Linkerd-proxy, Consul Connect proxy
- Istio CRDs: `VirtualService`, `DestinationRule`, `PeerAuthentication`, `AuthorizationPolicy`
- Linkerd CRDs: `ServiceProfile`, `TrafficSplit`, `Server`, `ServerAuthorization`
- Automatic sidecar injection annotations (`sidecar.istio.io/inject: "true"`, `linkerd.io/inject: enabled`)
- mTLS configuration between services (mesh-wide or per-service)
- Traffic policy definitions (retries, timeouts, circuit breaking at the mesh level)

### Confidence

- **high** -- sidecar proxies injected into pods, mesh CRDs managing traffic policies, mTLS enforced between services
- **medium** -- mesh control plane installed but sidecar injection is selective or traffic policies are minimal
- **low** -- Envoy or similar proxy present but configured manually without a mesh control plane

## Architecture

Look for transparent network-level service communication management via sidecar proxies controlled by a central control plane.

### Review Checklist

- mTLS is enforced mesh-wide (not just optional or permissive mode in production)
- Traffic policies (retries, timeouts) are set at the mesh level to avoid conflicting with application-level settings
- Sidecar resource limits are configured to prevent proxies from starving application containers
- Observability is leveraged (mesh provides metrics, traces, and access logs without application changes)
- Namespace-level policies control which services can communicate (zero-trust networking)
- Mesh upgrades have a tested rollout plan (control plane first, then data plane sidecars)

### Anti-patterns

- Leaving mTLS in permissive mode in production (allows plaintext bypass)
- Duplicate retry/timeout logic in both the mesh and the application (compounding retries)
- No resource limits on sidecar proxies (Envoy consuming excessive CPU/memory)
- Adding a mesh to a system with only a few services (operational overhead exceeds benefit)

---
description: Session-Based Authentication architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [security]
---
# Session-Based Authentication

## Recognition

How to identify this pattern in code.

### Signatures

- Server-side session store (Redis, database table, in-memory map)
- `session_id` cookie set on login response
- `Set-Cookie` header with `HttpOnly`, `Secure`, and `SameSite` attributes
- Session middleware (`express-session`, `django.contrib.sessions`, `gorilla/sessions`)
- `req.session` or `request.session` access in request handlers
- Server-side session lookup on every authenticated request
- CSRF tokens paired with sessions (`csrf_token`, `X-CSRF-Token` header)
- Session expiry and idle timeout configuration
- Libraries: `express-session`, `connect-redis`, `django.contrib.sessions`, `flask-session`, `gorilla/sessions`

### Confidence

- **high** -- Session store configured (Redis/DB), `Set-Cookie` with `HttpOnly`/`Secure`/`SameSite`, session middleware registered, and CSRF protection enabled
- **medium** -- `req.session` or `request.session` used in handlers with cookie-based auth, but session store backend unclear
- **low** -- Cookie-based authentication present but no explicit session store or middleware visible (could be signed cookies without server-side state)

## Architecture

Look for server-side session state management with secure cookie transport and CSRF protection.

### Review Checklist

- Session IDs are cryptographically random and sufficiently long (128+ bits of entropy)
- Session store has TTL/expiry configured (not unbounded growth)
- Cookies set `HttpOnly`, `Secure`, and `SameSite=Strict` or `SameSite=Lax`
- CSRF protection is enabled for all state-changing requests
- Session is regenerated on login to prevent session fixation
- Logout destroys the server-side session, not just the cookie

### Anti-patterns

- Storing sensitive data (passwords, tokens) directly in the session object
- Using in-memory session store in production (lost on restart, no horizontal scaling)
- Missing `HttpOnly`/`Secure` flags on session cookies (vulnerable to XSS and MITM)
- No session regeneration on privilege change (session fixation vulnerability)

---
description: Sharding architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [data, infrastructure]
---
# Sharding

## Recognition

How to identify this pattern in code.

### Signatures

- Shard key selection and shard ID derivation logic
- Consistent hashing or hash-ring implementations
- Shard router/resolver that maps keys to database connections or partitions
- Partition-aware queries with shard hints or routing decorators
- `shard_key`, `partition_key`, or `tenant_id` fields on models or tables
- Multiple database connection configurations (shard_0, shard_1, etc.)
- Rebalancing or migration tooling for shard splits

### Confidence

- **high** -- explicit shard router with consistent hashing and per-shard connection pools
- **medium** -- database partitioning configured at the schema level (PostgreSQL partitions, Vitess)
- **low** -- multiple databases used per tenant but without formal shard routing logic

## Architecture

Look for data distributed across multiple storage nodes with a deterministic routing layer that maps keys to shards.

### Review Checklist

- Shard key is immutable and evenly distributes data (avoids hot shards)
- Cross-shard queries are identified and handled explicitly (scatter-gather or denormalization)
- Shard routing is centralized, not duplicated across services
- Rebalancing strategy exists for adding or removing shards without downtime
- Connection pool management scales per-shard, not globally

### Anti-patterns

- Choosing a shard key that causes skewed distribution (all data on one shard)
- Cross-shard joins treated as normal queries (hidden N+1 across shards)
- No plan for resharding when shard count needs to change
- Application logic assuming data locality across shard boundaries

---
description: Shotgun Surgery anti-pattern
type: anti-pattern
testable: true
graphable: false
---
# Shotgun Surgery

## Recognition

How to identify this anti-pattern in code.

### Signatures

- One logical change requires editing 10+ files across different modules or packages
- Feature implementation spread across many packages with no central module
- Cross-cutting concerns (logging, auth, validation) duplicated in every module instead of centralized
- A single bug fix touching files in 5+ directories
- Git commits that routinely modify files across unrelated packages for a single feature
- Configuration values repeated in multiple files rather than sourced from one location
- The same conditional logic (`if feature_x:`) scattered across many modules

### Confidence

- **high** -- a single feature branch consistently modifies 10+ files across 5+ directories, and this pattern repeats across multiple features
- **medium** -- cross-cutting concerns like authorization checks or logging formats are duplicated in many modules
- **low** -- a recent feature required changes in more directories than expected, but it may be a one-off

## Impact

Changes are expensive and error-prone because a single logical modification requires coordinated edits across many scattered locations.

### Symptoms

- Simple feature requests take disproportionately long to implement
- Bug fixes frequently miss one of the many locations that need updating
- Code reviews are large and span many unrelated files
- Developers fear making changes because they cannot be sure they found every location
- Regression rate is high despite thorough-looking changes

### Remediation

- Identify the scattered concern and consolidate it into a single module or class
- Use decorators, middleware, or aspect-oriented techniques for cross-cutting concerns
- Apply the DRY principle by extracting shared logic into one authoritative location
- Introduce a facade or service layer that centralizes the scattered operations
- Set up architectural linting rules to prevent the concern from spreading again

---
description: Side Effect Hook — lifecycle-bound execution of effects in component frameworks
type: pattern
graphable: false
abstraction: [frontend, lifecycle]
---
# Side Effect Hook

## Recognition

How to identify this pattern in code.

### Signatures

- `useEffect` and `useLayoutEffect` with dependency arrays and cleanup returns (React)
- `onMounted`, `onUnmounted`, `watch`, `watchEffect` lifecycle and reactive watchers (Vue)
- `ngOnInit`, `ngOnDestroy`, `ngOnChanges` lifecycle hooks (Angular)
- `onMount`, `onDestroy`, `afterUpdate` lifecycle functions (Svelte)
- Cleanup functions returned from effect callbacks (unsubscribe, clearInterval, abort controller)
- Dependency arrays controlling when effects re-run: `[dep1, dep2]`, empty `[]` for mount-only
- `useInsertionEffect` for CSS-in-JS library injection before DOM mutations (React)
- Subscription setup and teardown patterns: `subscribe()`/`unsubscribe()`, `addEventListener`/`removeEventListener`
- `AbortController` created in effect and aborted in cleanup for fetch cancellation

### Confidence

- **high** -- Framework effect hook or lifecycle method with explicit dependency tracking, cleanup function, and clear separation from render logic
- **medium** -- Lifecycle method that performs side effects (API calls, subscriptions) but lacks proper cleanup or dependency management
- **low** -- Imperative code inside render or template that triggers side effects without lifecycle awareness

## Architecture

Look for side effects that are bound to component lifecycle, execute at the right time relative to rendering, and clean up properly on unmount or dependency change.

### Review Checklist

- Every subscription, timer, or listener set up in an effect has a corresponding cleanup
- Dependency arrays are complete and accurate -- no missing dependencies causing stale closures
- Effects that should run once (on mount) use an empty dependency array, not missing dependencies
- Data fetching effects handle race conditions (stale closure, component unmounted before response)
- Heavy effects are debounced or throttled to avoid performance issues on rapid re-renders
- Effects are not used for state derivation that could be computed synchronously during render

### Anti-patterns

- Missing cleanup functions causing memory leaks (orphaned subscriptions, dangling timers)
- Incorrect or missing dependency arrays causing effects to run too often or with stale data
- Using effects for derived state that should be computed with useMemo, computed properties, or selectors
- Fetch-in-effect without cancellation, causing state updates on unmounted components
- Chained effects where one effect sets state that triggers another effect (effect cascade)

---
description: Sidecar mesh structure — services with co-located helper processes for cross-cutting concerns
type: structure-shape
abstraction: [infrastructure, deployment]
---
# Sidecar Mesh

## Recognition

### Signatures

- Istio, Linkerd, or Consul Connect service mesh
- Envoy proxy sidecars injected into k8s pods
- Pod specs with multiple containers: main app + sidecar(s)
- Init containers for configuration or certificate injection
- mTLS between services handled by sidecar, not application
- Distributed tracing headers injected by sidecar proxy
- Traffic management (retries, timeouts, circuit breaking) at mesh level
- `istio-proxy` or `envoy` container in pod definitions
- Service mesh configuration: VirtualService, DestinationRule, AuthorizationPolicy

### Confidence

- **high** — service mesh (Istio/Linkerd) with sidecar injection, mTLS, and traffic management policies
- **medium** — sidecar containers for logging or monitoring but no service mesh control plane
- **low** — multi-container pods but sidecars are for unrelated purposes (e.g., log shipping only)

---
description: Sidecar architectural pattern
type: pattern
observable: true
distributed: true
graphable: true
abstraction: [lifecycle, infrastructure, deployment]
---
# Sidecar

## Recognition

How to identify this pattern in code.

### Signatures

- Multi-container pod specs with two or more containers in a single pod definition
- `sidecar.istio.io/inject` annotation on pods or namespaces
- `linkerd.io/inject: enabled` annotation for Linkerd proxy injection
- `emptyDir` shared volumes mounted by both sidecar and main containers
- Container names like `istio-proxy`, `linkerd-proxy`, `envoy`, or `fluentd`
- `initContainers` running setup tasks before the main and sidecar containers start
- Ambassador containers handling outbound proxy or authentication concerns
- Sidecar resource limits defined separately from the main container

### Confidence

- **high** -- Multi-container pod specs with `istio-proxy`/`linkerd-proxy` containers, or `sidecar.istio.io/inject`/`linkerd.io/inject` annotations
- **medium** -- `emptyDir` shared volumes between containers in the same pod with `initContainers`, but without service mesh annotations
- **low** -- Multi-container pod specs where container roles are unclear or all containers appear to run business logic

## Architecture

Look for the sidecar handling only cross-cutting concerns with no business logic.

### Review Checklist

- Sidecar handles a single cross-cutting concern (logging, proxy, auth — not all three)
- Communication with main container uses localhost/shared volume — no network hops
- Sidecar lifecycle is tied to the main container (starts before, stops after)
- Main container functions (possibly degraded) if the sidecar is temporarily unavailable

### Anti-patterns

- Business logic in the sidecar — it should be infrastructure only
- Sidecar and main container with mismatched lifecycle (sidecar outlives the app)
- Too many sidecars per pod — resource overhead exceeds the benefit
- Tight version coupling between sidecar and main container deployments

---
description: Singleton architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Singleton

## Recognition

How to identify this pattern in code.

### Signatures

- Class variable `_instance`, `__instance`, or `instance`
- Static method `getInstance()`, `get_instance()`, or `shared()`
- Python: `__new__` override checking for existing instance, `@singleton` decorator, module-level instance
- Java/TS: `private constructor` with `static getInstance()`
- Go: `sync.Once` with package-level `var instance`
- Rust: `lazy_static!` or `once_cell::sync::Lazy`

### Confidence

- **high** -- private constructor plus static `getInstance()` with lazy initialization and instance caching
- **medium** -- module-level instance variable with no public constructor, or `__new__` override
- **low** -- global variable used as a shared resource across the codebase

## Architecture

Look for thread safety and verify the singleton is genuinely needed over dependency injection.

### Review Checklist

- Thread-safe initialization (double-checked locking, `sync.Once`, module import)
- No mutable global state that makes testing impossible
- Clear justification for singleton over injected dependency
- Singleton lifecycle is explicit (creation, optional teardown for tests)
- Subclassing is either properly supported or explicitly prevented

### Anti-patterns

- Singleton used as a global grab bag (config, logger, cache, and DB all in one)
- No way to reset or replace the instance in tests
- Lazy initialization with race conditions in multi-threaded contexts
- Hidden dependencies -- classes reach for the singleton instead of receiving it via injection

---
description: Snapshot Testing architectural pattern
type: pattern
testable: true
graphable: false
abstraction: [testing]
---
# Snapshot Testing

## Recognition

How to identify this pattern in code.

### Signatures

- `toMatchSnapshot()`, `toMatchInlineSnapshot()` in Jest tests
- `__snapshots__` directories containing `.snap` files
- `syrupy` assertions (`assert snapshot == result`) in Python tests
- `approve_tests` or `ApprovalTests` library usage with `.approved.txt` files
- Snapshot update commands in CI or package scripts (`--update-snapshot`, `-u` flag)
- `.snap` or `.snapshot` file extensions tracked in version control

### Confidence

- **high** — Snapshot files committed to version control with corresponding test assertions, and a CI step that fails on snapshot drift
- **medium** — Snapshot assertions present but snapshot files are in `.gitignore` or frequently bulk-updated without review
- **low** — String comparison tests against large expected outputs that function like manual snapshots

## Architecture

Look for snapshot assertions that capture complex output and detect unintended changes through diff comparison.

### Review Checklist

- Snapshots capture meaningful output (serialized components, API responses, CLI output) not implementation internals
- Snapshot updates are reviewed in PRs -- bulk updates without explanation are flagged
- Volatile data (timestamps, random IDs, absolute paths) is masked or normalized before snapshotting
- Inline snapshots are used for small, focused assertions; file-based snapshots for larger outputs
- Obsolete snapshots are cleaned up when corresponding tests are removed

### Anti-patterns

- Blindly running `--update-snapshot` and committing without reviewing what changed
- Snapshotting entire DOM trees or large JSON blobs where small unrelated changes cause noisy diffs
- No normalization of non-deterministic values, causing snapshots to break on every run
- Using snapshots as a substitute for targeted assertions when specific field checks would be clearer

---
description: Snowflake Server anti-pattern
type: anti-pattern
graphable: false
---
# Snowflake Server

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Hand-configured servers with no Infrastructure as Code (IaC) backing them
- `ssh` commands in deploy scripts: `ssh prod-server 'sudo systemctl restart app'`
- Undocumented manual steps required to set up or update a server
- Works-on-my-machine issues that cannot be reproduced elsewhere
- Config files edited directly on the server via `vim`, `nano`, or `sed` in ad-hoc scripts
- Server setup instructions that include "ask Dave, he knows how this one is configured"
- No Terraform, Ansible, Puppet, Chef, or equivalent in the repository

### Confidence

- **high** -- deploy process involves SSH into a server and running manual commands, with no IaC in the repo
- **medium** -- partial IaC exists but some servers have manual tweaks applied outside of it
- **low** -- IaC exists but the actual server state has drifted and no one has reconciled it

## Impact

Unreproducible environments that cannot be rebuilt, audited, or scaled, turning every server into a unique artifact that the team is afraid to touch.

### Symptoms

- Disaster recovery is impossible or takes days because nobody knows the exact server configuration
- Scaling requires manually setting up each new server by hand
- Security patches are applied inconsistently across servers
- Configuration drift: nominally identical servers behave differently
- Knowledge of how to configure the server lives in one person's head

### Remediation

- Adopt Infrastructure as Code: define all server configuration in Terraform, Ansible, or equivalent
- Treat servers as cattle, not pets: any server should be replaceable by re-running the IaC
- Use immutable infrastructure: build machine images (AMI, Docker) and deploy new instances rather than mutating existing ones
- Store all configuration in version control and apply it through CI/CD pipelines
- Implement configuration drift detection that alerts when a server diverges from its declared state

See also: infrastructure-as-code, immutable-infra patterns

---
description: Social graph pattern for user relationships and activity feeds
type: pattern
category: domain-model
abstraction: [data, social]
---
# Social Graph

## Recognition

How to identify this pattern in code.

### Signatures

- `follow`, `Follow`, `follower`, `following` models or table names
- `friend`, `Friend`, `connection`, `Connection` relationship models
- `feed`, `Feed`, `activity_stream`, `ActivityStream` for content distribution
- `timeline`, `Timeline` aggregation of followed users' activities
- `mutual` friends/followers computation queries
- Python: `django-activity-stream`, `stream-python`, `Follow` model with `follower` and `following` FK
- JS/TS: `getstream`, `@stream-io/node`, feed and follow API calls
- Go: `follow` table with `follower_id` and `following_id`, fan-out service
- Rust: social relationship structs, feed generation pipeline
- Java: `@ManyToMany` friend relationships, activity feed service

### Confidence

- **high** -- Follow/Connection model with fan-out feed generation, activity stream aggregation, and timeline queries across the social graph
- **medium** -- Follow table with follower/following relationships and basic feed queries joining followed users' posts
- **low** -- Simple user list or contact book without relationship-driven content distribution

## Architecture

### When to use
- Social platforms where users follow or connect with others and see their activity
- Community features in products (follow authors, subscribe to topics)
- Any system requiring relationship-driven content distribution and discovery

### Anti-patterns
- Computing feeds on read by joining all followed users' posts, which becomes O(n*m) and unscalable
- Symmetric friend relationships stored as a single row, making directional queries ambiguous
- No fan-out strategy, forcing timeline assembly at query time for every request

### Complements
- [property-graph](/concepts/property-graph) — social relationships form a natural property graph
- [pub-sub](/concepts/pub-sub) — fan-out on write uses pub/sub to distribute activities
- [cache-aside](/concepts/cache-aside) — hot timelines benefit from cache-aside for feed caching

## Impact

Social graph operations (fan-out, timeline assembly, mutual friend computation) are among the most scale-sensitive patterns in application development. Feed generation strategy (fan-out on write vs. fan-out on read) is a fundamental architectural decision that affects latency, storage, and infrastructure costs.

---
description: Soft Delete architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [data]
---
# Soft Delete

## Recognition

How to identify this pattern in code.

### Signatures

- `deleted_at` timestamp column that is NULL for active records and set on deletion
- `is_deleted` boolean flag on database tables or document models
- Default query scopes that add `WHERE deleted_at IS NULL` to all reads
- `paranoid: true` (Sequelize), `acts_as_paranoid` (Rails), `SoftDeletes` trait (Laravel)
- `restore()` or `undelete()` method alongside the soft delete operation
- Unique index constraints that include the `deleted_at` column to allow re-creation of deleted records
- Scheduled hard-delete or purge jobs that permanently remove records past a retention period

### Confidence

- **high** -- `deleted_at` column with default query scope excluding deleted records and a `restore()` method
- **medium** -- `is_deleted` boolean flag referenced in query conditions across the codebase
- **low** -- Records marked with a status field (`status = 'archived'`) that are filtered from default queries

## Architecture

Look for consistent application of soft delete scopes across all queries and clear lifecycle for eventual hard deletion.

### Review Checklist

- Default query scopes exclude soft-deleted records so developers cannot accidentally return them
- A mechanism exists to query deleted records explicitly when needed (admin views, audit, restore)
- Unique constraints account for soft-deleted records (composite index with `deleted_at` or partial index)
- Foreign key relationships handle soft-deleted parents correctly (cascading soft delete or preventing it)
- A retention policy and purge job exist to hard-delete records past the retention period
- Soft delete is applied consistently across related entities (deleting a parent soft-deletes children)

### Anti-patterns

- Queries throughout the codebase manually adding `WHERE deleted_at IS NULL` instead of using a default scope
- No purge strategy, causing tables to grow unbounded with deleted records degrading query performance
- Unique constraints that break when re-creating a record with the same natural key as a soft-deleted one
- Soft-deleting a parent while leaving orphaned child records in an active state

---
description: Spaghetti Code anti-pattern
type: anti-pattern
graphable: false
---
# Spaghetti Code

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Conditionals nested 5+ levels deep (if/else/if/else/try/if)
- Functions with 10+ parameters
- Functions exceeding 500 lines
- Goto-like flow: deeply nested breaks, continues, early returns scattered unpredictably, exception-driven control flow
- No clear function boundaries -- logic inlined rather than extracted into named functions
- Variables reused for multiple unrelated purposes within the same scope

### Confidence

- **high** -- functions exceed 500 lines with 5+ nesting levels and 10+ parameters
- **medium** -- functions exceed 200 lines with 3+ nesting levels and interleaved concerns
- **low** -- inconsistent indentation levels and scattered return statements suggesting tangled flow

## Impact

Untraceable control flow makes the code impossible to debug, test, or safely modify.

### Symptoms

- Developers cannot follow execution paths without a debugger
- Adding a simple feature requires reading and understanding hundreds of lines of context
- Tests must replicate complex state setups to reach specific branches
- Cyclomatic complexity metrics are extremely high (50+)
- Code reviews take disproportionately long for small changes

### Remediation

- Extract deeply nested blocks into well-named functions with clear inputs and outputs
- Replace nested conditionals with guard clauses (early returns at the top)
- Break long parameter lists into parameter objects or configuration structs
- Apply "compose small functions" principle: each function does one thing at one level of abstraction
- Introduce intermediate variables with descriptive names to document intent at each step

---
description: Spatial Partitioning architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [data, realtime]
---
# Spatial Partitioning

## Recognition

How to identify this pattern in code.

### Signatures

- Classes named `QuadTree`, `Octree`, `SpatialHash`, `RTree`, `BVH`, `Grid`
- `insert()`, `query()`, `remove()` methods taking spatial coordinates or bounding boxes
- Broad-phase collision detection separating cheap spatial queries from expensive narrow-phase checks
- Bounding volume hierarchies (`AABB`, `BoundingBox`, `BoundingSphere`)
- Neighbor queries: `query_radius()`, `query_rect()`, `nearest()`
- Recursive subdivision of space into cells or nodes with max capacity
- Libraries: libspatialindex, nanoflann, rbush (JS), scipy.spatial, boost.geometry

### Confidence

- **high** — `QuadTree`/`Octree`/`SpatialHash` class with insert and spatial query methods
- **medium** — grid-based bucketing of objects by position with neighbor lookups
- **low** — spatial coordinates used as hash keys or array indices for proximity checks

## Architecture

Look for a spatial data structure that accelerates range or proximity queries over positioned objects.

### Review Checklist

- Partition structure matches the dimensionality of the problem (2D: quadtree/grid, 3D: octree/BVH)
- Tree depth or cell size is bounded to prevent degenerate performance
- Objects that span multiple cells are handled correctly (overlap, insertion into multiple cells)
- Structure is rebuilt or updated incrementally as objects move
- Query interface returns candidates, not final results (broad-phase, not narrow-phase)
- Memory allocation strategy avoids per-frame heap churn (object pools, pre-allocated nodes)

### Anti-patterns

- Rebuilding the entire spatial structure every frame when incremental updates suffice
- Using a single flat list with O(n^2) pairwise distance checks instead of spatial queries
- Tree with no depth limit, causing stack overflow on clustered data
- Mixing broad-phase and narrow-phase logic in the same structure

---
description: Spatial data model for geographic and geometric computations
type: pattern
category: domain-model
abstraction: [data, geospatial]
---
# Spatial

## Recognition

How to identify this pattern in code.

### Signatures

- `geometry`, `Point`, `Polygon`, `LineString` type definitions or column types
- `latitude`, `longitude`, `lat`, `lng`, `coordinates` fields on models
- GeoJSON structures: `type: "Feature"`, `geometry: { type: "Point", coordinates: [...] }`
- PostGIS functions: `ST_Distance`, `ST_Contains`, `ST_Within`, `ST_Intersects`, `ST_Buffer`
- `spatial_index`, `GIST` index, `rtree` index creation on geometry columns
- `geofence`, `bounding_box`, `bbox`, `envelope` boundary computations
- Python: `shapely`, `geopandas`, `pyproj`, `geopy` library imports
- JS/TS: `turf.js`, `mapbox-gl`, `leaflet`, `@types/geojson` imports
- Go: `orb`, `go-geom`, `tegola`, PostGIS via `pgx` with geometry types
- Rust: `geo`, `geozero`, `postgis` crate, `rtree` spatial index

### Confidence

- **high** -- PostGIS or spatial database with ST_ functions, spatial index, and GeoJSON serialization across API boundaries
- **medium** -- Shapely or turf.js geometry operations with coordinate reference system awareness
- **low** -- Raw latitude/longitude floats stored without geometry types or spatial query capability

## Architecture

### When to use
- Location-based services requiring proximity search, geofencing, or route computation
- Mapping and GIS applications with polygon operations and spatial joins
- Any domain where distance, containment, or intersection queries are core access patterns

### Anti-patterns
- Storing coordinates as separate float columns without a proper geometry type, losing spatial query capability
- Computing distances in application code instead of using database-level spatial functions with spatial indices
- Ignoring coordinate reference systems (CRS), leading to incorrect distance calculations across hemispheres

### Complements
- [search-index](/concepts/search-index) — spatial queries often combine with full-text search for location-aware results
- [cache-aside](/concepts/cache-aside) — geofence lookups benefit from caching for hot regions
- [pagination](/concepts/pagination) — spatial queries return bounded result sets requiring pagination

## Impact

Spatial data requires specialized indexing (R-tree, GiST) that differs fundamentally from B-tree indices. Query performance depends heavily on spatial index health, and incorrect CRS handling produces silently wrong results that are difficult to catch without geospatial-aware testing.

---
description: Specification Pattern architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Specification Pattern

## Recognition

How to identify this pattern in code.

### Signatures

- `is_satisfied_by()` or `isSatisfiedBy()` methods on business rule objects
- `and_spec()`, `or_spec()`, `not_spec()` combinators for composing specifications
- Classes named `*Specification`, `*Spec`, `*Rule`, `*Criteria`
- Chainable query filters that compose boolean predicates: `.where()`, `.and()`, `.or()`
- Predicate objects passed to repository or collection filtering methods
- Specification interface with a single `is_satisfied_by(candidate)` method

### Confidence

- **high** — Dedicated specification classes with `is_satisfied_by()`, composed via `and`/`or`/`not` combinators, used for domain validation or query building
- **medium** — Predicate functions or lambda chains used for filtering, but without formal specification classes or combinators
- **low** — Boolean methods on domain objects (`is_active()`, `is_eligible()`) that encode business rules but are not composable

## Architecture

Look for reusable, composable business rule objects that can be combined and applied to validation, filtering, and querying.

### Review Checklist

- Each specification encapsulates a single business rule and is named after that rule in domain language
- Specifications compose via `and`, `or`, `not` without the caller building ad-hoc boolean expressions
- The same specification works for both in-memory filtering and query generation (dual-purpose specs)
- Specifications are unit tested independently before being composed
- Complex business rules are expressed as named compositions, not deeply nested anonymous predicates
- Specifications accept the candidate as a parameter and have no hidden dependencies

### Anti-patterns

- Specifications that access databases, APIs, or other services inside `is_satisfied_by()` (side effects in predicates)
- Monolithic specification classes that encode multiple unrelated business rules
- Composing specifications but never testing the individual components in isolation
- Using specifications for trivial checks where a simple boolean expression would be clearer

---
description: SQL Injection anti-pattern
type: anti-pattern
testable: true
graphable: false
---
# SQL Injection

## Recognition

How to identify this anti-pattern in code.

### Signatures

- String concatenation in SQL queries (`f"SELECT * FROM users WHERE id = {id}"`)
- `cursor.execute("... %s" % var)` using Python string formatting instead of parameterized queries
- No parameterized queries (`?` or `$1` placeholders absent from SQL strings)
- `raw()` or `extra()` with user input in Django ORM
- `String.format()` or `+` concatenation building SQL in Java
- `execute("SELECT ... WHERE name = '" + name + "'")`
- `$"SELECT ... WHERE id = {Request.Query["id"]}"` in C#
- Stored procedures built with `EXEC('SELECT ... ' + @param)`

### Confidence

- **high** -- f-string or string concatenation directly inside `cursor.execute()`, `db.query()`, or equivalent with user-controlled input
- **medium** -- SQL strings built with variable interpolation but input source is unclear
- **low** -- raw SQL used anywhere without visible parameterization, even if input may be trusted

## Impact

Database compromise through attacker-controlled query manipulation, enabling data exfiltration, modification, or deletion.

### Symptoms

- Unexpected query results or data leaks reported by users
- Database audit logs show malformed or suspicious queries
- Application crashes on inputs containing single quotes or SQL keywords
- Web application firewall (WAF) alerts on SQL keywords in request parameters
- Data integrity violations with no corresponding application-level writes

### Remediation

- Use parameterized queries exclusively (`cursor.execute("SELECT * FROM users WHERE id = %s", (id,))`)
- Use ORM query builders instead of raw SQL wherever possible
- Validate and sanitize all user input at the boundary (allowlist, not denylist)
- Run static analysis tools (Bandit, Semgrep) with SQL injection rules enabled
- Apply principle of least privilege to database accounts used by the application

---
description: State Machine architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [design, lifecycle]
---
# State Machine

## Recognition

How to identify this pattern in code.

### Signatures

- Enum or constants defining states: `State`, `Status`, `Phase`
- Transition table/map: dict or map from `(state, event)` to `next_state`
- Lifecycle hooks: `on_enter`, `on_exit`, `before_transition`, `after_transition`
- State classes with `handle()` or `process()` methods
- Python: `transitions` library, `statemachine` library, enum-based state tracking
- JS/TS: XState (`createMachine`, `interpret`), state pattern with class-per-state
- Go: state as `int`/`string` const with transition function, `looplab/fsm`
- Rust: typestate pattern (different types per state), enum-based FSM

### Confidence

- **high** -- explicit transition table mapping `(state, event)` pairs to next states, with guard conditions
- **medium** -- enum state variable with switch/match on transitions and entry/exit hooks
- **low** -- status field updated in multiple places with ad-hoc if/else transitions

## Architecture

Look for a complete and well-defined transition table with no implicit state changes.

### Review Checklist

- All valid transitions are explicitly defined (no implicit state changes via direct assignment)
- Invalid transitions are rejected with clear errors, not silently ignored
- Entry/exit actions are tied to transitions, not scattered through business logic
- State is persisted correctly if the machine must survive restarts
- Guard conditions on transitions are pure (no side effects in guards)
- Terminal states are defined and reachable

### Anti-patterns

- State modified by direct assignment instead of through the transition mechanism
- Missing transitions causing the machine to get stuck in unexpected states
- Business logic embedded in transition guards (guards should only evaluate conditions)
- No protection against concurrent transitions (race between two events)

---
description: Strangler Fig architectural pattern
type: pattern
testable: true
distributed: true
graphable: true
abstraction: [lifecycle, architectural]
---
# Strangler Fig

## Recognition

How to identify this pattern in code.

### Signatures

- Routing layer splitting traffic between old and new systems: reverse proxy rules, feature flags, path-based routing
- Proxy or facade in front of legacy: `LegacyProxy`, `MigrationRouter`, Nginx/Envoy route splitting
- Feature-by-feature migration: new service handles some endpoints while legacy handles the rest
- Dual-write during transition: writes to both old and new data stores, reconciliation logic
- Gradual traffic shift: percentage-based routing, canary weights between legacy and replacement
- Anti-corruption layer translating between old and new data models
- Migration toggle: feature flags controlling which system handles each request

### Confidence

- **high** -- routing layer actively splits traffic between legacy and replacement systems with feature-level granularity
- **medium** -- new service exists alongside legacy with some endpoints migrated but no automated traffic shifting
- **low** -- legacy system has a proxy in front of it but no replacement services are receiving traffic yet

## Architecture

Look for a routing layer that incrementally redirects functionality from the legacy system to the replacement, feature by feature.

### Review Checklist

- A routing layer (proxy, gateway, or feature flag) controls which system handles each request
- Each migrated feature can be independently toggled back to legacy if issues arise
- Data consistency is maintained during dual-write periods with reconciliation or event replay
- The legacy system is not modified to accommodate the migration -- the strangler wraps it
- Migration progress is measurable: what percentage of traffic or features have been migrated
- There is a defined end state where the legacy system is fully decommissioned

### Anti-patterns

- Big-bang cutover disguised as strangler fig -- migrating everything at once defeats the purpose
- Dual-write without reconciliation -- data diverges silently between old and new stores
- No rollback path -- migrated features cannot fall back to legacy when problems arise
- Strangler proxy becoming permanent infrastructure with no plan to remove it after migration completes

---
description: Strategy architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Strategy

## Recognition

How to identify this pattern in code.

### Signatures

- Interface/protocol with a single method implemented by multiple concrete classes
- Strategy selection via configuration, environment variable, or runtime parameter
- Classes ending in `Strategy`, `Policy`, `Algorithm`, `Handler`
- Python: protocol/ABC with multiple implementations, function passed as strategy (callable)
- Java/TS: interface with `execute()`/`apply()`/`process()` method and multiple implementations
- Go: function type or interface with multiple implementations assigned at init

### Confidence

- **high** -- interface with one core method, multiple implementations, and runtime selection logic
- **medium** -- config-driven selection between interchangeable implementations of the same operation
- **low** -- if/else or switch choosing between inline algorithm variants

## Architecture

Look for clean separation between strategy selection and strategy execution.

### Review Checklist

- All strategies implement the same interface with identical input/output contracts
- Strategy selection is externalized (config, factory, or parameter), not hardcoded
- Context class delegates to the strategy without knowing which concrete strategy is active
- Adding a new strategy does not require modifying existing strategies or the context
- Strategies are stateless or their state is scoped to a single execution

### Anti-patterns

- Strategy interface with methods only some implementations use (interface segregation violation)
- Context class containing fallback logic that bypasses the strategy
- Strategies that depend on each other or share mutable state
- Using strategy pattern when a simple function parameter would suffice (over-engineering)

---
description: Stream To Store architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [data, integration]
---
# Stream-to-Store

## Recognition

How to identify this pattern in code.

### Signatures

- Kafka consumer imports (`kafka.KafkaConsumer`, `confluent_kafka.Consumer`)
- `consumer.poll()` / `consumer.commit()` calls managing offset lifecycle
- Buffered writes accumulating records before flushing to a store
- `flush()` callbacks triggered by buffer size or time thresholds
- `stoik` imports for stream processing integration
- Consumer group configuration (`group.id`, `auto.offset.reset`, `enable.auto.commit=false`)
- Offset management logic committing only after successful store writes
- Flink sink connectors writing stream data to external stores (`SinkFunction`, `RichSinkFunction`)

### Confidence

- **high** -- Kafka consumer with `poll()`/`commit()` and explicit offset management after buffered `flush()` to a store, or Flink sink connectors
- **medium** -- Consumer group configs with `enable.auto.commit=false` and buffered writes, but without explicit flush callbacks
- **low** -- Stream consumer reading from a broker without clear buffer-then-flush mechanics or offset commit ordering

## Architecture

Look for correct offset management — commits only after successful flush.

### Review Checklist

- Offsets are committed after the store write succeeds, not before
- Buffer has both size and time-based flush triggers
- Flush failures trigger retry with backoff before giving up
- Consumer group rebalancing is handled without data loss or duplication
- Store writes are idempotent (safe to replay on reprocessing)

### Anti-patterns

- Auto-commit enabled — offsets advance regardless of flush success
- Unbounded buffer with no size limit (memory exhaustion on slow stores)
- No dead-letter handling for permanently unprocessable messages

---
description: Streaming flow — continuous data flow with backpressure and windowing
type: flow-shape
abstraction: [data, messaging, realtime]
---
# Streaming

## Recognition

### Signatures

- Kafka consumer with continuous poll loop (not batch/cron)
- RxJS observables with `pipe()`, `map()`, `filter()`, `buffer()`
- Server-Sent Events (SSE) or WebSocket with ongoing data push
- Akka Streams, Reactor Flux, or Project Reactor with backpressure
- Kafka Streams or Flink with windowed operations (tumbling, sliding, session)
- gRPC server streaming or bidirectional streaming RPCs
- Python `async for` over an async generator or queue
- Redis Streams with `XREAD BLOCK`
- Backpressure mechanisms: buffering, dropping, throttling

### Confidence

- **high** — continuous consumer loop with backpressure handling and windowed aggregation
- **medium** — long-running consumer processing messages one at a time without explicit backpressure
- **low** — periodic polling disguised as streaming (fetch every N seconds)

---
description: Stringly Typed anti-pattern
type: anti-pattern
graphable: false
---
# Stringly Typed

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Strings used where enums or types should be (`status = "active"` instead of an enum)
- String comparison for branching logic (`if type == "admin"`)
- String parsing to extract structured data (`role.split(":")[1]`)
- Magic string constants scattered across multiple files with no single definition
- Function parameters typed as `str`/`string` that only accept a fixed set of known values

### Confidence

- **high** -- the same string literal appears in 3+ files for comparison or branching, with no enum or constant definition
- **medium** -- function signatures accept `string` for parameters that have a known, finite set of valid values
- **low** -- string literals used for status or type fields in a single module without a defining constant

## Impact

No compile-time safety; typos in string values cause silent runtime bugs that slip past code review.

### Symptoms

- A misspelled string (`"actve"` instead of `"active"`) causes a bug that only surfaces in specific code paths
- Renaming a status value requires a project-wide search-and-replace with no compiler assistance
- IDE autocomplete and refactoring tools cannot help because values are opaque strings
- Tests must cover every string variant manually since the type system provides no exhaustiveness checking
- Code review cannot catch invalid string values without memorizing the allowed set

### Remediation

- Replace string literals with enums, union types, or constant objects defined in a single location
- Use typed enums that the compiler can check for exhaustiveness in switch/match statements
- Introduce a validation layer at system boundaries that converts incoming strings to typed values immediately
- Add linting rules that flag raw string comparisons against known domain values
- For languages without enums, define a frozen set or constant map as the single source of truth

---
description: Structured Logging architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [observability]
---
# Structured Logging

## Recognition

How to identify this pattern in code.

### Signatures

- JSON log output format instead of plain text lines
- Key-value log fields: `logger.info("event", key=value)`, `log.With("key", value)`
- Libraries: `structlog` (Python), `logrus` (Go), `zap` (Go), `slog` (Go), `pino` (Node), `winston` with JSON transport
- Context binding: `logger = logger.bind(request_id=rid)`, `log.WithFields()`, `logger.With()`
- Log level as a structured field (`"level": "info"`) not a format prefix (`INFO:`)
- Correlation ID attached to every log entry
- Log configuration importing JSON formatter or structured encoder

### Confidence

- **high** -- JSON log formatter configured and context-bound logger used across request lifecycle
- **medium** -- structured logging library imported but log calls still use printf-style formatting
- **low** -- JSON output detected in logs but no explicit structured logging library in dependencies

## Architecture

Look for consistent structured output with contextual fields propagated through the request lifecycle.

### Review Checklist

- All log entries include a correlation/request ID for traceability
- Log fields are typed and consistent across services (not ad-hoc string interpolation)
- Sensitive data (passwords, tokens, PII) is never logged -- redaction is explicit
- Log levels are meaningful: ERROR for actionable failures, WARN for degradation, INFO for business events, DEBUG for troubleshooting
- Logger is bound to request context early and passed through the call chain

### Anti-patterns

- Mixing structured and unstructured logging in the same service
- Logging full request/response bodies without redaction
- Using string formatting inside structured log calls (`logger.info(f"user {user_id}")` instead of `logger.info("user_login", user_id=user_id)`)
- No correlation ID -- structured output with no way to trace a request across log entries

---
description: Subscription and recurring billing pattern for SaaS monetization
type: pattern
category: domain-model
abstraction: [data, financial]
---
# Subscription

## Recognition

How to identify this pattern in code.

### Signatures

- `Subscription`, `Plan`, `BillingCycle` model classes with status and period fields
- `invoice`, `Invoice`, `LineItem` classes for billing record generation
- `usage_meter`, `UsageMeter`, `metered_billing` for consumption-based pricing
- Stripe SDK: `stripe.Subscription`, `stripe.Invoice`, `stripe.PaymentIntent`
- Paddle SDK: `paddle`, `paddle.subscriptions`, webhook event handlers
- `trial`, `trial_end`, `trial_days` fields for free trial management
- `churn`, `MRR`, `ARR` metric calculations or dashboard fields
- `recurring_payment`, `billing_period`, `next_billing_date` scheduling fields
- Python: `djstripe`, `stripe` library, `billing` app or module
- JS/TS: `stripe` package, `@stripe/stripe-js`, subscription webhook handlers
- Go: `stripe-go`, `Subscription` struct with `Status` and `CurrentPeriodEnd`
- Java: `com.stripe.model.Subscription`, billing service with plan management

### Confidence

- **high** -- Stripe/Paddle integration with subscription lifecycle management (create, upgrade, downgrade, cancel), invoice generation, and webhook handling for payment events
- **medium** -- Custom Subscription and Plan models with billing cycle tracking and recurring charge scheduling
- **low** -- Simple boolean `is_premium` flag without plan tiers, billing cycles, or payment integration

## Architecture

### When to use
- SaaS products with tiered pricing plans and recurring revenue
- Usage-based or metered billing where charges depend on consumption
- Any product requiring trial periods, upgrades, downgrades, and cancellation flows

### Anti-patterns
- Building custom billing logic instead of using a payment provider's subscription management
- Not handling webhook delivery failures, causing billing state to drift from the payment provider
- Storing payment credentials locally instead of using tokenized references from the payment provider

### Complements
- [webhook](/concepts/webhook) — payment provider events arrive via webhooks
- [state-machine](/concepts/state-machine) — subscription lifecycle (trial, active, past_due, canceled) is a state machine
- [multi-tenant](/concepts/multi-tenant) — subscriptions often gate tenant-level feature access

## Impact

Subscription billing directly affects revenue. Failed payment handling, webhook reliability, and plan migration logic must be thoroughly tested. Monitoring must track payment failure rates, involuntary churn, and billing webhook processing lag to prevent silent revenue loss.

---
description: Suspense Boundary — declarative loading state management for async component trees
type: pattern
testable: true
graphable: true
abstraction: [frontend, lifecycle]
---
# Suspense Boundary

## Recognition

How to identify this pattern in code.

### Signatures

- `<Suspense fallback={...}>` (React)
- `<Suspense>` with `#fallback` template slot (Vue 3)
- `@defer` blocks (Angular 17+)
- `{#await}` blocks (Svelte)
- Nested suspense boundaries for granular loading states
- `useTransition` / `startTransition` for non-blocking updates (React)
- Streaming SSR with progressive hydration

### Confidence

- **high** -- explicit `<Suspense>` with fallback UI, nested boundaries for different loading zones
- **medium** -- framework provides implicit suspense (Next.js `loading.tsx`, Nuxt `<NuxtLoadingIndicator>`)
- **low** -- manual loading state management (`isLoading` flags) without declarative boundaries

## Architecture

Look for declarative boundaries that manage the loading state of async subtrees, providing fallback UI while suspended children resolve their data or code.

### Review Checklist

- Each async data boundary has its own Suspense wrapper (not one giant boundary)
- Fallback UI matches the layout of the loaded content (skeleton, not spinner)
- Nested boundaries prevent cascade (one slow component doesn't block siblings)
- Error boundaries are paired with suspense boundaries for failed loads
- SSR streaming is enabled when using server-side suspense

### Anti-patterns

- Single top-level Suspense wrapping the entire app (all-or-nothing loading)
- Suspense without paired error boundary (unhandled async failures)
- Using Suspense for synchronous conditional rendering (misuse of the pattern)
- Waterfall loading -- nested suspense that serializes parallel fetches

---
description: Swallowed Exception anti-pattern
type: anti-pattern
graphable: false
---
# Swallowed Exception

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Empty `except:` or `catch {}` blocks with no logging, metrics, or re-raise
- `except Exception: pass` or `catch(e) {}` that silently discard errors
- Error silently ignored with only a `# TODO: handle this` comment
- Catch-all exception handlers that return a default value without recording the failure
- `try/except` wrapped around large blocks of code with a bare `pass` in the handler

### Confidence

- **high** -- empty catch block or `except: pass` with no logging, metric, or alternative action
- **medium** -- catch block returns a default value (null, empty list) without logging the original exception
- **low** -- catch block logs at debug level only, which may be intentional but risks hiding errors in production

## Impact

Failures go completely unnoticed, making debugging impossible because the system silently produces wrong results instead of failing visibly.

### Symptoms

- Users report incorrect data or missing results but the logs show no errors
- Bugs take days to diagnose because the actual failure point left no trace
- System appears healthy by all metrics while silently dropping or corrupting data
- Intermittent issues are impossible to reproduce because the error evidence was discarded
- Technical debt accumulates as `TODO: handle this` comments never get addressed

### Remediation

- At minimum, log every caught exception at an appropriate level (warn for expected, error for unexpected)
- Replace bare `except:` or `catch(Exception)` with specific exception types that you know how to handle
- If an exception is truly ignorable, document explicitly why with a comment and emit a metric for visibility
- Add linting rules that flag empty catch blocks and bare `except:` clauses
- Use the "let it crash" principle: prefer failing loudly over silently returning wrong results

---
description: Sync-in-Async anti-pattern
type: anti-pattern
testable: true
graphable: false
---
# Sync-in-Async

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `requests.get()` or `requests.post()` inside an `async def` function
- Blocking I/O (`open()`, `socket.recv()`, `subprocess.run()`) in asyncio coroutines
- `time.sleep()` in an async function (should be `await asyncio.sleep()`)
- `open()` for file I/O without `aiofiles` in async code
- Database drivers without async support (`psycopg2` instead of `asyncpg`) used in async handlers
- `os.path.exists()`, `os.listdir()`, or other blocking OS calls in coroutines
- `urllib.request.urlopen()` inside `async def`
- Synchronous ORM calls (Django ORM without `sync_to_async`) in async views

### Confidence

- **high** -- `requests.get()` or `time.sleep()` directly inside an `async def`, especially in a web handler (FastAPI, aiohttp)
- **medium** -- blocking file I/O or synchronous database calls inside async functions, but wrapped in `run_in_executor`
- **low** -- synchronous utility calls in async code where the blocking duration is very short (< 1ms)

## Impact

Blocks the event loop, defeating the concurrency benefits of async and causing all concurrent tasks to stall.

### Symptoms

- Async web server handles requests sequentially despite async framework
- Response latency spikes when any single request involves blocking I/O
- Event loop warnings: `asyncio` reports "Executing ... took X seconds"
- Throughput does not improve with concurrent requests as expected from async architecture
- CPU usage is low while the event loop is blocked on I/O waits

### Remediation

- Replace `requests` with `httpx.AsyncClient` or `aiohttp.ClientSession` for HTTP calls
- Replace `time.sleep()` with `await asyncio.sleep()`
- Use `aiofiles` for file operations in async code
- Use async database drivers (`asyncpg`, `motor`, `aiosqlite`) instead of synchronous ones
- Wrap unavoidable blocking calls in `asyncio.to_thread()` or `loop.run_in_executor()`

---
description: Template Method architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Template Method

## Recognition

How to identify this pattern in code.

### Signatures

- Abstract base class with a concrete method calling abstract/hook methods in sequence
- Hook methods: `_do_step()`, `_on_before()`, `_on_after()`, `_process()`, `_validate()`
- Subclasses override specific steps without changing the overall algorithm structure
- Python: `ABC` with mix of concrete and `@abstractmethod` methods, `_hook()` naming convention
- Java: abstract class with `final` template method calling abstract `doStep()` methods
- Go: embedded struct with interface for overridable steps
- Rust: trait with default method implementations calling required methods

### Confidence

- **high** -- abstract base class with a final/concrete orchestrating method calling abstract step methods, plus subclasses
- **medium** -- base class with overridable hook methods called in a fixed sequence
- **low** -- inheritance hierarchy where subclasses override some methods of a base class

## Architecture

Look for invariant algorithm structure in the base class with variation points in subclasses.

### Review Checklist

- Template method defines the algorithm skeleton and is not overridable (final/non-virtual)
- Hook methods have sensible defaults (not all abstract -- allow partial override)
- Subclasses override only the intended extension points, not the template method itself
- Base class documents which hooks are required vs optional
- Number of hooks is small (3-5); too many indicates the algorithm should be decomposed

### Anti-patterns

- Subclass overriding the template method itself, breaking the invariant structure
- Too many abstract methods forcing subclasses to implement everything (defeats the template)
- Hook methods with hidden ordering dependencies not documented in the base class
- Using inheritance for code reuse when composition (strategy) would be cleaner

---
description: Temporal Coupling anti-pattern
type: anti-pattern
graphable: false
---
# Temporal Coupling

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Methods that must be called in a specific order (`init()` before `run()`, `connect()` before `query()`) but nothing in the type system enforces it
- Setup methods that silently fail or produce wrong results if called out of order
- Undocumented call sequences that only long-time contributors know
- Objects that are partially initialized after construction and require separate `configure()` or `setup()` calls
- Comments like "must call X before Y" or "call after init" scattered in the codebase
- State machine transitions with no explicit state tracking

### Confidence

- **high** -- calling methods out of order produces a runtime error or silent corruption, and the required order is not enforced by the API
- **medium** -- documentation or comments describe required call order, but the compiler/type system allows violations
- **low** -- a two-step initialization exists but the second step is always called immediately after construction

## Impact

Subtle bugs arise when methods are called in the wrong order, and nothing catches the mistake until runtime -- or worse, the mistake causes silent data corruption.

### Symptoms

- `NullPointerException` or `AttributeError` on fields that should have been set by a prior method call
- Tests pass individually but fail when run in a different order because shared setup was assumed
- Integration bugs appear only when components are wired together in a slightly different sequence
- Onboarding developers trigger errors that existing developers "just know" to avoid
- Race conditions in concurrent code because the required sequence is not atomic

### Remediation

- Use the type system to enforce order: return a new type from each step (Builder pattern, typestate pattern)
- Make constructors fully initialize objects: require all dependencies at construction time
- Combine steps that must happen together into a single method or factory
- If multi-step setup is unavoidable, validate preconditions at the start of each method and fail fast with a clear message
- Replace implicit state transitions with an explicit state machine that rejects invalid transitions

---
description: Tenant Isolation architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [security, data]
---
# Tenant Isolation

## Recognition

How to identify this pattern in code.

### Signatures

- Tenant ID in request context: `request.tenant_id`, `ctx.tenant`, `TenantContext.current()`
- `tenant_id` column in database tables, foreign key or partition key
- Schema-per-tenant: `SET search_path TO tenant_<id>`, dynamic schema selection
- Database-per-tenant: tenant-specific connection strings, connection pool per tenant
- Row-level security policies: `CREATE POLICY`, `ENABLE ROW LEVEL SECURITY`, `SET app.current_tenant`
- Tenant middleware extracting tenant from subdomain, header (`X-Tenant-ID`), or JWT claim
- Tenant-scoped query filters: `.filter(tenant_id=current_tenant)`, `WHERE tenant_id = ?`

### Confidence

- **high** -- row-level security or schema-per-tenant enforced at database level with middleware extracting tenant from auth token
- **medium** -- `tenant_id` column present and filtered in queries but no database-level enforcement
- **low** -- tenant identifier exists in the data model but some queries lack tenant filtering

## Architecture

Look for defense-in-depth tenant boundaries: middleware sets context, queries filter by tenant, database enforces isolation.

### Review Checklist

- Tenant context is set once at the request boundary (middleware/interceptor) and propagated, never parsed repeatedly
- Every data access query includes tenant filtering -- no unscoped queries that could leak cross-tenant data
- Database-level enforcement exists (RLS, schema isolation, or separate databases) as a safety net beyond application code
- Tenant ID is validated against the authenticated user's permissions, not blindly trusted from headers
- Background jobs and async tasks carry tenant context through the execution chain
- Tenant isolation is tested with explicit cross-tenant access attempts

### Anti-patterns

- Relying solely on application-level WHERE clauses with no database enforcement
- Trusting `X-Tenant-ID` header without validating it against the authenticated identity
- Queries that JOIN across tenants or aggregate without tenant scoping
- Missing tenant context in async workers -- background jobs running with no tenant or wrong tenant

---
description: Tenant-Aware Routing architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [security, integration]
---
# Tenant-Aware Routing

## Recognition

How to identify this pattern in code.

### Signatures

- Subdomain extraction: parsing tenant from `{tenant}.example.com`, `Host` header splitting
- `X-Tenant-ID` header injection or extraction at the gateway/load balancer layer
- Tenant-specific connection pools: `ConnectionPool.for_tenant(id)`, pool registry keyed by tenant
- Shard router: `ShardRouter.route(tenant_id)`, consistent hashing by tenant, shard map lookup
- Tenant config lookup: `TenantConfig.get(tenant_id)`, feature flags per tenant, tier-based routing
- Multi-database connection switching: `use_database(tenant.db_name)`, `router.db_for_read(tenant)`
- Tenant-based request routing at reverse proxy or service mesh level (Nginx, Envoy, Istio)

### Confidence

- **high** -- gateway extracts tenant, routes to tenant-specific backend or shard, with connection pool per tenant
- **medium** -- tenant ID extracted from request and used to select a database connection, but routing is application-level only
- **low** -- tenant identifier present in routing config but actual request routing does not vary by tenant

## Architecture

Look for a clear routing layer that maps tenant identity to the correct backend, database, or shard before business logic executes.

### Review Checklist

- Tenant resolution happens at the edge (gateway, load balancer, or first middleware) before any business logic
- Connection pools are bounded per tenant to prevent one tenant from exhausting shared resources
- Routing decisions are cached or precomputed -- no per-request database lookups for tenant config
- Fallback behavior is defined for unknown or misconfigured tenants (reject, not route to default)
- Shard mappings support rebalancing without downtime (migration path for moving tenants between shards)

### Anti-patterns

- Resolving tenant routing in business logic instead of infrastructure/middleware
- Unbounded connection pools per tenant that scale with tenant count and exhaust database connections
- Hardcoded tenant-to-shard mappings with no migration path for rebalancing
- No validation of tenant routing -- requests silently route to a wrong or default tenant on lookup failure

---
description: Tensor and matrix computation pattern for ML and numerical workloads
type: pattern
category: domain-model
abstraction: [data, compute]
---
# Tensor

## Recognition

How to identify this pattern in code.

### Signatures

- `torch.Tensor`, `torch.tensor()`, `torch.zeros()`, `torch.randn()` tensor creation
- `tf.Tensor`, `tf.constant()`, `tf.Variable()` TensorFlow tensor operations
- `jax.numpy`, `jnp.array()`, `jax.jit`, `jax.grad` JAX functional transforms
- `numpy.ndarray`, `np.array()`, `np.dot()`, `np.matmul()` array operations
- `model.predict()`, `model.forward()`, `model.__call__()` inference entry points
- `.to('cuda')`, `.to(device)`, `torch.cuda.is_available()` GPU dispatch
- `batch_size`, `DataLoader`, `Dataset` training/inference pipeline components
- Go: `gonum/mat`, `gorgonia` tensor operations
- Rust: `ndarray`, `tch-rs` (PyTorch bindings), `candle` tensor library
- Java: `DJL` (Deep Java Library), `nd.NDArray`, `tensorflow-java` bindings

### Confidence

- **high** -- PyTorch/TensorFlow/JAX model with tensor operations, GPU dispatch, and a DataLoader-based inference or training pipeline
- **medium** -- NumPy ndarray computations with matrix operations and batch processing but no deep learning framework
- **low** -- Simple array math without explicit tensor semantics or multi-dimensional broadcasting

## Architecture

### When to use
- Machine learning model training and inference pipelines
- Scientific computing with multi-dimensional array operations
- GPU-accelerated numerical workloads requiring batch processing

### Anti-patterns
- Running inference on CPU in production when GPU is available, causing unnecessary latency
- Loading the full model on every request instead of keeping it warm in memory
- Ignoring tensor dtype and device mismatches, causing silent precision loss or runtime errors

### Complements
- [feature-store](/concepts/feature-store) — tensor models consume features from feature stores
- [model-registry](/concepts/model-registry) — trained models are versioned and served from a registry
- [training-pipeline](/concepts/training-pipeline) — tensor computations are core to training pipelines

## Impact

Tensor workloads have fundamentally different resource profiles than typical services — they require GPU scheduling, batch-oriented scaling, and memory management for large model weights. Monitoring must track inference latency, GPU utilization, and memory pressure to prevent OOM failures.

---
description: Test Doubles (Mock/Stub/Fake/Spy) architectural pattern
type: pattern
testable: true
graphable: false
abstraction: [testing]
---
# Test Doubles (Mock/Stub/Fake/Spy)

## Recognition

How to identify this pattern in code.

### Signatures

- `unittest.mock`, `MagicMock`, `patch()` decorators in Python test files
- `jest.fn()`, `jest.spyOn()` in JavaScript/TypeScript tests
- `sinon.stub()`, `sinon.spy()`, `sinon.fake()` in Node.js tests
- `gomock.NewController`, `mockgen` generated files in Go
- `mockito`, `@Mock`, `@InjectMocks`, `when().thenReturn()` in Java tests
- `Fake*` or `Mock*` or `Stub*` classes in test directories
- Spy assertions on `.call_count`, `.called_with`, `.toHaveBeenCalledTimes()`

### Confidence

- **high** — Mock/stub/fake classes implementing production interfaces found in test directories, with explicit verification of call behavior
- **medium** — `patch()` or `jest.fn()` usage in tests without dedicated fake implementations
- **low** — Test helper functions that return hardcoded values but are not explicitly named as doubles

## Architecture

Look for clear separation between the type of double (mock, stub, fake, spy) and appropriate use of each.

### Review Checklist

- Mocks verify behavior (was this method called?), stubs provide canned answers, fakes have working implementations -- each is used for its intended purpose
- Doubles implement the same interface/protocol as the real dependency
- Test doubles live in test directories, never imported by production code
- Spy assertions check meaningful interactions, not implementation details
- Fakes for external services (databases, APIs) are maintained alongside their real counterparts
- Double setup is extracted into helpers or fixtures to avoid repetition across tests

### Anti-patterns

- Mocking everything including the unit under test, leaving nothing real to verify
- Asserting on internal call order rather than observable outcomes
- Stubs that silently return success for every input, hiding real failure paths
- Production code importing from test double modules

---
description: Test Pollution anti-pattern
type: anti-pattern
testable: true
graphable: false
---
# Test Pollution

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Tests modifying global state (module-level variables, class attributes, singletons)
- Missing teardown or cleanup (`setUp` without matching `tearDown`)
- `setUpClass` without matching `tearDownClass`
- Shared fixtures mutated between tests (e.g., appending to a list in a shared fixture)
- Database not reset between test cases (previous test data affecting subsequent tests)
- Environment variables set in one test and not restored
- Monkey-patching without restoration (manual `module.func = mock` without cleanup)
- Global registry or cache populated by tests and never cleared

### Confidence

- **high** -- tests pass individually but fail when run together, and the failure depends on which test ran first
- **medium** -- `setUpClass` modifies shared state without `tearDownClass`, or fixtures are mutated across tests
- **low** -- tests use global state but have not yet shown order-dependent failures

## Impact

Test order dependencies and intermittent failures, making the test suite unreliable and hiding real bugs behind environmental noise.

### Symptoms

- Tests pass in isolation (`pytest test_file.py::test_one`) but fail when run as a full suite
- Adding or removing a test causes unrelated tests to start failing
- Test results differ between local runs and CI due to execution order
- Debugging test failures requires understanding which tests ran before the failing one
- Flaky failures disappear when test ordering changes

### Remediation

- Use fresh fixtures per test (`setUp`/`tearDown` or `pytest` function-scoped fixtures)
- Always pair `setUpClass` with `tearDownClass` to restore class-level state
- Use `unittest.mock.patch` or `monkeypatch` (pytest) which auto-restore on test exit
- Reset database state between tests with transactions (rollback after each test) or truncation
- Run tests in random order (`pytest-randomly`) to detect pollution early

---
description: Tick-Based Simulation architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [lifecycle, realtime]
---
# Tick-Based Simulation

## Recognition

How to identify this pattern in code.

### Signatures

- `tick()` or `step()` method called at a fixed rate with a tick counter
- Discrete time steps where all state advances atomically per tick
- `fixed_update()` distinct from frame-based rendering updates
- Tick counter or tick number used for ordering, replay, and synchronization
- Deterministic update functions: same inputs at same tick produce same outputs
- Lockstep networking where clients exchange inputs per tick
- Replay systems that record and replay per-tick inputs
- Simulation rate constants (e.g., `TICKS_PER_SECOND = 20`)

### Confidence

- **high** — `tick()` method with a tick counter, deterministic state updates, and replay or lockstep networking
- **medium** — fixed-rate `step()` function with discrete state transitions and a simulation clock
- **low** — periodic timer advancing state in uniform increments without explicit tick numbering

## Architecture

Look for deterministic discrete-time state progression with explicit tick ordering.

### Review Checklist

- Tick updates are deterministic: identical inputs at the same tick always produce the same state
- Tick rate is decoupled from frame rate (simulation runs independently of rendering)
- State snapshots or input logs enable replay from any tick
- Tick counter is monotonic and used as the canonical time reference
- Network synchronization uses tick-aligned input exchange, not wall-clock timestamps
- Late or missing inputs are handled explicitly (prediction, rollback, or pause)

### Anti-patterns

- Using wall-clock time instead of tick numbers for simulation ordering
- Non-deterministic operations (random without seed, floating-point inconsistencies) inside tick updates
- Coupling tick rate to frame rate, causing simulation speed to vary with performance
- No mechanism to handle missed or late ticks in networked scenarios

---
description: Tight Coupling anti-pattern
type: anti-pattern
graphable: false
---
# Tight Coupling

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Concrete class references everywhere with no interfaces or protocols between components
- Constructors that create their own dependencies internally (`self.db = Database()`) instead of receiving them via injection
- Direct database calls and HTTP requests embedded in business logic methods
- Changing one class signature breaks many other classes that reference it directly
- Extensive use of `isinstance` checks against concrete types to branch behavior

### Confidence

- **high** -- business logic directly instantiates infrastructure (database connections, HTTP clients, file handles) and changing one class cascades compilation or test failures across 5+ other files
- **medium** -- no dependency injection framework or manual injection pattern, concrete types used in method signatures instead of abstractions
- **low** -- classes reference each other by name but the coupling might be intentional and stable

## Impact

Cannot test, swap, or evolve components independently because every piece is wired directly to its collaborators.

### Symptoms

- Unit tests require real databases, network connections, or complex mocks because dependencies cannot be substituted
- Swapping an implementation (e.g., switching from PostgreSQL to SQLite for testing) requires modifying business logic code
- A single interface change ripples across the codebase
- Components cannot be reused in different contexts because they hard-code their environment
- Feature flags and A/B tests are difficult because alternatives cannot be injected

### Remediation

- Introduce interfaces or protocols at component boundaries and depend on those rather than concrete classes
- Apply constructor injection: pass dependencies in rather than creating them internally
- Use a composition root or lightweight DI container to wire dependencies at application startup
- Isolate infrastructure behind adapter interfaces (ports and adapters / hexagonal architecture)
- Write tests that verify coupling: if a unit test needs more than 2-3 test doubles, the unit is too coupled

---
description: Time-series data pattern for temporal metrics and event streams
type: pattern
category: domain-model
abstraction: [data, temporal]
---
# Time Series

## Recognition

How to identify this pattern in code.

### Signatures

- `timestamp` as the primary or leading index column in tables or collections
- `retention_policy` configuration for automatic data expiry
- `downsample` or `rollup` functions aggregating high-frequency data into coarser buckets
- InfluxDB client: `influxdb_client`, `write_api`, `query_api`, Flux query language
- TimescaleDB: `create_hypertable`, `time_bucket()`, `add_retention_policy()`
- Prometheus: `prometheus_client`, `Counter`, `Gauge`, `Histogram`, `Summary` metric types
- Python: `pandas.DatetimeIndex`, `resample()`, `rolling()` window operations
- JS/TS: `@influxdata/influxdb-client`, timeseries-specific ORMs
- Go: `prometheus/client_golang`, `influxdb-client-go`, custom `TimeBucket` aggregation
- Rust: `influxdb`, `prometheus` crate, timestamp-indexed data structures

### Confidence

- **high** -- TimescaleDB hypertable or InfluxDB bucket with retention policies, time_bucket aggregation, and downsampling jobs
- **medium** -- Prometheus metrics with histogram/summary types and recording rules for pre-aggregation
- **low** -- Regular table with a timestamp column and ad-hoc time-range queries without specialized time-series tooling

## Architecture

### When to use
- Metrics, monitoring, and observability data with high write throughput and time-range queries
- IoT sensor data, financial tick data, or any append-heavy temporal stream
- Workloads where data naturally ages and older data can be downsampled or expired

### Anti-patterns
- Querying raw high-frequency data for dashboards instead of using pre-aggregated rollups
- No retention policy, causing unbounded storage growth as time-series data accumulates
- Using a general-purpose RDBMS for time-series workloads without partitioning or hypertables

### Complements
- [metrics-instrumentation](/concepts/metrics-instrumentation) — time-series storage backs metrics pipelines
- [materialized-view](/concepts/materialized-view) — rollups and pre-aggregations are materialized views over time
- [stream-to-store](/concepts/stream-to-store) — streaming ingestion feeds time-series stores

## Impact

Time-series data drives monitoring, alerting, and capacity planning. Retention policies and downsampling directly affect storage costs and query performance, so missing configurations silently degrade both operational visibility and infrastructure budgets.

---
description: Timeout architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [resilience, integration]
---
# Timeout

## Recognition

How to identify this pattern in code.

### Signatures

- `timeout=` parameter on HTTP, gRPC, or database calls
- `context.WithTimeout` or `context.WithDeadline` (Go)
- `asyncio.wait_for(timeout=)` (Python)
- `socket.settimeout()` (Python)
- `TimeoutError` or `DeadlineExceeded` handling in catch/except blocks
- Request timeout configs (`connect_timeout`, `read_timeout`, `write_timeout`)
- Deadline propagation across service boundaries via context or headers
- `AbortController` with `setTimeout` (JavaScript)

### Confidence

- **high** -- explicit timeout parameter on every external call with corresponding error handling
- **medium** -- timeout config present but not consistently applied to all call sites
- **low** -- only default framework timeouts relied upon, no explicit timeout values in code

## Architecture

Look for explicit timeout enforcement on every external call with deadline propagation across boundaries.

### Review Checklist

- Every external call (HTTP, DB, gRPC, message broker) has an explicit timeout set
- Timeouts propagate through the call chain -- downstream deadlines are shorter than upstream
- Timeout values are configurable, not hardcoded literals
- Timeout errors are caught and handled distinctly from other failures
- Connection timeouts are separate from read/write timeouts

### Anti-patterns

- No timeout on external calls -- a hung dependency blocks the caller indefinitely
- Uniform timeout across all calls regardless of expected latency profile
- Catching timeout errors silently without logging, metrics, or fallback
- Deadline not propagated to downstream services -- child call outlives parent deadline

See also: circuit-breaker, retry (often combined)

---
description: Token-Based Authentication (JWT) architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [security]
---
# Token-Based Authentication (JWT)

## Recognition

How to identify this pattern in code.

### Signatures

- `Authorization: Bearer <token>` header extraction in middleware
- JWT decode/verify calls (`jwt.decode()`, `jwt.verify()`, `jwt.encode()`)
- Token claims parsing: `exp`, `iat`, `sub`, `iss`, `aud`
- Refresh token flow with separate `/refresh` or `/token` endpoint
- Stateless validation against a signing key or JWKS endpoint
- `jsonwebtoken` (Node), `PyJWT` (Python), `jose` (JS/Rust), `golang-jwt` (Go) library imports
- JWKS URI configuration for key rotation (`/.well-known/jwks.json`)
- Token blacklist or revocation check for logout support

### Confidence

- **high** -- `Authorization: Bearer` extraction, JWT signature verification with `exp`/`iss`/`aud` claim validation, and refresh token flow implemented
- **medium** -- JWT decode present with expiry check but no signature verification or refresh flow visible
- **low** -- Bearer token in headers but no JWT-specific parsing (could be opaque tokens or API keys)

## Architecture

Look for stateless token validation with proper signing, claim verification, and secure token lifecycle management.

### Review Checklist

- Tokens are signed with a strong algorithm (RS256/ES256 for asymmetric, HS256 minimum for symmetric)
- Signature is always verified before trusting claims (never decode-only)
- Expiry (`exp`), issuer (`iss`), and audience (`aud`) claims are validated on every request
- Access tokens have short TTL (minutes, not hours) with refresh tokens for renewal
- Refresh tokens are stored securely and rotated on use (one-time use)
- Token revocation mechanism exists for logout and compromise scenarios

### Anti-patterns

- Using `none` algorithm or allowing algorithm switching in verification (algorithm confusion attack)
- Storing JWTs in localStorage (vulnerable to XSS) instead of httpOnly cookies or memory
- Long-lived access tokens with no refresh flow (hours or days without rotation)
- Including sensitive data (PII, secrets) in token payload (JWTs are base64-encoded, not encrypted)

---
description: Train Wreck anti-pattern
type: anti-pattern
graphable: false
---
# Train Wreck

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `a.getB().getC().getD().doThing()` -- long method chains navigating through an object graph
- Multiple dots on a single expression traversing different objects (not fluent API on the same object)
- Violating the Law of Demeter: reaching through multiple layers of objects to get to a distant collaborator
- Null checks chained: `if a and a.b and a.b.c and a.b.c.d`
- Code that breaks when any intermediate object in the chain changes its structure

### Confidence

- **high** -- a single expression chains through 4+ different objects' methods or properties to reach a value
- **medium** -- code reaches through 2-3 objects and would break if any intermediate type changed
- **low** -- a fluent API chain on the same builder object (this is intentional and not a train wreck)

## Impact

Tight coupling to the entire object structure, making the code fragile to any change in the intermediate types.

### Symptoms

- A change to one class deep in the hierarchy breaks code in distant, seemingly unrelated modules
- NullPointerException or AttributeError at some point in the chain with no clear indication of which link was null
- Test setup requires building elaborate object graphs just to reach the value the test needs
- Code duplication: the same chain appears in multiple places because there is no encapsulated accessor
- Refactoring any intermediate class requires updating every chain that traverses through it

### Remediation

- Follow the Law of Demeter: only talk to your immediate collaborators, not their collaborators
- Create delegate methods that encapsulate the traversal: `a.doThingOnD()` instead of `a.getB().getC().getD().doThing()`
- Pass the needed value directly rather than passing the root object and letting the callee navigate
- Use null-safe navigation operators (`?.` in Kotlin/C#, `&.` in Ruby) as a stopgap, not a solution
- Flatten the data structure if the deep nesting does not represent a genuine domain relationship

---
description: Training Pipeline architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [data, ml]
---
# Training Pipeline

## Recognition

How to identify this pattern in code.

### Signatures

- Sequential stages: data loading, preprocessing, training, evaluation, model export
- Hyperparameter configuration files (YAML/JSON) or config objects
- Experiment tracking with run IDs, logged metrics, and parameters
- Methods like `fit()`, `train()`, `evaluate()`, `save_model()`
- Epoch loops, batch iterators, learning rate schedulers
- Checkpoint saving and resumption for long-running training
- Libraries: PyTorch Lightning, Keras, TFX, Kubeflow Pipelines, Metaflow, Airflow, Ray Train

### Confidence

- **high** — multi-stage pipeline with data loading, `fit()`/`train()`, evaluation, and model export, plus experiment tracking
- **medium** — training script with epoch loop, metric logging, and checkpoint saving
- **low** — script that loads data, calls a model's fit method, and saves the result

## Architecture

Look for a structured pipeline with reproducible stages from raw data to validated model artifact.

### Review Checklist

- Each stage (load, preprocess, train, evaluate, export) is a discrete, testable unit
- Hyperparameters are externalized in config, not hardcoded in training code
- Experiment tracking records all parameters, metrics, and artifacts per run
- Checkpoints are saved periodically so training can resume after failure
- Evaluation stage gates the model: only models meeting threshold metrics are exported
- Data versioning or snapshotting ensures reproducibility of training runs

### Anti-patterns

- Monolithic training script with no separation between data prep, training, and evaluation
- Hardcoded hyperparameters scattered throughout training code
- No checkpointing, requiring full restart on any failure during long training runs
- Training results not tracked, making it impossible to compare runs or reproduce outcomes

---
description: Trie (Prefix Tree) architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [data]
---
# Trie (Prefix Tree)

## Recognition

How to identify this pattern in code.

### Signatures

- Node-per-character tree structure with children stored in a dict or fixed-size array
- `insert()`, `search()`, `starts_with()` (or `has_prefix()`) methods
- `TrieNode` class with a `children` mapping and an `is_end` / `is_terminal` flag
- Autocomplete or typeahead search implementations
- IP routing table or CIDR prefix matching (bitwise trie)
- Prefix-based filtering or longest-prefix-match logic
- `pygtrie`, `datrie` (Python), `trie-memoize` (Node), Apache Commons `PatriciaTrie` (Java)
- Compressed variants: radix tree, Patricia trie, PATRICIA

### Confidence

- **high** -- Node-per-character tree with `insert`/`search`/`starts_with` and terminal markers
- **medium** -- Prefix matching logic with tree traversal but no explicit `TrieNode` class
- **low** -- Nested dictionary structure used for prefix lookups that may be a trie

## Architecture

Look for correct prefix-based operations with efficient shared-prefix storage.

### Review Checklist

- Each node stores only the branching structure, not full copies of keys
- Terminal/end-of-word markers correctly distinguish complete keys from prefixes
- Memory usage is considered -- standard tries can be sparse; compression (radix) is used when appropriate
- Deletion correctly handles non-leaf nodes that are prefixes of other keys
- Character set is bounded and known (alphabet size affects node children storage choice)
- Thread safety is addressed if the trie is accessed concurrently

### Anti-patterns

- Storing full keys at every node instead of leveraging shared prefixes
- Missing terminal markers -- `search("app")` incorrectly returns true when only `"apple"` was inserted
- Using a standard trie for large alphabets without compression (excessive memory waste)
- Implementing deletion by simply unsetting the terminal flag without pruning orphaned branches

---
description: Unbounded Growth anti-pattern
type: anti-pattern
observable: true
graphable: false
---
# Unbounded Growth

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Lists or dicts that grow without bound (`cache = {}` with no eviction)
- No TTL on cache entries (items added but never expired)
- No max size on collections (no `maxlen`, `maxsize`, or capacity check)
- Append-only patterns without eviction (`history.append()` in a long-running process)
- `@lru_cache` without `maxsize` parameter (defaults to 128, but `maxsize=None` means unbounded)
- In-memory queues with no consumer backpressure or size limit
- Log buffers or event collectors that accumulate indefinitely
- Session stores or connection pools that grow but never shrink

### Confidence

- **high** -- a dict or list in a long-running process grows monotonically with no eviction, TTL, or size limit, and memory usage climbs over time
- **medium** -- cache or collection has no visible size limit, but the growth rate may be slow enough to not trigger OOM quickly
- **low** -- `append()` or dict assignment in a loop without clear bounds, but the process may be short-lived

## Impact

Memory exhaustion and OOM crashes in long-running processes as collections grow without limit.

### Symptoms

- Application memory usage increases steadily over hours or days
- OOM kills in production after extended uptime (visible in `dmesg` or container logs)
- Performance degrades gradually as data structures grow (slower lookups, GC pressure)
- Restarting the process temporarily resolves memory issues
- Memory profiling shows a single dict or list consuming most of the heap

### Remediation

- Use `collections.OrderedDict` with size-limited eviction or `functools.lru_cache(maxsize=N)`
- Set TTL on cache entries using `cachetools.TTLCache` or equivalent
- Use `collections.deque(maxlen=N)` instead of unbounded lists for rolling buffers
- Implement backpressure or size limits on in-memory queues
- Add memory monitoring and alerts for long-running processes to catch growth before OOM

---
description: Unit of Work architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design, data]
---
# Unit of Work

## Recognition

How to identify this pattern in code.

### Signatures

- Transaction management wrapping multiple repository operations
- Explicit `commit()` and `rollback()` methods on a unit-of-work object
- Dirty object tracking: `register_new()`, `register_dirty()`, `register_deleted()`
- SQLAlchemy `Session` used as a unit of work (add, flush, commit)
- Django `transaction.atomic()` blocks coordinating multiple saves
- Entity Framework `DbContext` with `SaveChanges()`
- Context manager or decorator scoping a transaction boundary

### Confidence

- **high** -- explicit UoW class tracking changes with `commit()`/`rollback()` controlling flush
- **medium** -- ORM session used transactionally across multiple repository calls within a single scope
- **low** -- `transaction.atomic()` or `BEGIN`/`COMMIT` blocks without explicit change tracking

## Architecture

Look for a single transactional boundary that coordinates writes across multiple repositories and flushes them atomically.

### Review Checklist

- All repository operations within a use case share the same unit of work instance
- Commit happens once at the end of the business operation, not per-repository call
- Rollback on failure reverts all changes, not just the last write
- Unit of work lifetime is scoped to the request or use case, not a singleton
- Nested units of work are either prohibited or handled with savepoints

### Anti-patterns

- Each repository managing its own transaction independently (no coordination)
- Committing inside individual repository methods instead of at the UoW boundary
- Long-lived units of work that span multiple user interactions (session leak)
- Catching exceptions inside the UoW and continuing after partial failure

---
description: Value Object architectural pattern
type: pattern
testable: true
graphable: false
abstraction: [design]
---
# Value Object

## Recognition

How to identify this pattern in code.

### Signatures

- `@dataclass(frozen=True)` or `@attr.s(frozen=True)` in Python
- `record` types in Java 16+ or C#
- `__eq__` and `__hash__` implemented based on all fields, not identity
- No setter methods or mutating operations on the object
- `frozenset` or `tuple` used instead of mutable collections
- Factory methods that return new instances instead of modifying existing ones
- Classes named `*Value`, `*Amount`, `*Range`, `*Address`, `*Money`, `*Quantity`

### Confidence

- **high** -- Immutable class with equality by value, no ID field, and a factory method for transformations
- **medium** -- Frozen dataclass or record type with no setters, but equality semantics not explicitly defined
- **low** -- Plain class that happens to have no setters but is compared by reference or has an ID field

## Architecture

Look for immutable objects that are compared by their field values rather than by identity.

### Review Checklist

- Object is immutable after construction (no setters, no mutable internal state)
- Equality is based on all significant fields, not object identity
- Hash code is consistent with equality (same fields used)
- Validation happens at construction time -- invalid states are impossible
- Transformations return new instances rather than mutating in place

### Anti-patterns

- Value object with an `id` field that participates in equality checks
- Mutable fields hidden behind an immutable facade (e.g., internal mutable list)
- Equality defined on a subset of fields, breaking substitutability
- Value objects that grow to hold behavior unrelated to the value they represent

See also: ddd

---
description: Versioned document pattern with revision history and conflict resolution
type: pattern
category: domain-model
abstraction: [data, collaboration]
---
# Versioned Document

## Recognition

How to identify this pattern in code.

### Signatures

- `revision`, `version`, or `version_number` fields tracking document iterations
- `version_history` or `revisions` array/table storing past states
- `diff` and `patch` functions computing and applying changes between versions
- CRDT imports: `yjs`, `automerge`, `diamond-types`, `loro`
- Operational Transform: `ot`, `operational_transform`, `ShareDB`, `sharedb`
- Python: `diff_match_patch`, `deepdiff`, custom `Revision` model classes
- JS/TS: `yjs`, `automerge`, `Yjs.Doc`, `prosemirror` with collaboration plugin
- Go: `sergi/go-diff`, `revision` structs with parent hash references
- Rust: `automerge-rs`, `diamond-types`, `similar` crate for diff computation
- `snapshot` and `restore` methods for materializing a specific version

### Confidence

- **high** -- CRDT or OT library with real-time collaboration, plus a revision history table with immutable snapshots and diff-based change tracking
- **medium** -- Version number field with a revisions table storing full document snapshots on each edit
- **low** -- Simple `updated_at` timestamp or `version` integer used for optimistic locking without actual content history

## Architecture

### When to use
- Collaborative editing where multiple users modify the same document concurrently
- Content management systems requiring full revision history and rollback capability
- Legal, regulatory, or compliance contexts where every change must be preserved

### Anti-patterns
- Storing only the latest version, making rollback impossible without backups
- Using optimistic locking version numbers but never actually persisting revision content
- Implementing custom merge logic instead of using proven CRDT/OT libraries for real-time collaboration

### Complements
- [event-sourcing](/concepts/event-sourcing) — document revisions can be modeled as an event stream
- [block-content](/concepts/block-content) — versioned documents often use block-based content structures
- [optimistic-locking](/concepts/optimistic-locking) — version fields serve double duty for concurrency control

## Impact

Versioned documents create storage growth proportional to edit frequency and require merge conflict resolution strategies. Testing must cover concurrent edit scenarios, and monitoring should track revision chain integrity and storage consumption over time.

---
description: Visitor architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Visitor

## Recognition

How to identify this pattern in code.

### Signatures

- `accept(visitor)` method on element/node classes
- `visit_*(node)` methods on visitor classes: `visit_BinaryExpr`, `visit_Literal`, `visit_IfStmt`
- Double dispatch: element calls `visitor.visit_X(self)` in its `accept()` method
- AST walkers, tree traversals, compiler passes, serialization visitors
- Python: `ast.NodeVisitor` with `visit_*` methods, `generic_visit()` fallback
- Java: `Visitor` interface with `visit()` overloads per element type
- Rust: visitor traits in `syn` crate, `Visit`/`VisitMut` patterns
- Go: `ast.Walk` with `ast.Visitor` interface

### Confidence

- **high** -- `accept(visitor)` on elements plus `visit_Type(element)` methods on visitors (classic double dispatch)
- **medium** -- visitor class with `visit_*` methods dispatched by element type, without explicit `accept()`
- **low** -- type-switch traversal over a union/enum of node types

## Architecture

Look for correct double dispatch and separation of algorithm from data structure.

### Review Checklist

- Each element type has an `accept()` that dispatches to the correct `visit_*` method
- Adding a new visitor does not require modifying element classes
- Visitor has access to the element's public interface, not its internals
- Traversal order is well-defined (depth-first, breadth-first) and controlled
- Fallback handling exists for unvisited element types (`generic_visit` or error)

### Anti-patterns

- Visitor reaching into element private state (breaks encapsulation)
- Adding a new element type requires modifying every existing visitor (fragile)
- Visitor accumulating mutable state across visits without clear reset boundaries
- Using visitor when a simple polymorphic method on the elements would suffice

---
description: Webhook architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [integration]
---
# Webhook

## Recognition

How to identify this pattern in code.

### Signatures

- Callback URL registration endpoints (`POST /webhooks`, `webhook_url` config field)
- HTTP POST to registered endpoints when events occur
- Webhook payload signing with HMAC (`X-Hub-Signature`, `X-Signature-256` headers)
- Retry with exponential backoff on delivery failure (4xx/5xx responses)
- `webhook_url` or `callback_url` in configuration or database models
- Event delivery queue backing webhook dispatch
- Signature verification on the receiving side (`hmac.compare_digest`)

### Confidence

- **high** -- callback URL registration, signed payloads, and retry logic all present
- **medium** -- HTTP POST on events with callback URLs but no signing or retry mechanism
- **low** -- outbound HTTP calls triggered by events but no formal registration or delivery guarantees

## Architecture

Look for event-driven HTTP callback delivery with authentication and at-least-once guarantees.

### Review Checklist

- Payloads are signed with a shared secret (HMAC-SHA256) and receivers verify the signature
- Failed deliveries are retried with exponential backoff and a maximum retry count
- Webhook endpoints are registered with validation (URL reachability or ownership proof)
- Idempotency keys or event IDs are included so receivers can deduplicate
- A dead-letter mechanism exists for permanently failed deliveries
- Payload size is bounded to prevent abuse

### Anti-patterns

- No payload signing -- receivers cannot verify the sender's identity
- Synchronous webhook dispatch blocking the event producer
- No retry mechanism -- a single network failure permanently drops the event
- Unbounded payload size allowing arbitrarily large deliveries

---
description: WebSocket architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [infrastructure, integration]
---
# WebSocket

## Recognition

How to identify this pattern in code.

### Signatures

- `ws://` or `wss://` URL schemes in connection strings or config
- `on_message`, `on_connect`, `on_close`, `on_error` handler callbacks
- HTTP `Upgrade: websocket` and `Connection: Upgrade` headers
- Ping/pong frame handling for keepalive
- Import of `websockets` (Python), `ws` or `socket.io` (Node), `gorilla/websocket` (Go)
- Spring `@MessageMapping` or `@EnableWebSocket` annotations
- `WebSocketHandler`, `WebSocketServer`, `WebSocketClient` class names
- `STOMP` or `SockJS` fallback configuration

### Confidence

- **high** -- `ws://`/`wss://` URLs combined with message handler callbacks and upgrade headers
- **medium** -- WebSocket library imports with handler registration but no visible connection lifecycle
- **low** -- Generic bidirectional messaging code without explicit WebSocket protocol references

## Architecture

Look for correct connection lifecycle management and message framing over persistent bidirectional channels.

### Review Checklist

- Connection lifecycle is complete: open, message, error, close handlers all defined
- Ping/pong or application-level heartbeat prevents silent connection drops
- Reconnection logic with backoff exists on the client side
- Message serialization format is consistent (JSON, protobuf) with schema validation
- Connection limits and backpressure are enforced on the server
- Authentication happens during the upgrade handshake, not after

### Anti-patterns

- No reconnection strategy -- single disconnect permanently kills the session
- Sending unbounded messages without flow control or rate limiting
- Performing authentication only via query params in the `ws://` URL (leaks credentials in logs)
- Using WebSocket where SSE or simple polling would suffice (over-engineering)

---
description: Worker/Thread Pool architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [concurrency, infrastructure]
---
# Worker/Thread Pool

## Recognition

How to identify this pattern in code.

### Signatures

- Fixed pool of workers processing tasks submitted to a shared queue
- `ThreadPoolExecutor`, `ProcessPoolExecutor`, or equivalent pool constructors
- Worker count configuration (often tied to CPU count or a config value)
- `submit()`, `map()`, or `apply_async()` calls dispatching work to the pool
- Libraries: Python `concurrent.futures`, Go goroutine pools, Node `worker_threads`, Java `ExecutorService`

### Confidence

- **high** -- Explicit pool instantiation with `ThreadPoolExecutor(max_workers=N)` or equivalent
- **medium** -- Fixed number of goroutines or threads pulling from a shared channel/queue
- **low** -- Multiple workers processing tasks concurrently without a formal pool abstraction

## Architecture

Look for a fixed set of reusable workers pulling tasks from a shared submission queue.

### Review Checklist

- Pool size is configurable and documented (not hardcoded magic numbers)
- Tasks submitted to the pool are independent -- no hidden shared state between tasks
- Pool shutdown is graceful: pending tasks complete before termination
- Exceptions in worker tasks are captured and reported, not silently lost
- Resource limits are enforced (max queue depth, task timeout)
- Future/result objects are consumed -- no fire-and-forget leaks

### Anti-patterns

- Creating a new thread per task instead of reusing pooled workers
- Pool size equal to unbounded input (defeats the purpose of pooling)
- Blocking the main thread waiting on every future immediately after submission (serial execution)
- No timeout on task execution, allowing hung tasks to consume a worker forever

---
description: Workflow Engine architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [lifecycle, integration]
---
# Workflow Engine

## Recognition

How to identify this pattern in code.

### Signatures

- `@task`, `@dag`, `@workflow`, `@step` decorators defining workflow steps
- DAG (directed acyclic graph) definitions with explicit step dependencies
- State machine implementations tracking workflow progress (`pending`, `running`, `completed`, `failed`)
- Libraries: Airflow, Temporal, AWS Step Functions, Prefect, Celery chains/chords, Argo Workflows
- Workflow definition files (YAML/JSON DAGs, state machine definitions)
- Step retry policies, timeout configuration, and conditional branching
- `workflow_id` or `run_id` used for tracking execution instances

### Confidence

- **high** -- DAG definitions with explicit dependencies, a workflow engine library, and step state tracking with retry policies
- **medium** -- Sequential task chains with dependency ordering and basic state tracking, but no formal DAG library
- **low** -- Chained function calls with manual error handling that loosely resembles a workflow but has no formal orchestration

## Architecture

Look for DAG-based task orchestration with explicit step dependencies, state tracking, and failure handling.

### Review Checklist

- Each step is idempotent and safe to retry on failure
- Step dependencies form a valid DAG (no circular dependencies)
- Workflow state is persisted so execution can resume after a crash
- Timeout and retry policies are defined per step, not globally
- Failed workflows can be manually retried from the point of failure
- Workflow execution is observable (step-level status, duration, and logs)

### Anti-patterns

- Workflows defined in imperative code with no visible dependency graph
- Steps that cannot be retried because they produce side effects without idempotency keys
- Monolithic workflow with dozens of tightly coupled steps instead of composed sub-workflows
- No persistent state -- a process crash loses all progress and requires full restart

See also: saga (for distributed transactions with compensation)

---
description: Workflow/state machine domain model — entities with defined states, transitions, and guards
type: domain-model
abstraction: [data, lifecycle]
---
# Workflow / State Machine

## Recognition

### Signatures

- State enum or constants: `PENDING`, `APPROVED`, `REJECTED`, `COMPLETED`, `CANCELLED`
- Transition functions that validate current state before allowing change
- Guard conditions on transitions (e.g., "can only approve if all reviewers signed off")
- State machine libraries: XState (JS), transitions (Python), statesman (Ruby), Spring Statemachine
- Workflow engines: Temporal, Airflow, Prefect, Step Functions, Camunda
- Status columns with CHECK constraints limiting valid values
- Event handlers triggered on state entry/exit
- State history tables recording every transition with timestamp and actor

### Confidence

- **high** — explicit state machine library or workflow engine with defined states, transitions, and guards
- **medium** — status field with transition validation logic but no formal state machine
- **low** — status field updated directly without transition validation

---
description: Write-Behind architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [data]
---
# Write-Behind

## Recognition

How to identify this pattern in code.

### Signatures

- Writes go to cache first, then asynchronously flushed to the backing store
- Write-through variant: synchronous write to both cache and store
- Cache warming or preloading on startup
- Write coalescing: multiple writes to the same key batched into a single store write
- Async flush workers, write buffers, or dirty-flag tracking on cached entries
- Configuration for flush intervals, batch sizes, or write-behind delay
- Libraries: Hazelcast write-behind, Redis with async persistence, NCache

### Confidence

- **high** -- writes target cache with explicit async flush to backing store and coalescing logic
- **medium** -- write-through with synchronous dual-write to cache and database
- **low** -- application writes to an in-memory buffer that periodically syncs to storage

## Architecture

Look for cache as the primary write target with deferred or synchronous propagation to the persistent store.

### Review Checklist

- Data durability guarantees are documented (what happens if cache crashes before flush)
- Flush failures are retried with backoff and dead-letter handling
- Write ordering is preserved when coalescing (last-write-wins or merge strategy is explicit)
- Cache and backing store consistency is monitored (drift detection)
- Startup handles cache warming from the backing store before accepting writes

### Anti-patterns

- No durability guarantee: cache is sole copy and data is lost on crash
- Unbounded write-behind buffer that grows until memory is exhausted
- Flush errors silently dropped, leading to permanent data loss
- Write-behind delay so long that reads from the backing store return stale data

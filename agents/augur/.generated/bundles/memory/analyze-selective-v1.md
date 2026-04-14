# Augur Analyze Bundle — Selective v1

## Shared analyze workflow

1. Resolve mode and scope (full, incremental, or skip).
2. Start from the prepared deterministic artifacts for this run: `$RUN/blast.json` and `$RUN/facts/`.
3. Use deterministic evidence, including `facts/concept-evidence.json`, to decide what deserves attention.
4. Interpret that evidence semantically.
5. Widen into source files only where the prepared artifacts leave ambiguity or show a larger boundary.
6. Build the architectural model, derive failure modes/debt, and write atlas/stories.

Deterministic detector evidence establishes what is likely present in the codebase. Semantic memory is used to interpret and evaluate that evidence, not to replace it.

This bundle includes the ontology and semantic summaries, not the full semantic catalog. Begin with the prepared run artifacts, then read full semantic definitions only for the most relevant concepts before final interpretation.

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

## Framework summaries

- **FastAPI** (`fastapi`) — FastAPI is an async Python web API framework centered on typed request/response models, declarative routing, and dependency injection.

## Concept summaries

- **Abstract Factory** (`abstract-factory`) — Family of related objects created through a factory interface
- **Active Record** (`active-record`) — Model classes with instance methods `save()`, `delete()`, `update()`
- **Actor Model** (`actor-model`) — Message passing between isolated actors with no shared mutable state
- **Adapter** (`adapter`) — Classes named `*Adapter`, `*Gateway`, `*Wrapper`
- **Aggregate Root** (`aggregate`) — `AggregateRoot` or `AggregateBase` base class / mixin
- **Anemic Domain Model** (`anemic-domain-model`) — Model or entity classes containing only getters and setters with no behavior or business logic methods
- **Anti-Corruption Layer** (`anti-corruption-layer`) — `*Translator`, `*Mapper`, `*Adapter` classes at integration boundaries
- **API Gateway** (`api-gateway`) — Kong, Envoy, NGINX Ingress, or Traefik as the gateway runtime
- **API Key Authentication** (`api-key-auth`) — `X-API-Key` header extraction in middleware or gateway configuration
- **Abstract Syntax Tree (AST)** (`ast`) — Tree node classes or enums representing language constructs (`IfExpr`, `BinOp`, `FnDecl`, `LetStmt`)
- **Audit Logging** (`audit-logging`) — `AuditLog` model, table, or collection storing who-did-what-when
- **Backpressure** (`backpressure`) — `Flowable` or `Observable` with `onBackpressure*` operators (RxJava)
- **Batch Loader (N+1 Prevention)** (`batch-loader`) — DataLoader pattern: batched key collection with deferred resolution (`new DataLoader(batchFn)`)
- **Batch Processing** (`batch-processing`) — Cron-scheduled jobs processing accumulated data
- **Backend for Frontend** (`bff`) — Separate API layers per frontend type: `/api/mobile/*`, `/api/web/*`, `/api/admin/*`
- **Big Ball of Mud** (`big-ball-of-mud`) — No directory structure convention -- files placed arbitrarily without grouping by feature, layer, or domain
- **Block Content** (`block-content`) — `block`, `Block`, `block_type` fields defining typed content units
- **Bloom Filter** (`bloom-filter`) — Probabilistic membership test: `add()` and `might_contain()` (or `__contains__` returning possible matches)
- **Blue-Green Deployment** (`blue-green`) — Two identical environments labeled `blue`/`green` or `active`/`standby`
- **Boolean Blindness** (`boolean-blindness`) — Functions taking 3 or more boolean parameters: `create(true, false, true)`
- **Breaking Changes** (`breaking-changes`) — Removed fields from API responses without a deprecation period
- **Bridge** (`bridge`) — Separating abstraction from implementation so both can vary independently
- **Builder** (`builder`) — Classes ending in `Builder`, `Config`, or `Options` with fluent setter methods
- **Bulkhead** (`bulkhead`) — `resilience4j-bulkhead` dependency and `@Bulkhead` annotations (Java)
- **Busy Waiting** (`busy-waiting`) — `while True: sleep(0.1); if condition: break` polling loops
- **Cache-Aside** (`cache-aside`) — Check cache first, on miss load from source, then populate cache before returning
- **Cache Stampede Prevention** (`cache-stampede-prevention`) — Lock-based cache population (only one thread/process recomputes on miss)
- **Callback Hell** (`callback-hell`) — Deeply nested callbacks (4+ levels of indentation from nested anonymous functions)
- **Canary Release** (`canary`) — Traffic splitting with explicit percentages (e.g., 5%, 10%, 50%, 100%)
- **Cargo Cult Programming** (`cargo-cult`) — Design patterns applied without understanding their purpose (e.g., a Factory that only ever creates one type, a Singleton wrapping a stateless utility, a Repository layered over another Repository)
- **Catalog** (`catalog`) — `Product`, `Variant`, `SKU` model classes with relationships between them
- **Cell-Based** (`cell-based`) — Multiple identical deployments serving different customer segments or regions
- **Chain of Responsibility** (`chain-of-responsibility`) — Middleware chains: `app.use()`, `next()` calls, ordered handler lists
- **Change Data Capture (CDC)** (`change-data-capture`) — Database log tailing (WAL, binlog, oplog)
- **Chatty API** (`chatty-api`) — Client making 10+ sequential API calls to assemble a single view or page
- **Choreography** (`choreography`) — Event-based service communication without a central orchestrator or saga coordinator
- **Circuit Breaker** (`circuit-breaker`) — `resilience4j` with `CircuitBreaker` and `CircuitBreakerConfig` classes (Java)
- **Circular Dependency** (`circular-dependency`) — Module A imports module B which imports module A (direct cycle)
- **Claim Check** (`claim-check`) — Large payload stored in blob or object storage before sending a message
- **Command** (`command`) — Classes with `execute()`, `run()`, `do()` methods, often paired with `undo()` or `rollback()`
- **Competing Consumers** (`competing-consumers`) — Multiple consumers reading from the same queue or topic partition
- **Component Slot** (`component-slot`) — `children` prop for content projection and `Slot` component from Radix/headless libraries (React)
- **Component Architecture** (`component`) — Self-contained UI components with props/state, composed into a tree
- **Composite** (`composite`) — Tree structures where leaves and containers share the same interface
- **Configuration Management** (`config-management`) — 12-factor config via environment variables (`os.environ`, `process.env`, `std::env`)
- **Configuration Sprawl** (`config-sprawl`) — Config values spread across environment variables AND yaml files AND code constants AND database settings
- **Connection Pooling** (`connection-pooling`) — `pool_size`, `max_connections`, `min_idle` configuration parameters
- **Content/Protocol Negotiation** (`content-negotiation`) — `Accept` and `Content-Type` HTTP headers used for format selection
- **Contract Testing** (`contract-testing`) — Pact files (`.json` contracts) in a `pacts/` or `contracts/` directory
- **Conversation Thread** (`conversation-thread`) — `Message`, `Thread`, `Conversation` model classes with parent-child relationships
- **Copy-Paste Programming** (`copy-paste-programming`) — Identical or near-identical code blocks in multiple files
- **Correlation ID** (`correlation-id`) — Request ID generation: `uuid4()`, `ulid()`, `nanoid()` for unique correlation IDs
- **CORS (Cross-Origin Resource Sharing)** (`cors`) — `Access-Control-Allow-Origin` response headers
- **CQRS** (`cqrs`) — Separate `CommandHandler` and `QueryHandler` classes or interfaces
- **Data Mapper** (`data-mapper`) — Separate mapper classes that transfer data between domain objects and database rows
- **Data Pipeline** (`data-pipeline`) — ETL/ELT patterns: extract → transform → load
- **Database Migration** (`database-migration`) — Versioned migration files: numbered or timestamped scripts (`001_create_users.sql`, `V2__add_index.sql`)
- **Domain-Driven Design (DDD)** (`ddd`) — `Entity`, `ValueObject`, or `AggregateRoot` base classes or interfaces in domain layer
- **Dead Letter Queue** (`dead-letter`) — DLQ or DLX (dead-letter exchange) configuration on queues or topics
- **Deadlock** (`deadlock`) — Multiple locks acquired in inconsistent order across different code paths
- **Decorator/Wrapper** (`decorator`) — Object wrapping another object while exposing the same interface
- **Deep Nesting** (`deep-nesting`) — 5 or more levels of if/for/try nesting
- **Dependency Injection** (`dependency-injection`) — Constructor parameters that are interfaces/protocols, not concrete classes
- **Distributed Lock** (`distributed-lock`) — Lock acquire/release calls with TTL (time-to-live) for automatic expiry
- **Distributed Monolith** (`distributed-monolith`) — Microservices sharing a single database (multiple services with connection strings to the same DB)
- **Distributed Tracing** (`distributed-tracing`) — OpenTelemetry SDK: `opentelemetry-api`, `opentelemetry-sdk`, `@opentelemetry/api`, `go.opentelemetry.io/otel`
- **Dual Writes** (`dual-writes`) — Writing to a database AND publishing to a message broker in the same method without a transactional outbox
- **Entity-Component-System (ECS)** (`entity-component-system`) — Entities represented as plain integer IDs or opaque handles, not class hierarchies
- **Environment Parity Gap** (`environment-parity-gap`) — Different databases in dev vs prod: SQLite in development, PostgreSQL in production
- **Error Boundary** (`error-boundary`) — `ErrorBoundary` class component with `componentDidCatch` and `getDerivedStateFromError` (React)
- **Error Code Returns** (`error-code-returns`) — Functions returning -1, 0, or 1 to indicate success/failure instead of using exceptions or Result types
- **ETL/ELT** (`etl`) — Airflow `DAG` definitions with operators (`PythonOperator`, `BashOperator`, `SqlOperator`)
- **Event-Carried State Transfer (Fat Events)** (`event-carried-state`) — Events containing full entity state, not just identifiers
- **Event-Driven Architecture** (`event-driven`) — Domain events as first-class objects with type, timestamp, and payload
- **Event Log** (`event-log`) — Append-only tables or streams — inserts only, no updates or deletes
- **Event Notification (Thin Events)** (`event-notification`) — Events containing only ID, type, and timestamp -- no entity payload
- **Event Sourcing** (`event-sourcing`) — `EventStore` or `EventStream` classes managing append-only event persistence
- **A/B Experiment Framework** (`experiment-framework`) — Experiment assignment logic: users bucketed into control/treatment variants
- **Facade** (`facade`) — Classes named `*Facade` or `*Gateway` or `*Client` that wrap complex subsystems
- **Factory** (`factory`) — Classes ending in `Factory`, `Creator`, or `Provider`
- **Failure Cascade** (`failure-cascade`) — Component A depends on B depends on C — if C fails, B fails, then A fails
- **Fan-In** (`fan-in`) — `Promise.all()` or `asyncio.gather()` collecting parallel results
- **Fan-Out** (`fan-out`) — One Kafka/RabbitMQ/SNS producer with multiple consumer groups on the same topic
- **Feature Envy** (`feature-envy`) — Methods that access more fields from another class than from their own class
- **Feature Flag/Toggle** (`feature-flag`) — Conditional checks like `if feature_enabled("X")`, `is_feature_on()`, `hasFeature()`
- **Feature Store** (`feature-store`) — Centralized feature repository with feature definitions and metadata
- **Fire and Forget** (`fire-and-forget`) — Publishing messages with no delivery guarantee or acknowledgment check
- **Test Fixture / Data Builder** (`fixture-builder`) — `*Factory` or `*Builder` classes in test directories (`UserFactory`, `OrderBuilder`)
- **Flaky Tests** (`flaky-tests`) — `sleep()` or `time.sleep()` in test code to wait for conditions
- **Flux/Redux (Unidirectional Data Flow)** (`flux`) — Central store holding application state as a single source of truth
- **Flyweight** (`flyweight`) — Shared immutable objects to reduce memory footprint
- **Form Binding** (`form-binding`) — Controlled inputs with `value` + `onChange` handlers managing state (React)
- **Future/Promise** (`future-promise`) — Deferred computation represented as a handle to a result not yet available
- **Game Loop** (`game-loop`) — Main loop structure: `while running: process_input(); update(dt); render()`
- **Gateway-Backends** (`gateway-backends`) — API gateway (Kong, AWS API Gateway, Traefik, nginx) routing to multiple services
- **GitOps** (`gitops`) — Git repository as the single source of truth for infrastructure and application state
- **God Endpoint** (`god-endpoint`) — Single API route handling multiple unrelated operations via an `action` or `type` parameter
- **God Object/Class** (`god-object`) — Classes exceeding 1000 lines of code
- **Golden Hammer** (`golden-hammer`) — One framework or library used for everything (e.g., Celery for async tasks, cron scheduling, messaging, and orchestration simultaneously)
- **Graceful Degradation** (`graceful-degradation`) — Fallback responses returned when a dependency is down or slow
- **Graph** (`graph`) — `Graph`, `DiGraph`, `DAG` class definitions or type aliases
- **GraphQL** (`graphql`) — Schema definition language files with `type Query {}`, `type Mutation {}`, `type Subscription {}`
- **gRPC/RPC** (`grpc`) — `.proto` files with `service` and `rpc` declarations
- **Hardcoded Credentials** (`hardcoded-credentials`) — `password = "..."` or `passwd = "..."` assigned as string literals
- **Hardcoded URLs** (`hardcoded-urls`) — `http://localhost:8080` or `http://127.0.0.1` in production code paths
- **Health Check** (`health-check`) — Endpoints: `/health`, `/healthz`, `/ready`, `/readyz`, `/live`, `/livez`, `/status`
- **Hexagonal (Ports & Adapters)** (`hexagonal`) — `ports/` and `adapters/` directory structure separating interface definitions from implementations
- **Hidden Side Effects** (`hidden-side-effects`) — Functions that look pure (no indication in name or signature) but modify global state or module-level variables
- **Hydration** (`hydration`) — `dehydrate(queryClient)` and `HydrationBoundary` or `Hydrate` component (TanStack Query)
- **Ice Cream Cone** (`ice-cream-cone`) — `test/e2e` or `tests/integration` directory much larger than `test/unit` or `tests/unit`
- **Idempotent Consumer** (`idempotent-consumer`) — Message ID deduplication before processing
- **Immutable Infrastructure** (`immutable-infra`) — Dockerfiles building application images with all dependencies baked in
- **Inbox** (`inbox`) — Database table named `inbox`, `processed_messages`, or `received_events`
- **Inconsistent Naming** (`inconsistent-naming`) — Mix of camelCase and snake_case in the same file or module
- **Infrastructure as Code** (`infrastructure-as-code`) — Declarative infrastructure definitions in version-controlled files
- **Input Validation** (`input-validation`) — Schema validation at the API boundary before business logic executes
- **Insecure Deserialization** (`insecure-deserialization`) — `pickle.loads()` on untrusted or network-received input
- **Intermediate Representation (IR)** (`intermediate-representation`) — Lowered representation sitting between the AST (source) and final output (machine code, bytecode, target language)
- **Iterator** (`iterator`) — Python: `__iter__()` / `__next__()` protocol, `yield` generators, `itertools` usage
- **Key-Value** (`key-value-model`) — Redis, Memcached, DynamoDB, etcd, or Consul as primary data store
- **Lava Flow (Dead Code)** (`lava-flow`) — Commented-out code blocks left in the source
- **Layered** (`layered`) — Directory structure: `presentation/` or `api/` → `service/` or `domain/` → `repository/` or `data/`
- **Lazy Loading** (`lazy-loading`) — `React.lazy(() => import(...))` and `<Suspense>` wrapper (React)
- **Leader Election** (`leader-election`) — Leader/follower role assignment logic with election protocol
- **Leaky Abstraction** (`leaky-abstraction`) — Implementation details in interface signatures (SQL fragments in repository method names, HTTP headers in domain object fields, file paths in service interfaces)
- **Ledger** (`ledger`) — `debit` and `credit` columns or fields appearing in the same table/model
- **Lexer/Parser** (`lexer-parser`) — Two-phase processing: tokenization (lexer/scanner) followed by parsing into a tree structure
- **Log and Throw** (`log-and-throw`) — `logger.error(e); raise e` or `catch(e) { log(e); throw e; }` in the same block
- **Log Spam** (`log-spam`) — `logger.info()` or `logger.debug()` inside `for`/`while` loops
- **Long Polling** (`long-polling`) — Client sends HTTP request, server holds it open until data is available or timeout expires
- **Long Transactions** (`long-transactions`) — Database transaction wrapping HTTP calls or external API calls
- **LRU Cache** (`lru-cache`) — `@lru_cache` or `functools.lru_cache` decorator in Python
- **Magic Numbers/Strings** (`magic-numbers`) — Hardcoded numeric values with no explanation (`if count > 42`)
- **MapReduce** (`mapreduce`) — Parallel map phase followed by a reduce/aggregate phase
- **Materialized View** (`materialized-view`) — `CREATE MATERIALIZED VIEW` in database migrations or schema definitions
- **Mediator** (`mediator`) — Central coordinator class: `Mediator`, `EventBus`, `Dispatcher`, `Hub`, `Broker`
- **Memento** (`memento`) — `save_state()` / `restore_state()` method pairs
- **Memory Leak** (`memory-leak`) — Event listeners never removed (`addEventListener` without corresponding `removeEventListener`)
- **Message Queue** (`message-queue`) — Point-to-point messaging: each message consumed by exactly one consumer
- **Metric Cardinality Explosion** (`metric-cardinality-explosion`) — User ID, request ID, URL path, or email used as Prometheus label values
- **Metrics Instrumentation** (`metrics-instrumentation`) — Prometheus client usage: `prometheus_client` (Python), `prom-client` (Node), `prometheus/client_golang` (Go)
- **Micro-Frontend** (`micro-frontend`) — Independently deployable frontend modules owned by separate teams
- **Microservices** (`microservices`) — Multiple independently deployable services, each with its own Dockerfile or build target
- **Middleware** (`middleware`) — `app.use()` with function signature `(req, res, next)` (Express)
- **Misleading Names** (`misleading-names`) — `get*` methods that mutate state or have side effects (database writes, cache invalidation, HTTP calls)
- **Missing Log Context** (`missing-log-context`) — Log messages with no request ID or correlation ID attached
- **Model Registry** (`model-registry`) — Versioned model storage with unique model names and version numbers
- **Modular Monolith** (`modular-monolith`) — Single deployable unit with internal module boundaries (`modules/`, `packages/`, `domains/`)
- **Monad/Railway-Oriented Programming** (`monad`) — `bind()`, `flatMap()`, `>>=`, `and_then()`, `chain()` methods for monadic composition
- **Mutual TLS** (`mtls`) — Client certificate configuration (`--cert`, `--key` flags, `tls.Certificate` structs)
- **Multi-Tenant** (`multi-tenant`) — `tenant_id`, `organization_id`, `org_id` columns present on most or all database tables
- **Model-View-Controller** (`mvc`) — Separate `models/`, `views/`, `controllers/` directories or class suffixes (`UserController`, `UserModel`)
- **Model-View-ViewModel** (`mvvm`) — ViewModel classes exposing observable properties that the view binds to
- **N+1 Queries** (`n-plus-one`) — Database query inside a loop (`for item in items: item.related.load()`)
- **Null Object** (`null-object`) — No-op implementations of interfaces: `NullLogger`, `NoOpCache`, `NullMetrics`
- **OAuth2/OpenID Connect** (`oauth-oidc`) — Authorization code flow endpoints: `/authorize`, `/token`, `/callback`
- **Object Pool** (`object-pool`) — Methods named `acquire()`, `release()`, `borrow()`, `return_to_pool()`, `get()`, `put()`
- **Observer** (`observer`) — Methods named `subscribe()`, `on()`, `addListener()`, `register()`, `attach()`
- **Optimistic Locking** (`optimistic-locking`) — `version` column or field on database entities, incremented on each update
- **Optimistic Update** (`optimistic-update`) — `onMutate` / `onError` / `onSettled` callbacks in TanStack Query mutations
- **Outbox** (`outbox`) — Database table named `outbox`, `outbox_events`, or `pending_events`
- **Over/Under-Fetching** (`over-under-fetching`) — Returning entire database rows or full object graphs when the caller needs one or two fields (over-fetching)
- **Pagination** (`pagination`) — `limit`/`offset` query parameters or `LIMIT ? OFFSET ?` in SQL queries
- **Pipeline/Filter** (`pipeline-filter`) — Ordered chain of transform functions where output of one feeds input of the next
- **Pipeline Stages** (`pipeline-stages`) — Components named `Stage`, `Step`, `Phase`, `Processor` with sequential numbering or ordering
- **Plugin Host** (`plugin-host`) — Plugin interface or abstract base class that extensions implement
- **Plugin Architecture** (`plugin`) — Plugin registry classes or dictionaries mapping plugin names to implementations
- **Pokemon Exception** (`pokemon-exception`) — `except:` or `except Exception:` catching everything in Python
- **Polling** (`polling-flow`) — `setInterval()` or `setTimeout()` with recurring fetch/check
- **Premature Optimization** (`premature-optimization`) — Caching layer introduced before measuring whether latency is actually a problem
- **Primitive Obsession** (`primitive-obsession`) — Email addresses, phone numbers, money amounts, or URLs represented as plain strings
- **Producer-Consumer** (`producer-consumer`) — Shared queue or buffer between producer and consumer threads/processes
- **Prop Drilling** (`prop-drilling`) — Same prop passed through 5+ component layers unchanged
- **Property Graph** (`property-graph`) — `Node` and `Edge` or `Vertex` and `Relationship` class definitions with property maps
- **Property-Based Testing** (`property-testing`) — `@given` decorator with `hypothesis` strategies in Python tests
- **Prototype** (`prototype`) — Creating objects by cloning existing instances rather than constructing from scratch
- **Proxy** (`proxy`) — Class implementing the same interface as the real object but controlling access to it
- **Publish-Subscribe** (`pub-sub`) — Topic or channel-based messaging: `publish(topic, message)`, `subscribe(topic, handler)`
- **Race Condition** (`race-condition`) — Unsynchronized read-modify-write on shared mutable state (`count = count + 1` without a lock)
- **Rate Limiting/Throttling** (`rate-limiting`) — Request counters per client/IP with time window tracking
- **Role-Based Access Control** (`rbac`) — Role definitions with associated permissions (`admin`, `editor`, `viewer`)
- **Reactive Store** (`reactive-store`) — `zustand` with `create()`, selector hooks, `set`/`get` state functions (React)
- **Reactor/Event Loop** (`reactor`) — Single-threaded event loop dispatching I/O events to registered handlers
- **Read-Through Cache** (`read-through`) — Cache that loads from the backing source automatically on miss (vs cache-aside where the caller loads)
- **Read-Write Lock** (`read-write-lock`) — Separate lock acquisition for read vs write operations
- **Refresh-Ahead Cache** (`refresh-ahead`) — Proactive cache refresh before TTL expiry
- **Registry** (`registry-model`) — Entity classes with `status`/`state` fields and defined lifecycle transitions
- **Reinventing the Wheel** (`reinventing-the-wheel`) — Custom JSON parser when `json.loads()` or equivalent exists
- **Repository** (`repository`) — Classes ending in `Repository` or `Repo` (e.g., `UserRepository`, `OrderRepo`)
- **Request Path** (`request-path`) — HTTP route handler calling a service layer which calls a repository/data layer
- **Request-Reply** (`request-reply`) — Correlation ID linking request messages to their responses
- **REST API** (`rest`) — HTTP methods mapped to CRUD operations (GET=read, POST=create, PUT/PATCH=update, DELETE=delete)
- **Result/Either Type** (`result-type`) — `Result<T, E>`, `Ok()`, `Err()` in Rust code
- **Retry with Backoff** (`retry`) — `tenacity` imports and decorators in Python (`@retry`, `wait_exponential`, `stop_after_attempt`)
- **Ring Buffer** (`ring-buffer`) — Fixed-size circular buffer with head and tail pointers (or read/write indices)
- **Route Guard** (`route-guard`) — `clientLoader` or `loader` returning `redirect()` based on auth state (React Router)
- **Router** (`router`) — `react-router-dom` with `BrowserRouter`, `Routes`, `Route`, `useNavigate`, `useParams` (React)
- **Rule Engine** (`rule-engine`) — `Rule`, `Condition`, `Action` class hierarchy or interfaces
- **Saga Orchestrator** (`saga-orchestrator`) — Central coordinator class managing a sequence of saga steps (`SagaOrchestrator`, `SagaManager`, `SagaCoordinator`)
- **Saga** (`saga`) — `Temporal` workflow definitions with activity sequences and compensation logic
- **Scatter-Gather** (`scatter-gather`) — Parallel HTTP calls to multiple backends with results merged
- **Cron/Scheduler** (`scheduler`) — Cron expressions in config files or decorators (`"0 */5 * * *"`, `@crontab`)
- **Schema-on-Read** (`schema-on-read`) — JSON blobs stored in database columns without a defined schema
- **Search Index** (`search-index`) — Elasticsearch client usage: `Elasticsearch()`, `client.index()`, `client.search()`, index mappings
- **Secret Management** (`secret-management`) — Vault integration (`hashicorp/vault`, `vault` CLI, `VAULT_ADDR`)
- **Select Star** (`select-star`) — `SELECT *` in production queries or raw SQL strings
- **Server Prefetch** (`server-prefetch`) — `loader` functions with `queryClient.prefetchQuery` and `dehydrate` (React Router + TanStack Query)
- **Server-Sent Events (SSE)** (`server-sent-events`) — `Content-Type: text/event-stream` response header
- **Serverless / FaaS** (`serverless`) — Lambda handler functions: `handler(event, context)`, `exports.handler`, `def lambda_handler`
- **Service Discovery** (`service-discovery`) — Service registry with registration and lookup APIs
- **Service Manager** (`service-manager`) — Signal handlers registering for graceful shutdown (`signal.signal(signal.SIGTERM, handler)`)
- **Service Mesh** (`service-mesh`) — Sidecar proxy containers: Envoy, Linkerd-proxy, Consul Connect proxy
- **Session-Based Authentication** (`session-auth`) — Server-side session store (Redis, database table, in-memory map)
- **Sharding** (`sharding`) — Shard key selection and shard ID derivation logic
- **Shotgun Surgery** (`shotgun-surgery`) — One logical change requires editing 10+ files across different modules or packages
- **Side Effect Hook** (`side-effect-hook`) — `useEffect` and `useLayoutEffect` with dependency arrays and cleanup returns (React)
- **Sidecar Mesh** (`sidecar-mesh`) — Istio, Linkerd, or Consul Connect service mesh
- **Sidecar** (`sidecar`) — Multi-container pod specs with two or more containers in a single pod definition
- **Singleton** (`singleton`) — Class variable `_instance`, `__instance`, or `instance`
- **Snapshot Testing** (`snapshot-testing`) — `toMatchSnapshot()`, `toMatchInlineSnapshot()` in Jest tests
- **Snowflake Server** (`snowflake-server`) — Hand-configured servers with no Infrastructure as Code (IaC) backing them
- **Social Graph** (`social-graph`) — `follow`, `Follow`, `follower`, `following` models or table names
- **Soft Delete** (`soft-delete`) — `deleted_at` timestamp column that is NULL for active records and set on deletion
- **Spaghetti Code** (`spaghetti-code`) — Conditionals nested 5+ levels deep (if/else/if/else/try/if)
- **Spatial Partitioning** (`spatial-partitioning`) — Classes named `QuadTree`, `Octree`, `SpatialHash`, `RTree`, `BVH`, `Grid`
- **Spatial** (`spatial`) — `geometry`, `Point`, `Polygon`, `LineString` type definitions or column types
- **Specification Pattern** (`specification`) — `is_satisfied_by()` or `isSatisfiedBy()` methods on business rule objects
- **SQL Injection** (`sql-injection`) — String concatenation in SQL queries (`f"SELECT * FROM users WHERE id = {id}"`)
- **State Machine** (`state-machine`) — Enum or constants defining states: `State`, `Status`, `Phase`
- **Strangler Fig** (`strangler-fig`) — Routing layer splitting traffic between old and new systems: reverse proxy rules, feature flags, path-based routing
- **Strategy** (`strategy`) — Interface/protocol with a single method implemented by multiple concrete classes
- **Stream-to-Store** (`stream-to-store`) — Kafka consumer imports (`kafka.KafkaConsumer`, `confluent_kafka.Consumer`)
- **Streaming** (`streaming-flow`) — Kafka consumer with continuous poll loop (not batch/cron)
- **Stringly Typed** (`stringly-typed`) — Strings used where enums or types should be (`status = "active"` instead of an enum)
- **Structured Logging** (`structured-logging`) — JSON log output format instead of plain text lines
- **Subscription** (`subscription`) — `Subscription`, `Plan`, `BillingCycle` model classes with status and period fields
- **Suspense Boundary** (`suspense-boundary`) — `<Suspense fallback={...}>` (React)
- **Swallowed Exception** (`swallowed-exception`) — Empty `except:` or `catch {}` blocks with no logging, metrics, or re-raise
- **Sync-in-Async** (`sync-in-async`) — `requests.get()` or `requests.post()` inside an `async def` function
- **Template Method** (`template-method`) — Abstract base class with a concrete method calling abstract/hook methods in sequence
- **Temporal Coupling** (`temporal-coupling`) — Methods that must be called in a specific order (`init()` before `run()`, `connect()` before `query()`) but nothing in the type system enforces it
- **Tenant Isolation** (`tenant-isolation`) — Tenant ID in request context: `request.tenant_id`, `ctx.tenant`, `TenantContext.current()`
- **Tenant-Aware Routing** (`tenant-routing`) — Subdomain extraction: parsing tenant from `{tenant}.example.com`, `Host` header splitting
- **Tensor** (`tensor`) — `torch.Tensor`, `torch.tensor()`, `torch.zeros()`, `torch.randn()` tensor creation
- **Test Doubles (Mock/Stub/Fake/Spy)** (`test-doubles`) — `unittest.mock`, `MagicMock`, `patch()` decorators in Python test files
- **Test Pollution** (`test-pollution`) — Tests modifying global state (module-level variables, class attributes, singletons)
- **Tick-Based Simulation** (`tick-simulation`) — `tick()` or `step()` method called at a fixed rate with a tick counter
- **Tight Coupling** (`tight-coupling`) — Concrete class references everywhere with no interfaces or protocols between components
- **Time Series** (`time-series`) — `timestamp` as the primary or leading index column in tables or collections
- **Timeout** (`timeout`) — `timeout=` parameter on HTTP, gRPC, or database calls
- **Token-Based Authentication (JWT)** (`token-auth`) — `Authorization: Bearer <token>` header extraction in middleware
- **Train Wreck** (`train-wreck`) — `a.getB().getC().getD().doThing()` -- long method chains navigating through an object graph
- **Training Pipeline** (`training-pipeline`) — Sequential stages: data loading, preprocessing, training, evaluation, model export
- **Trie (Prefix Tree)** (`trie`) — Node-per-character tree structure with children stored in a dict or fixed-size array
- **Unbounded Growth** (`unbounded-growth`) — Lists or dicts that grow without bound (`cache = {}` with no eviction)
- **Unit of Work** (`unit-of-work`) — Transaction management wrapping multiple repository operations
- **Value Object** (`value-object`) — `@dataclass(frozen=True)` or `@attr.s(frozen=True)` in Python
- **Versioned Document** (`versioned-document`) — `revision`, `version`, or `version_number` fields tracking document iterations
- **Visitor** (`visitor`) — `accept(visitor)` method on element/node classes
- **Webhook** (`webhook`) — Callback URL registration endpoints (`POST /webhooks`, `webhook_url` config field)
- **WebSocket** (`websocket`) — `ws://` or `wss://` URL schemes in connection strings or config
- **Worker/Thread Pool** (`worker-pool`) — Fixed pool of workers processing tasks submitted to a shared queue
- **Workflow Engine** (`workflow-engine`) — `@task`, `@dag`, `@workflow`, `@step` decorators defining workflow steps
- **Workflow / State Machine** (`workflow-state-machine`) — State enum or constants: `PENDING`, `APPROVED`, `REJECTED`, `COMPLETED`, `CANCELLED`
- **Write-Behind** (`write-behind`) — Writes go to cache first, then asynchronously flushed to the backing store

## Selective-read rule

When detector evidence is ambiguous, high-signal, or central to the architecture, read the full semantic definition from `memory/catalog/frameworks/<name>/framework.md` or `memory/catalog/concepts/<name>.md` before final interpretation.

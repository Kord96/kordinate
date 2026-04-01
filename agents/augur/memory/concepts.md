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
| Microservices | Multiple independently deployable services | [view](concepts/microservices/concept.md) |
| Modular monolith | Single deployment with internal module boundaries | [view](concepts/modular-monolith/concept.md) |
| Serverless / FaaS | Stateless request handlers triggered by events | [view](concepts/serverless/concept.md) |

### Structural

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Hexagonal (ports & adapters) | Decouples business logic from infrastructure via ports and adapters | [view](concepts/hexagonal/concept.md) |
| Domain-driven design (DDD) | Organizes code around bounded contexts and domain aggregates | [view](concepts/ddd/concept.md) |
| Plugin architecture | Extensible core with pluggable components registered at startup | [view](concepts/plugin/concept.md) |
| Aggregate root | Root entity controlling access to child entities within a consistency boundary | [view](concepts/aggregate/concept.md) |
| Value object | Immutable objects compared by value, not identity | [view](concepts/value-object/concept.md) |
| Anti-corruption layer | Boundary translation between systems or bounded contexts | [view](concepts/anti-corruption-layer/concept.md) |
| Decorator / Wrapper | Adding behavior to an object without modifying its interface | [view](concepts/decorator/concept.md) |
| Proxy | Controls access to an object through the same interface | [view](concepts/proxy/concept.md) |
| Adapter | Translates one interface to another | [view](concepts/adapter/concept.md) |
| Facade | Simplified interface to a complex subsystem | [view](concepts/facade/concept.md) |
| Pipeline / Filter | Ordered chain of transform functions processing data through stages | [view](concepts/pipeline-filter/concept.md) |
| Composite | Tree structures where leaves and containers share the same interface | [view](concepts/composite/concept.md) |
| Flyweight | Shared immutable objects to reduce memory | [view](concepts/flyweight/concept.md) |
| Bridge | Separating abstraction from implementation so both can vary | [view](concepts/bridge/concept.md) |

### Data

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Stream-to-store | Kafka consumer that writes to a local store via buffered flushes | [view](concepts/stream-to-store/concept.md) |
| ETL/ELT | Batch extract-transform-load for periodic data processing | [view](concepts/etl/concept.md) |
| Event sourcing | Append-only event log as the source of truth | [view](concepts/event-sourcing/concept.md) |
| CQRS | Separate models for reading and writing data | [view](concepts/cqrs/concept.md) |
| MapReduce | Parallel map phase + reduce/aggregate phase over distributed data | [view](concepts/mapreduce/concept.md) |
| Idempotent consumer | Message deduplication before processing | [view](concepts/idempotent-consumer/concept.md) |
| Change data capture | Database log tailing to capture changes as events | [view](concepts/change-data-capture/concept.md) |
| Ring buffer | Fixed-size circular buffer with wrap-around | [view](concepts/ring-buffer/concept.md) |
| Bloom filter | Probabilistic membership test with bit array | [view](concepts/bloom-filter/concept.md) |
| Trie | Prefix tree for autocomplete and routing | [view](concepts/trie/concept.md) |

### Integration

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Saga | Distributed transactions via local transactions with compensating actions | [view](concepts/saga/concept.md) |
| Choreography | Services react to events independently with no central coordinator | [view](concepts/choreography/concept.md) |
| API gateway | Centralized entry point for routing, auth, and rate limiting | [view](concepts/api-gateway/concept.md) |
| Webhook | Callback URL registration with event delivery | [view](concepts/webhook/concept.md) |
| Claim check | Large payload stored externally, message contains reference | [view](concepts/claim-check/concept.md) |

### Resilience

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Circuit breaker | Stops calling a failing dependency after a threshold, allows recovery | [view](concepts/circuit-breaker/concept.md) |
| Bulkhead | Isolates components so one failure doesn't exhaust shared resources | [view](concepts/bulkhead/concept.md) |
| Retry with backoff | Retries failed operations with exponential delay and jitter | [view](concepts/retry/concept.md) |
| Backpressure | Flow control when a producer is faster than its consumer | [view](concepts/backpressure/concept.md) |
| Timeout | Explicit timeout on every external call | [view](concepts/timeout/concept.md) |
| Graceful degradation | Fallback responses when dependencies are down | [view](concepts/graceful-degradation/concept.md) |

### Lifecycle

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Service manager | Manages service startup, shutdown, health reporting, and graceful degradation | [view](concepts/service-manager/concept.md) |
| Sidecar | Auxiliary container handling cross-cutting concerns alongside the main workload | [view](concepts/sidecar/concept.md) |
| Scheduler / Cron | Time-based triggers for periodic task execution | [view](concepts/scheduler/concept.md) |
| Workflow engine | DAG-based step/task orchestration with dependencies | [view](concepts/workflow-engine/concept.md) |
| Strangler fig | Incremental replacement of legacy system | [view](concepts/strangler-fig/concept.md) |
| Database migration | Versioned schema changes with up/down rollback | [view](concepts/database-migration/concept.md) |

### Creational

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Factory | Object creation via factory methods/classes returning interfaces | [view](concepts/factory/concept.md) |
| Abstract factory | Family of related objects created through a factory interface | [view](concepts/abstract-factory/concept.md) |
| Builder | Step-by-step object construction with fluent method chaining | [view](concepts/builder/concept.md) |
| Singleton | Single instance shared across the application | [view](concepts/singleton/concept.md) |
| Object pool | Reusable object pool with acquire/release lifecycle | [view](concepts/object-pool/concept.md) |
| Dependency injection | Inversion of control via constructor/setter injection | [view](concepts/dependency-injection/concept.md) |
| Prototype | Creating objects by cloning existing instances | [view](concepts/prototype/concept.md) |

### Behavioral

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Strategy | Interchangeable algorithms behind a common interface | [view](concepts/strategy/concept.md) |
| Observer | Event emitter with subscribe/notify for decoupled communication | [view](concepts/observer/concept.md) |
| Command | Encapsulated operations as objects with execute/undo | [view](concepts/command/concept.md) |
| State machine | Explicit states with defined transitions and lifecycle hooks | [view](concepts/state-machine/concept.md) |
| Chain of responsibility | Ordered handler chain where each can process or pass the request | [view](concepts/chain-of-responsibility/concept.md) |
| Mediator | Central coordinator for component communication | [view](concepts/mediator/concept.md) |
| Template method | Abstract base with overridable hook methods | [view](concepts/template-method/concept.md) |
| Visitor | Double-dispatch traversal with accept/visit methods | [view](concepts/visitor/concept.md) |
| Iterator | Lazy sequential access to elements without exposing internals | [view](concepts/iterator/concept.md) |
| Specification | Composable boolean predicates for business rules | [view](concepts/specification/concept.md) |
| Monad / Railway | Chained operations that short-circuit on failure via bind/flatMap | [view](concepts/monad/concept.md) |
| Memento | Capturing and restoring object state (undo/redo) | [view](concepts/memento/concept.md) |

### Concurrency

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Actor model | Isolated actors communicating via asynchronous message passing | [view](concepts/actor-model/concept.md) |
| Producer-consumer | Shared queue/buffer between producing and consuming threads | [view](concepts/producer-consumer/concept.md) |
| Worker pool | Fixed pool of workers processing tasks from a queue | [view](concepts/worker-pool/concept.md) |
| Reactor / Event loop | Single-threaded event loop with non-blocking I/O | [view](concepts/reactor/concept.md) |
| Read-write lock | Separate locks for concurrent reads and exclusive writes | [view](concepts/read-write-lock/concept.md) |
| Future / Promise | Deferred computation with async result containers | [view](concepts/future-promise/concept.md) |

### Frontend

| Pattern | Description | Reference |
|---------|-------------|-----------|
| MVC | Model-View-Controller separation of concerns | [view](concepts/mvc/concept.md) |
| MVVM | Model-View-ViewModel with observable data binding | [view](concepts/mvvm/concept.md) |
| Component | Self-contained UI components with props/state composition | [view](concepts/component/concept.md) |
| Flux / Redux | Unidirectional data flow with store, actions, and reducers | [view](concepts/flux/concept.md) |
| Micro-frontend | Independently deployable frontend modules | [view](concepts/micro-frontend/concept.md) |

### Storage

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Repository | Abstraction over data access with CRUD operations | [view](concepts/repository/concept.md) |
| Unit of work | Transaction management wrapping multiple operations | [view](concepts/unit-of-work/concept.md) |
| Active record | Model instances with built-in persistence methods | [view](concepts/active-record/concept.md) |
| Data mapper | Separate mapper transferring data between objects and database | [view](concepts/data-mapper/concept.md) |
| Cache-aside | Check cache first, load from source on miss | [view](concepts/cache-aside/concept.md) |
| Read-through | Cache that loads from source on miss automatically | [view](concepts/read-through/concept.md) |
| Refresh-ahead | Proactive cache refresh before TTL expiry | [view](concepts/refresh-ahead/concept.md) |
| Write-behind | Writes go to cache first, async flush to backing store | [view](concepts/write-behind/concept.md) |
| Cache stampede prevention | Lock-based or probabilistic cache population to prevent thundering herd | [view](concepts/cache-stampede-prevention/concept.md) |
| LRU cache | Bounded cache with least-recently-used eviction | [view](concepts/lru-cache/concept.md) |
| Sharding | Data partitioned across nodes by shard key | [view](concepts/sharding/concept.md) |
| Optimistic locking | Version field for conflict detection on write | [view](concepts/optimistic-locking/concept.md) |
| Soft delete | Logical deletion with timestamp/flag instead of physical removal | [view](concepts/soft-delete/concept.md) |
| Materialized view | Pre-computed query results stored as table/cache | [view](concepts/materialized-view/concept.md) |
| Batch loader | N+1 prevention via batched queries | [view](concepts/batch-loader/concept.md) |
| Pagination | Cursor or offset-based result windowing | [view](concepts/pagination/concept.md) |

### Messaging

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Publish-subscribe | Topic-based fan-out messaging to multiple subscribers | [view](concepts/pub-sub/concept.md) |
| Message queue | Point-to-point messaging with each message consumed once | [view](concepts/message-queue/concept.md) |
| Dead letter queue | Failed message routing with retry tracking | [view](concepts/dead-letter/concept.md) |
| Competing consumers | Multiple consumers on the same queue for load balancing | [view](concepts/competing-consumers/concept.md) |
| Request-reply | RPC over message broker with correlation IDs | [view](concepts/request-reply/concept.md) |
| Event-driven architecture | Domain events as first-class objects flowing through an event bus | [view](concepts/event-driven/concept.md) |
| Outbox | Events written to DB in same transaction, published by separate process | [view](concepts/outbox/concept.md) |
| Event notification | Thin events containing only ID + type, consumer calls back for data | [view](concepts/event-notification/concept.md) |
| Event-carried state | Fat events containing full entity state for replication | [view](concepts/event-carried-state/concept.md) |

### Deployment

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Blue-green | Two identical environments with traffic switching | [view](concepts/blue-green/concept.md) |
| Canary | Gradual traffic splitting between stable and new versions | [view](concepts/canary/concept.md) |
| Feature flag | Runtime feature toggles for conditional functionality | [view](concepts/feature-flag/concept.md) |
| GitOps | Git repo as source of truth with reconciliation loops | [view](concepts/gitops/concept.md) |
| Immutable infrastructure | Replace-not-patch, image-based deployment | [view](concepts/immutable-infra/concept.md) |

### Security

| Pattern | Description | Reference |
|---------|-------------|-----------|
| OAuth2 / OIDC | Authorization code flow with token-based access | [view](concepts/oauth-oidc/concept.md) |
| RBAC | Role-based access control with role-permission mapping | [view](concepts/rbac/concept.md) |
| Rate limiting | Request throttling with token bucket or sliding window | [view](concepts/rate-limiting/concept.md) |
| Secret management | Vault/KMS-based credential storage, never hardcoded | [view](concepts/secret-management/concept.md) |
| Session auth | Session-based authentication with server-side session store | [view](concepts/session-auth/concept.md) |
| Token auth (JWT) | Stateless token-based authentication with Bearer tokens | [view](concepts/token-auth/concept.md) |
| Mutual TLS | Client certificate authentication for service-to-service | [view](concepts/mtls/concept.md) |
| API key auth | API key validation for programmatic access | [view](concepts/api-key-auth/concept.md) |
| Audit logging | Immutable log of who-did-what-when for compliance | [view](concepts/audit-logging/concept.md) |
| Input validation | Schema validation and sanitization at API boundary | [view](concepts/input-validation/concept.md) |
| CORS | Cross-origin resource sharing configuration | [view](concepts/cors/concept.md) |
| Tenant isolation | Tenant-scoped data access (DB/schema/row-level) | [view](concepts/tenant-isolation/concept.md) |
| Tenant routing | Tenant-aware request routing and connection switching | [view](concepts/tenant-routing/concept.md) |

### API

| Pattern | Description | Reference |
|---------|-------------|-----------|
| REST | Resource-based HTTP API with standard methods and status codes | [view](concepts/rest/concept.md) |
| GraphQL | Schema-driven query language with single endpoint | [view](concepts/graphql/concept.md) |
| gRPC | Protocol buffer-based RPC with generated stubs | [view](concepts/grpc/concept.md) |
| BFF | Backend for Frontend — API layer tailored per client type | [view](concepts/bff/concept.md) |
| Content negotiation | Format selection via Accept/Content-Type headers | [view](concepts/content-negotiation/concept.md) |

### Distributed

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Service mesh | Sidecar proxy layer for service-to-service communication | [view](concepts/service-mesh/concept.md) |
| Leader election | Single leader coordination with lease-based failover | [view](concepts/leader-election/concept.md) |
| Distributed lock | Cross-node mutual exclusion with TTL | [view](concepts/distributed-lock/concept.md) |
| Health check | Liveness/readiness probes with dependency health aggregation | [view](concepts/health-check/concept.md) |
| Correlation ID | Request ID propagation for distributed tracing | [view](concepts/correlation-id/concept.md) |
| Service discovery | Registry-based or DNS-based service endpoint resolution | [view](concepts/service-discovery/concept.md) |

### Testing

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Test doubles | Mock, stub, fake, and spy implementations for isolation | [view](concepts/test-doubles/concept.md) |
| Contract testing | Consumer-driven contracts verified against providers | [view](concepts/contract-testing/concept.md) |
| Property testing | Generator-based input with invariant assertions | [view](concepts/property-testing/concept.md) |
| Fixture builder | Test data factories and builder helpers | [view](concepts/fixture-builder/concept.md) |
| Snapshot testing | Output comparison against stored snapshots | [view](concepts/snapshot-testing/concept.md) |

### Error Handling

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Result / Either type | Errors as values, not exceptions — with map/bind composition | [view](concepts/result-type/concept.md) |
| Null object | No-op implementations replacing null checks | [view](concepts/null-object/concept.md) |

### Infrastructure

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Configuration management | 12-factor config with env vars and hierarchical overrides | [view](concepts/config-management/concept.md) |
| Infrastructure as Code | Declarative infra definitions (Terraform, Pulumi, CloudFormation) | [view](concepts/infrastructure-as-code/concept.md) |
| Connection pooling | Reusable connection pools for databases and HTTP | [view](concepts/connection-pooling/concept.md) |

### Networking

| Pattern | Description | Reference |
|---------|-------------|-----------|
| WebSocket | Persistent bidirectional connection | [view](concepts/websocket/concept.md) |
| Server-sent events | One-way server push via HTTP streaming | [view](concepts/server-sent-events/concept.md) |
| Long polling | Client holds request until server has data | [view](concepts/long-polling/concept.md) |

### Observability

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Structured logging | JSON log output with key-value fields | [view](concepts/structured-logging/concept.md) |
| Metrics instrumentation | Prometheus client usage for counters, gauges, histograms | [view](concepts/metrics-instrumentation/concept.md) |
| Distributed tracing | OpenTelemetry SDK with span context propagation | [view](concepts/distributed-tracing/concept.md) |

### Realtime

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Entity-component-system | Entities as IDs, components as data, systems operating on queries | [view](concepts/entity-component-system/concept.md) |
| Game loop | Fixed timestep update loop with input/update/render phases | [view](concepts/game-loop/concept.md) |
| Spatial partitioning | Quadtree, octree, or spatial hash for neighbor queries | [view](concepts/spatial-partitioning/concept.md) |
| Tick simulation | Discrete time steps with deterministic updates | [view](concepts/tick-simulation/concept.md) |

### ML

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Feature store | Centralized feature repository with online/offline serving | [view](concepts/feature-store/concept.md) |
| Model registry | Versioned model storage with stage transitions | [view](concepts/model-registry/concept.md) |
| Training pipeline | Data-to-model stages with experiment tracking | [view](concepts/training-pipeline/concept.md) |
| Experiment framework | A/B testing with variant bucketing and metric collection | [view](concepts/experiment-framework/concept.md) |

### Compiler

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Lexer / Parser | Tokenization + parsing into structured representation | [view](concepts/lexer-parser/concept.md) |
| Abstract syntax tree | Tree node hierarchy representing language constructs | [view](concepts/ast/concept.md) |
| Intermediate representation | Lowered representation for optimization passes | [view](concepts/intermediate-representation/concept.md) |

## Libraries

Patterns with kordinate library implementations: stream-to-store (stoik), service-manager (orchestrator).
Implementation files are co-located in the pattern directory.

## Domain Model

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Ledger | Double-entry ledger — debits, credits, balanced transactions | [view](concepts/ledger/concept.md) |
| Property graph | Typed nodes and edges with properties and traversal queries | [view](concepts/property-graph/concept.md) |
| Search index | Inverted index, analyzers, ranked full-text retrieval | [view](concepts/search-index/concept.md) |
| Time-series | Timestamp-indexed append-only data with retention and downsampling | [view](concepts/time-series/concept.md) |
| Versioned document | Immutable revisions, diffs, conflict resolution | [view](concepts/versioned-document/concept.md) |
| Tensor | Multi-dimensional array computation with GPU dispatch | [view](concepts/tensor/concept.md) |
| Spatial | Geographic/geometric data with spatial indexes | [view](concepts/spatial/concept.md) |
| Rule engine | Declarative business rules, policy evaluation, decision tables | [view](concepts/rule-engine/concept.md) |
| Multi-tenant | Tenant-scoped data isolation and configuration | [view](concepts/multi-tenant/concept.md) |
| Subscription | Recurring billing, plan management, usage metering | [view](concepts/subscription/concept.md) |
| Block content | Structured rich text with nested typed blocks | [view](concepts/block-content/concept.md) |
| Catalog | Product/variant/SKU hierarchy with inventory | [view](concepts/catalog/concept.md) |
| Social graph | Follow/connection relationships with feed generation | [view](concepts/social-graph/concept.md) |
| Conversation thread | Threaded messaging with real-time delivery | [view](concepts/conversation-thread/concept.md) |
| Graph | Generic graph model — DAGs, traversal, cycle detection | [view](concepts/graph/concept.md) |

---
description: Index of recognized architectural patterns by category
curated: true
scope: global
preloaded: designer
---
# Patterns Index

156 patterns across 20 categories. Each pattern has recognition signatures for code scanning.

## Categories

| Category | Scope | Key Question |
|----------|-------|--------------|
| architecture | Overall system structure | What is the deployment and service topology? |
| structural | How code is organized within a service | Is business logic decoupled from infrastructure? |
| data | How data flows and is stored | Is data moving correctly through the system? |
| integration | How services communicate with each other | Are cross-service interactions safe and traceable? |
| resilience | How the system handles failure | What happens when a dependency goes down? |
| lifecycle | How a single service starts, runs, and stops | Does the service boot and shut down cleanly? |
| creational | How objects are created | Are object creation concerns separated from business logic? |
| behavioral | How objects communicate | Are responsibilities clearly distributed? |
| concurrency | How parallel work is managed | Is concurrent access safe and efficient? |
| frontend | How user interfaces are structured | Is UI state and rendering well-organized? |
| storage | How data is persisted and accessed | Is persistence abstracted from domain logic? |
| messaging | How messages flow between components | Are messages delivered reliably and processed correctly? |
| deployment | How software is released | Are releases safe, reversible, and observable? |
| security | How access and trust are managed | Are authentication and authorization enforced correctly? |
| api | How services expose interfaces | Are APIs consistent, versioned, and well-defined? |
| distributed | How distributed systems coordinate | Are coordination and consistency handled correctly? |
| testing | How code is verified | Are tests isolated, deterministic, and covering the right boundaries? |
| error-handling | How failures are represented | Are errors values or exceptions, and is handling explicit? |
| infrastructure | How environments are provisioned | Is infrastructure reproducible and secrets secure? |
| networking | How network communication is handled | Are protocols and connections managed correctly? |
| observability | How systems are monitored | Are logs, metrics, and traces structured and useful? |
| realtime | How real-time systems are structured | Is simulation deterministic and performant? |
| ml | How ML systems are built | Are models versioned, features managed, and experiments tracked? |
| compiler | How language tooling is structured | Are parsing, representation, and transformation well-separated? |

## Patterns

### Architecture

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Microservices | Multiple independently deployable services | [view](patterns/microservices/concept.md) |
| Modular monolith | Single deployment with internal module boundaries | [view](patterns/modular-monolith/concept.md) |
| Serverless / FaaS | Stateless request handlers triggered by events | [view](patterns/serverless/concept.md) |

### Structural

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Hexagonal (ports & adapters) | Decouples business logic from infrastructure via ports and adapters | [view](patterns/hexagonal/concept.md) |
| Domain-driven design (DDD) | Organizes code around bounded contexts and domain aggregates | [view](patterns/ddd/concept.md) |
| Plugin architecture | Extensible core with pluggable components registered at startup | [view](patterns/plugin/concept.md) |
| Aggregate root | Root entity controlling access to child entities within a consistency boundary | [view](patterns/aggregate/concept.md) |
| Value object | Immutable objects compared by value, not identity | [view](patterns/value-object/concept.md) |
| Anti-corruption layer | Boundary translation between systems or bounded contexts | [view](patterns/anti-corruption-layer/concept.md) |
| Decorator / Wrapper | Adding behavior to an object without modifying its interface | [view](patterns/decorator/concept.md) |
| Proxy | Controls access to an object through the same interface | [view](patterns/proxy/concept.md) |
| Adapter / Facade | Translates one interface to another or simplifies a complex subsystem | [view](patterns/adapter/concept.md) |
| Pipeline / Filter | Ordered chain of transform functions processing data through stages | [view](patterns/pipeline-filter/concept.md) |
| Composite | Tree structures where leaves and containers share the same interface | [view](patterns/composite/concept.md) |
| Flyweight | Shared immutable objects to reduce memory | [view](patterns/flyweight/concept.md) |
| Bridge | Separating abstraction from implementation so both can vary | [view](patterns/bridge/concept.md) |

### Data

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Stream-to-store | Kafka consumer that writes to a local store via buffered flushes | [view](patterns/stream-to-store/concept.md) |
| ETL/ELT | Batch extract-transform-load for periodic data processing | [view](patterns/etl/concept.md) |
| Event sourcing | Append-only event log as the source of truth | [view](patterns/event-sourcing/concept.md) |
| CQRS | Separate models for reading and writing data | [view](patterns/cqrs/concept.md) |
| MapReduce | Parallel map phase + reduce/aggregate phase over distributed data | [view](patterns/mapreduce/concept.md) |
| Idempotent consumer | Message deduplication before processing | [view](patterns/idempotent-consumer/concept.md) |
| Change data capture | Database log tailing to capture changes as events | [view](patterns/change-data-capture/concept.md) |
| Ring buffer | Fixed-size circular buffer with wrap-around | [view](patterns/ring-buffer/concept.md) |
| Bloom filter | Probabilistic membership test with bit array | [view](patterns/bloom-filter/concept.md) |
| Trie | Prefix tree for autocomplete and routing | [view](patterns/trie/concept.md) |

### Integration

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Saga | Distributed transactions via local transactions with compensating actions | [view](patterns/saga/concept.md) |
| Choreography | Services react to events independently with no central coordinator | [view](patterns/choreography/concept.md) |
| API gateway | Centralized entry point for routing, auth, and rate limiting | [view](patterns/api-gateway/concept.md) |
| Webhook | Callback URL registration with event delivery | [view](patterns/webhook/concept.md) |
| Claim check | Large payload stored externally, message contains reference | [view](patterns/claim-check/concept.md) |

### Resilience

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Circuit breaker | Stops calling a failing dependency after a threshold, allows recovery | [view](patterns/circuit-breaker/concept.md) |
| Bulkhead | Isolates components so one failure doesn't exhaust shared resources | [view](patterns/bulkhead/concept.md) |
| Retry with backoff | Retries failed operations with exponential delay and jitter | [view](patterns/retry/concept.md) |
| Backpressure | Flow control when a producer is faster than its consumer | [view](patterns/backpressure/concept.md) |
| Timeout | Explicit timeout on every external call | [view](patterns/timeout/concept.md) |
| Graceful degradation | Fallback responses when dependencies are down | [view](patterns/graceful-degradation/concept.md) |

### Lifecycle

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Service manager | Manages service startup, shutdown, health reporting, and graceful degradation | [view](patterns/service-manager/concept.md) |
| Sidecar | Auxiliary container handling cross-cutting concerns alongside the main workload | [view](patterns/sidecar/concept.md) |
| Scheduler / Cron | Time-based triggers for periodic task execution | [view](patterns/scheduler/concept.md) |
| Workflow engine | DAG-based step/task orchestration with dependencies | [view](patterns/workflow-engine/concept.md) |
| Strangler fig | Incremental replacement of legacy system | [view](patterns/strangler-fig/concept.md) |
| Database migration | Versioned schema changes with up/down rollback | [view](patterns/database-migration/concept.md) |

### Creational

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Factory | Object creation via factory methods/classes returning interfaces | [view](patterns/factory/concept.md) |
| Abstract factory | Family of related objects created through a factory interface | [view](patterns/abstract-factory/concept.md) |
| Builder | Step-by-step object construction with fluent method chaining | [view](patterns/builder/concept.md) |
| Singleton | Single instance shared across the application | [view](patterns/singleton/concept.md) |
| Object pool | Reusable object pool with acquire/release lifecycle | [view](patterns/object-pool/concept.md) |
| Dependency injection | Inversion of control via constructor/setter injection | [view](patterns/dependency-injection/concept.md) |
| Prototype | Creating objects by cloning existing instances | [view](patterns/prototype/concept.md) |

### Behavioral

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Strategy | Interchangeable algorithms behind a common interface | [view](patterns/strategy/concept.md) |
| Observer | Event emitter with subscribe/notify for decoupled communication | [view](patterns/observer/concept.md) |
| Command | Encapsulated operations as objects with execute/undo | [view](patterns/command/concept.md) |
| State machine | Explicit states with defined transitions and lifecycle hooks | [view](patterns/state-machine/concept.md) |
| Chain of responsibility | Ordered handler chain where each can process or pass the request | [view](patterns/chain-of-responsibility/concept.md) |
| Mediator | Central coordinator for component communication | [view](patterns/mediator/concept.md) |
| Template method | Abstract base with overridable hook methods | [view](patterns/template-method/concept.md) |
| Visitor | Double-dispatch traversal with accept/visit methods | [view](patterns/visitor/concept.md) |
| Iterator | Lazy sequential access to elements without exposing internals | [view](patterns/iterator/concept.md) |
| Specification | Composable boolean predicates for business rules | [view](patterns/specification/concept.md) |
| Monad / Railway | Chained operations that short-circuit on failure via bind/flatMap | [view](patterns/monad/concept.md) |
| Memento | Capturing and restoring object state (undo/redo) | [view](patterns/memento/concept.md) |

### Concurrency

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Actor model | Isolated actors communicating via asynchronous message passing | [view](patterns/actor-model/concept.md) |
| Producer-consumer | Shared queue/buffer between producing and consuming threads | [view](patterns/producer-consumer/concept.md) |
| Worker pool | Fixed pool of workers processing tasks from a queue | [view](patterns/worker-pool/concept.md) |
| Reactor / Event loop | Single-threaded event loop with non-blocking I/O | [view](patterns/reactor/concept.md) |
| Read-write lock | Separate locks for concurrent reads and exclusive writes | [view](patterns/read-write-lock/concept.md) |
| Future / Promise | Deferred computation with async result containers | [view](patterns/future-promise/concept.md) |

### Frontend

| Pattern | Description | Reference |
|---------|-------------|-----------|
| MVC | Model-View-Controller separation of concerns | [view](patterns/mvc/concept.md) |
| MVVM | Model-View-ViewModel with observable data binding | [view](patterns/mvvm/concept.md) |
| Component | Self-contained UI components with props/state composition | [view](patterns/component/concept.md) |
| Flux / Redux | Unidirectional data flow with store, actions, and reducers | [view](patterns/flux/concept.md) |
| Micro-frontend | Independently deployable frontend modules | [view](patterns/micro-frontend/concept.md) |

### Storage

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Repository | Abstraction over data access with CRUD operations | [view](patterns/repository/concept.md) |
| Unit of work | Transaction management wrapping multiple operations | [view](patterns/unit-of-work/concept.md) |
| Active record | Model instances with built-in persistence methods | [view](patterns/active-record/concept.md) |
| Data mapper | Separate mapper transferring data between objects and database | [view](patterns/data-mapper/concept.md) |
| Cache-aside | Check cache first, load from source on miss | [view](patterns/cache-aside/concept.md) |
| Read-through | Cache that loads from source on miss automatically | [view](patterns/read-through/concept.md) |
| Refresh-ahead | Proactive cache refresh before TTL expiry | [view](patterns/refresh-ahead/concept.md) |
| Write-behind | Writes go to cache first, async flush to backing store | [view](patterns/write-behind/concept.md) |
| Cache stampede prevention | Lock-based or probabilistic cache population to prevent thundering herd | [view](patterns/cache-stampede-prevention/concept.md) |
| LRU cache | Bounded cache with least-recently-used eviction | [view](patterns/lru-cache/concept.md) |
| Sharding | Data partitioned across nodes by shard key | [view](patterns/sharding/concept.md) |
| Optimistic locking | Version field for conflict detection on write | [view](patterns/optimistic-locking/concept.md) |
| Soft delete | Logical deletion with timestamp/flag instead of physical removal | [view](patterns/soft-delete/concept.md) |
| Materialized view | Pre-computed query results stored as table/cache | [view](patterns/materialized-view/concept.md) |
| Batch loader | N+1 prevention via batched queries | [view](patterns/batch-loader/concept.md) |
| Pagination | Cursor or offset-based result windowing | [view](patterns/pagination/concept.md) |

### Messaging

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Publish-subscribe | Topic-based fan-out messaging to multiple subscribers | [view](patterns/pub-sub/concept.md) |
| Message queue | Point-to-point messaging with each message consumed once | [view](patterns/message-queue/concept.md) |
| Dead letter queue | Failed message routing with retry tracking | [view](patterns/dead-letter/concept.md) |
| Competing consumers | Multiple consumers on the same queue for load balancing | [view](patterns/competing-consumers/concept.md) |
| Request-reply | RPC over message broker with correlation IDs | [view](patterns/request-reply/concept.md) |
| Event-driven architecture | Domain events as first-class objects flowing through an event bus | [view](patterns/event-driven/concept.md) |
| Outbox | Events written to DB in same transaction, published by separate process | [view](patterns/outbox/concept.md) |
| Inbox | Idempotent message processing with deduplication | [view](patterns/inbox/concept.md) |
| Saga orchestrator | Central coordinator managing saga steps with compensation | [view](patterns/saga-orchestrator/concept.md) |
| Event notification | Thin events containing only ID + type, consumer calls back for data | [view](patterns/event-notification/concept.md) |
| Event-carried state | Fat events containing full entity state for replication | [view](patterns/event-carried-state/concept.md) |

### Deployment

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Blue-green | Two identical environments with traffic switching | [view](patterns/blue-green/concept.md) |
| Canary | Gradual traffic splitting between stable and new versions | [view](patterns/canary/concept.md) |
| Feature flag | Runtime feature toggles for conditional functionality | [view](patterns/feature-flag/concept.md) |
| GitOps | Git repo as source of truth with reconciliation loops | [view](patterns/gitops/concept.md) |
| Immutable infrastructure | Replace-not-patch, image-based deployment | [view](patterns/immutable-infra/concept.md) |

### Security

| Pattern | Description | Reference |
|---------|-------------|-----------|
| OAuth2 / OIDC | Authorization code flow with token-based access | [view](patterns/oauth-oidc/concept.md) |
| RBAC | Role-based access control with role-permission mapping | [view](patterns/rbac/concept.md) |
| Rate limiting | Request throttling with token bucket or sliding window | [view](patterns/rate-limiting/concept.md) |
| Secret management | Vault/KMS-based credential storage, never hardcoded | [view](patterns/secret-management/concept.md) |
| Session auth | Session-based authentication with server-side session store | [view](patterns/session-auth/concept.md) |
| Token auth (JWT) | Stateless token-based authentication with Bearer tokens | [view](patterns/token-auth/concept.md) |
| Mutual TLS | Client certificate authentication for service-to-service | [view](patterns/mtls/concept.md) |
| API key auth | API key validation for programmatic access | [view](patterns/api-key-auth/concept.md) |
| Audit logging | Immutable log of who-did-what-when for compliance | [view](patterns/audit-logging/concept.md) |
| Input validation | Schema validation and sanitization at API boundary | [view](patterns/input-validation/concept.md) |
| CORS | Cross-origin resource sharing configuration | [view](patterns/cors/concept.md) |
| Tenant isolation | Tenant-scoped data access (DB/schema/row-level) | [view](patterns/tenant-isolation/concept.md) |
| Tenant routing | Tenant-aware request routing and connection switching | [view](patterns/tenant-routing/concept.md) |

### API

| Pattern | Description | Reference |
|---------|-------------|-----------|
| REST | Resource-based HTTP API with standard methods and status codes | [view](patterns/rest/concept.md) |
| GraphQL | Schema-driven query language with single endpoint | [view](patterns/graphql/concept.md) |
| gRPC | Protocol buffer-based RPC with generated stubs | [view](patterns/grpc/concept.md) |
| BFF | Backend for Frontend — API layer tailored per client type | [view](patterns/bff/concept.md) |
| Content negotiation | Format selection via Accept/Content-Type headers | [view](patterns/content-negotiation/concept.md) |

### Distributed

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Service mesh | Sidecar proxy layer for service-to-service communication | [view](patterns/service-mesh/concept.md) |
| Leader election | Single leader coordination with lease-based failover | [view](patterns/leader-election/concept.md) |
| Distributed lock | Cross-node mutual exclusion with TTL | [view](patterns/distributed-lock/concept.md) |
| Health check | Liveness/readiness probes with dependency health aggregation | [view](patterns/health-check/concept.md) |
| Correlation ID | Request ID propagation for distributed tracing | [view](patterns/correlation-id/concept.md) |
| Service discovery | Registry-based or DNS-based service endpoint resolution | [view](patterns/service-discovery/concept.md) |

### Testing

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Test doubles | Mock, stub, fake, and spy implementations for isolation | [view](patterns/test-doubles/concept.md) |
| Contract testing | Consumer-driven contracts verified against providers | [view](patterns/contract-testing/concept.md) |
| Property testing | Generator-based input with invariant assertions | [view](patterns/property-testing/concept.md) |
| Fixture builder | Test data factories and builder helpers | [view](patterns/fixture-builder/concept.md) |
| Snapshot testing | Output comparison against stored snapshots | [view](patterns/snapshot-testing/concept.md) |

### Error Handling

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Result / Either type | Errors as values, not exceptions — with map/bind composition | [view](patterns/result-type/concept.md) |
| Null object | No-op implementations replacing null checks | [view](patterns/null-object/concept.md) |

### Infrastructure

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Configuration management | 12-factor config with env vars and hierarchical overrides | [view](patterns/config-management/concept.md) |
| Infrastructure as Code | Declarative infra definitions (Terraform, Pulumi, CloudFormation) | [view](patterns/infrastructure-as-code/concept.md) |
| Connection pooling | Reusable connection pools for databases and HTTP | [view](patterns/connection-pooling/concept.md) |

### Networking

| Pattern | Description | Reference |
|---------|-------------|-----------|
| WebSocket | Persistent bidirectional connection | [view](patterns/websocket/concept.md) |
| Server-sent events | One-way server push via HTTP streaming | [view](patterns/server-sent-events/concept.md) |
| Long polling | Client holds request until server has data | [view](patterns/long-polling/concept.md) |

### Observability

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Structured logging | JSON log output with key-value fields | [view](patterns/structured-logging/concept.md) |
| Metrics instrumentation | Prometheus client usage for counters, gauges, histograms | [view](patterns/metrics-instrumentation/concept.md) |
| Distributed tracing | OpenTelemetry SDK with span context propagation | [view](patterns/distributed-tracing/concept.md) |

### Realtime

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Entity-component-system | Entities as IDs, components as data, systems operating on queries | [view](patterns/entity-component-system/concept.md) |
| Game loop | Fixed timestep update loop with input/update/render phases | [view](patterns/game-loop/concept.md) |
| Spatial partitioning | Quadtree, octree, or spatial hash for neighbor queries | [view](patterns/spatial-partitioning/concept.md) |
| Tick simulation | Discrete time steps with deterministic updates | [view](patterns/tick-simulation/concept.md) |

### ML

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Feature store | Centralized feature repository with online/offline serving | [view](patterns/feature-store/concept.md) |
| Model registry | Versioned model storage with stage transitions | [view](patterns/model-registry/concept.md) |
| Training pipeline | Data-to-model stages with experiment tracking | [view](patterns/training-pipeline/concept.md) |
| Experiment framework | A/B testing with variant bucketing and metric collection | [view](patterns/experiment-framework/concept.md) |

### Compiler

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Lexer / Parser | Tokenization + parsing into structured representation | [view](patterns/lexer-parser/concept.md) |
| Abstract syntax tree | Tree node hierarchy representing language constructs | [view](patterns/ast/concept.md) |
| Intermediate representation | Lowered representation for optimization passes | [view](patterns/intermediate-representation/concept.md) |

## Libraries

Patterns with kordinate library implementations: stream-to-store (stoik), service-manager (orchestrator).
Implementation files are co-located in the pattern directory.

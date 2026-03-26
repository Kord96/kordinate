---
description: Index of recognized architectural patterns by category
curated: true
scope: global
preloaded: designer
---
# Patterns Index

157 patterns across 20 categories. Each pattern has recognition signatures for code scanning.

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
| Microservices | Multiple independently deployable services | [view](patterns/microservices/pattern.md) |
| Modular monolith | Single deployment with internal module boundaries | [view](patterns/modular-monolith/pattern.md) |
| Serverless / FaaS | Stateless request handlers triggered by events | [view](patterns/serverless/pattern.md) |

### Structural

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Hexagonal (ports & adapters) | Decouples business logic from infrastructure via ports and adapters | [view](patterns/hexagonal/pattern.md) |
| Domain-driven design (DDD) | Organizes code around bounded contexts and domain aggregates | [view](patterns/ddd/pattern.md) |
| Plugin architecture | Extensible core with pluggable components registered at startup | [view](patterns/plugin/pattern.md) |
| Aggregate root | Root entity controlling access to child entities within a consistency boundary | [view](patterns/aggregate/pattern.md) |
| Value object | Immutable objects compared by value, not identity | [view](patterns/value-object/pattern.md) |
| Anti-corruption layer | Boundary translation between systems or bounded contexts | [view](patterns/anti-corruption-layer/pattern.md) |
| Decorator / Wrapper | Adding behavior to an object without modifying its interface | [view](patterns/decorator/pattern.md) |
| Proxy | Controls access to an object through the same interface | [view](patterns/proxy/pattern.md) |
| Adapter | Translates one interface to another | [view](patterns/adapter/pattern.md) |
| Facade | Simplified interface to a complex subsystem | [view](patterns/facade/pattern.md) |
| Pipeline / Filter | Ordered chain of transform functions processing data through stages | [view](patterns/pipeline-filter/pattern.md) |
| Composite | Tree structures where leaves and containers share the same interface | [view](patterns/composite/pattern.md) |
| Flyweight | Shared immutable objects to reduce memory | [view](patterns/flyweight/pattern.md) |
| Bridge | Separating abstraction from implementation so both can vary | [view](patterns/bridge/pattern.md) |

### Data

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Stream-to-store | Kafka consumer that writes to a local store via buffered flushes | [view](patterns/stream-to-store/pattern.md) |
| ETL/ELT | Batch extract-transform-load for periodic data processing | [view](patterns/etl/pattern.md) |
| Event sourcing | Append-only event log as the source of truth | [view](patterns/event-sourcing/pattern.md) |
| CQRS | Separate models for reading and writing data | [view](patterns/cqrs/pattern.md) |
| MapReduce | Parallel map phase + reduce/aggregate phase over distributed data | [view](patterns/mapreduce/pattern.md) |
| Idempotent consumer | Message deduplication before processing | [view](patterns/idempotent-consumer/pattern.md) |
| Change data capture | Database log tailing to capture changes as events | [view](patterns/change-data-capture/pattern.md) |
| Ring buffer | Fixed-size circular buffer with wrap-around | [view](patterns/ring-buffer/pattern.md) |
| Bloom filter | Probabilistic membership test with bit array | [view](patterns/bloom-filter/pattern.md) |
| Trie | Prefix tree for autocomplete and routing | [view](patterns/trie/pattern.md) |

### Integration

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Saga | Distributed transactions via local transactions with compensating actions | [view](patterns/saga/pattern.md) |
| Choreography | Services react to events independently with no central coordinator | [view](patterns/choreography/pattern.md) |
| API gateway | Centralized entry point for routing, auth, and rate limiting | [view](patterns/api-gateway/pattern.md) |
| Webhook | Callback URL registration with event delivery | [view](patterns/webhook/pattern.md) |
| Claim check | Large payload stored externally, message contains reference | [view](patterns/claim-check/pattern.md) |

### Resilience

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Circuit breaker | Stops calling a failing dependency after a threshold, allows recovery | [view](patterns/circuit-breaker/pattern.md) |
| Bulkhead | Isolates components so one failure doesn't exhaust shared resources | [view](patterns/bulkhead/pattern.md) |
| Retry with backoff | Retries failed operations with exponential delay and jitter | [view](patterns/retry/pattern.md) |
| Backpressure | Flow control when a producer is faster than its consumer | [view](patterns/backpressure/pattern.md) |
| Timeout | Explicit timeout on every external call | [view](patterns/timeout/pattern.md) |
| Graceful degradation | Fallback responses when dependencies are down | [view](patterns/graceful-degradation/pattern.md) |

### Lifecycle

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Service manager | Manages service startup, shutdown, health reporting, and graceful degradation | [view](patterns/service-manager/pattern.md) |
| Sidecar | Auxiliary container handling cross-cutting concerns alongside the main workload | [view](patterns/sidecar/pattern.md) |
| Scheduler / Cron | Time-based triggers for periodic task execution | [view](patterns/scheduler/pattern.md) |
| Workflow engine | DAG-based step/task orchestration with dependencies | [view](patterns/workflow-engine/pattern.md) |
| Strangler fig | Incremental replacement of legacy system | [view](patterns/strangler-fig/pattern.md) |
| Database migration | Versioned schema changes with up/down rollback | [view](patterns/database-migration/pattern.md) |

### Creational

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Factory | Object creation via factory methods/classes returning interfaces | [view](patterns/factory/pattern.md) |
| Abstract factory | Family of related objects created through a factory interface | [view](patterns/abstract-factory/pattern.md) |
| Builder | Step-by-step object construction with fluent method chaining | [view](patterns/builder/pattern.md) |
| Singleton | Single instance shared across the application | [view](patterns/singleton/pattern.md) |
| Object pool | Reusable object pool with acquire/release lifecycle | [view](patterns/object-pool/pattern.md) |
| Dependency injection | Inversion of control via constructor/setter injection | [view](patterns/dependency-injection/pattern.md) |
| Prototype | Creating objects by cloning existing instances | [view](patterns/prototype/pattern.md) |

### Behavioral

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Strategy | Interchangeable algorithms behind a common interface | [view](patterns/strategy/pattern.md) |
| Observer | Event emitter with subscribe/notify for decoupled communication | [view](patterns/observer/pattern.md) |
| Command | Encapsulated operations as objects with execute/undo | [view](patterns/command/pattern.md) |
| State machine | Explicit states with defined transitions and lifecycle hooks | [view](patterns/state-machine/pattern.md) |
| Chain of responsibility | Ordered handler chain where each can process or pass the request | [view](patterns/chain-of-responsibility/pattern.md) |
| Mediator | Central coordinator for component communication | [view](patterns/mediator/pattern.md) |
| Template method | Abstract base with overridable hook methods | [view](patterns/template-method/pattern.md) |
| Visitor | Double-dispatch traversal with accept/visit methods | [view](patterns/visitor/pattern.md) |
| Iterator | Lazy sequential access to elements without exposing internals | [view](patterns/iterator/pattern.md) |
| Specification | Composable boolean predicates for business rules | [view](patterns/specification/pattern.md) |
| Monad / Railway | Chained operations that short-circuit on failure via bind/flatMap | [view](patterns/monad/pattern.md) |
| Memento | Capturing and restoring object state (undo/redo) | [view](patterns/memento/pattern.md) |

### Concurrency

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Actor model | Isolated actors communicating via asynchronous message passing | [view](patterns/actor-model/pattern.md) |
| Producer-consumer | Shared queue/buffer between producing and consuming threads | [view](patterns/producer-consumer/pattern.md) |
| Worker pool | Fixed pool of workers processing tasks from a queue | [view](patterns/worker-pool/pattern.md) |
| Reactor / Event loop | Single-threaded event loop with non-blocking I/O | [view](patterns/reactor/pattern.md) |
| Read-write lock | Separate locks for concurrent reads and exclusive writes | [view](patterns/read-write-lock/pattern.md) |
| Future / Promise | Deferred computation with async result containers | [view](patterns/future-promise/pattern.md) |

### Frontend

| Pattern | Description | Reference |
|---------|-------------|-----------|
| MVC | Model-View-Controller separation of concerns | [view](patterns/mvc/pattern.md) |
| MVVM | Model-View-ViewModel with observable data binding | [view](patterns/mvvm/pattern.md) |
| Component | Self-contained UI components with props/state composition | [view](patterns/component/pattern.md) |
| Flux / Redux | Unidirectional data flow with store, actions, and reducers | [view](patterns/flux/pattern.md) |
| Micro-frontend | Independently deployable frontend modules | [view](patterns/micro-frontend/pattern.md) |

### Storage

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Repository | Abstraction over data access with CRUD operations | [view](patterns/repository/pattern.md) |
| Unit of work | Transaction management wrapping multiple operations | [view](patterns/unit-of-work/pattern.md) |
| Active record | Model instances with built-in persistence methods | [view](patterns/active-record/pattern.md) |
| Data mapper | Separate mapper transferring data between objects and database | [view](patterns/data-mapper/pattern.md) |
| Cache-aside | Check cache first, load from source on miss | [view](patterns/cache-aside/pattern.md) |
| Read-through | Cache that loads from source on miss automatically | [view](patterns/read-through/pattern.md) |
| Refresh-ahead | Proactive cache refresh before TTL expiry | [view](patterns/refresh-ahead/pattern.md) |
| Write-behind | Writes go to cache first, async flush to backing store | [view](patterns/write-behind/pattern.md) |
| Cache stampede prevention | Lock-based or probabilistic cache population to prevent thundering herd | [view](patterns/cache-stampede-prevention/pattern.md) |
| LRU cache | Bounded cache with least-recently-used eviction | [view](patterns/lru-cache/pattern.md) |
| Sharding | Data partitioned across nodes by shard key | [view](patterns/sharding/pattern.md) |
| Optimistic locking | Version field for conflict detection on write | [view](patterns/optimistic-locking/pattern.md) |
| Soft delete | Logical deletion with timestamp/flag instead of physical removal | [view](patterns/soft-delete/pattern.md) |
| Materialized view | Pre-computed query results stored as table/cache | [view](patterns/materialized-view/pattern.md) |
| Batch loader | N+1 prevention via batched queries | [view](patterns/batch-loader/pattern.md) |
| Pagination | Cursor or offset-based result windowing | [view](patterns/pagination/pattern.md) |

### Messaging

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Publish-subscribe | Topic-based fan-out messaging to multiple subscribers | [view](patterns/pub-sub/pattern.md) |
| Message queue | Point-to-point messaging with each message consumed once | [view](patterns/message-queue/pattern.md) |
| Dead letter queue | Failed message routing with retry tracking | [view](patterns/dead-letter/pattern.md) |
| Competing consumers | Multiple consumers on the same queue for load balancing | [view](patterns/competing-consumers/pattern.md) |
| Request-reply | RPC over message broker with correlation IDs | [view](patterns/request-reply/pattern.md) |
| Event-driven architecture | Domain events as first-class objects flowing through an event bus | [view](patterns/event-driven/pattern.md) |
| Outbox | Events written to DB in same transaction, published by separate process | [view](patterns/outbox/pattern.md) |
| Inbox | Idempotent message processing with deduplication | [view](patterns/inbox/pattern.md) |
| Saga orchestrator | Central coordinator managing saga steps with compensation | [view](patterns/saga-orchestrator/pattern.md) |
| Event notification | Thin events containing only ID + type, consumer calls back for data | [view](patterns/event-notification/pattern.md) |
| Event-carried state | Fat events containing full entity state for replication | [view](patterns/event-carried-state/pattern.md) |

### Deployment

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Blue-green | Two identical environments with traffic switching | [view](patterns/blue-green/pattern.md) |
| Canary | Gradual traffic splitting between stable and new versions | [view](patterns/canary/pattern.md) |
| Feature flag | Runtime feature toggles for conditional functionality | [view](patterns/feature-flag/pattern.md) |
| GitOps | Git repo as source of truth with reconciliation loops | [view](patterns/gitops/pattern.md) |
| Immutable infrastructure | Replace-not-patch, image-based deployment | [view](patterns/immutable-infra/pattern.md) |

### Security

| Pattern | Description | Reference |
|---------|-------------|-----------|
| OAuth2 / OIDC | Authorization code flow with token-based access | [view](patterns/oauth-oidc/pattern.md) |
| RBAC | Role-based access control with role-permission mapping | [view](patterns/rbac/pattern.md) |
| Rate limiting | Request throttling with token bucket or sliding window | [view](patterns/rate-limiting/pattern.md) |
| Secret management | Vault/KMS-based credential storage, never hardcoded | [view](patterns/secret-management/pattern.md) |
| Session auth | Session-based authentication with server-side session store | [view](patterns/session-auth/pattern.md) |
| Token auth (JWT) | Stateless token-based authentication with Bearer tokens | [view](patterns/token-auth/pattern.md) |
| Mutual TLS | Client certificate authentication for service-to-service | [view](patterns/mtls/pattern.md) |
| API key auth | API key validation for programmatic access | [view](patterns/api-key-auth/pattern.md) |
| Audit logging | Immutable log of who-did-what-when for compliance | [view](patterns/audit-logging/pattern.md) |
| Input validation | Schema validation and sanitization at API boundary | [view](patterns/input-validation/pattern.md) |
| CORS | Cross-origin resource sharing configuration | [view](patterns/cors/pattern.md) |
| Tenant isolation | Tenant-scoped data access (DB/schema/row-level) | [view](patterns/tenant-isolation/pattern.md) |
| Tenant routing | Tenant-aware request routing and connection switching | [view](patterns/tenant-routing/pattern.md) |

### API

| Pattern | Description | Reference |
|---------|-------------|-----------|
| REST | Resource-based HTTP API with standard methods and status codes | [view](patterns/rest/pattern.md) |
| GraphQL | Schema-driven query language with single endpoint | [view](patterns/graphql/pattern.md) |
| gRPC | Protocol buffer-based RPC with generated stubs | [view](patterns/grpc/pattern.md) |
| BFF | Backend for Frontend — API layer tailored per client type | [view](patterns/bff/pattern.md) |
| Content negotiation | Format selection via Accept/Content-Type headers | [view](patterns/content-negotiation/pattern.md) |

### Distributed

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Service mesh | Sidecar proxy layer for service-to-service communication | [view](patterns/service-mesh/pattern.md) |
| Leader election | Single leader coordination with lease-based failover | [view](patterns/leader-election/pattern.md) |
| Distributed lock | Cross-node mutual exclusion with TTL | [view](patterns/distributed-lock/pattern.md) |
| Health check | Liveness/readiness probes with dependency health aggregation | [view](patterns/health-check/pattern.md) |
| Correlation ID | Request ID propagation for distributed tracing | [view](patterns/correlation-id/pattern.md) |
| Service discovery | Registry-based or DNS-based service endpoint resolution | [view](patterns/service-discovery/pattern.md) |

### Testing

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Test doubles | Mock, stub, fake, and spy implementations for isolation | [view](patterns/test-doubles/pattern.md) |
| Contract testing | Consumer-driven contracts verified against providers | [view](patterns/contract-testing/pattern.md) |
| Property testing | Generator-based input with invariant assertions | [view](patterns/property-testing/pattern.md) |
| Fixture builder | Test data factories and builder helpers | [view](patterns/fixture-builder/pattern.md) |
| Snapshot testing | Output comparison against stored snapshots | [view](patterns/snapshot-testing/pattern.md) |

### Error Handling

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Result / Either type | Errors as values, not exceptions — with map/bind composition | [view](patterns/result-type/pattern.md) |
| Null object | No-op implementations replacing null checks | [view](patterns/null-object/pattern.md) |

### Infrastructure

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Configuration management | 12-factor config with env vars and hierarchical overrides | [view](patterns/config-management/pattern.md) |
| Infrastructure as Code | Declarative infra definitions (Terraform, Pulumi, CloudFormation) | [view](patterns/infrastructure-as-code/pattern.md) |
| Connection pooling | Reusable connection pools for databases and HTTP | [view](patterns/connection-pooling/pattern.md) |

### Networking

| Pattern | Description | Reference |
|---------|-------------|-----------|
| WebSocket | Persistent bidirectional connection | [view](patterns/websocket/pattern.md) |
| Server-sent events | One-way server push via HTTP streaming | [view](patterns/server-sent-events/pattern.md) |
| Long polling | Client holds request until server has data | [view](patterns/long-polling/pattern.md) |

### Observability

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Structured logging | JSON log output with key-value fields | [view](patterns/structured-logging/pattern.md) |
| Metrics instrumentation | Prometheus client usage for counters, gauges, histograms | [view](patterns/metrics-instrumentation/pattern.md) |
| Distributed tracing | OpenTelemetry SDK with span context propagation | [view](patterns/distributed-tracing/pattern.md) |

### Realtime

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Entity-component-system | Entities as IDs, components as data, systems operating on queries | [view](patterns/entity-component-system/pattern.md) |
| Game loop | Fixed timestep update loop with input/update/render phases | [view](patterns/game-loop/pattern.md) |
| Spatial partitioning | Quadtree, octree, or spatial hash for neighbor queries | [view](patterns/spatial-partitioning/pattern.md) |
| Tick simulation | Discrete time steps with deterministic updates | [view](patterns/tick-simulation/pattern.md) |

### ML

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Feature store | Centralized feature repository with online/offline serving | [view](patterns/feature-store/pattern.md) |
| Model registry | Versioned model storage with stage transitions | [view](patterns/model-registry/pattern.md) |
| Training pipeline | Data-to-model stages with experiment tracking | [view](patterns/training-pipeline/pattern.md) |
| Experiment framework | A/B testing with variant bucketing and metric collection | [view](patterns/experiment-framework/pattern.md) |

### Compiler

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Lexer / Parser | Tokenization + parsing into structured representation | [view](patterns/lexer-parser/pattern.md) |
| Abstract syntax tree | Tree node hierarchy representing language constructs | [view](patterns/ast/pattern.md) |
| Intermediate representation | Lowered representation for optimization passes | [view](patterns/intermediate-representation/pattern.md) |

## Libraries

Patterns with kordinate library implementations: stream-to-store (stoik), service-manager (orchestrator).
Implementation files are co-located in the pattern directory.

---
description: Index of recognized architectural patterns by category
curated: true
scope: global
preloaded: designer
---
# Patterns Index

155 patterns across 20 categories. Each pattern has recognition signatures for code scanning.

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
| Microservices | Multiple independently deployable services | [view](concepts/microservices/pattern.md) |
| Modular monolith | Single deployment with internal module boundaries | [view](concepts/modular-monolith/pattern.md) |
| Serverless / FaaS | Stateless request handlers triggered by events | [view](concepts/serverless/pattern.md) |

### Structural

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Hexagonal (ports & adapters) | Decouples business logic from infrastructure via ports and adapters | [view](concepts/hexagonal/pattern.md) |
| Domain-driven design (DDD) | Organizes code around bounded contexts and domain aggregates | [view](concepts/ddd/pattern.md) |
| Plugin architecture | Extensible core with pluggable components registered at startup | [view](concepts/plugin/pattern.md) |
| Aggregate root | Root entity controlling access to child entities within a consistency boundary | [view](concepts/aggregate/pattern.md) |
| Value object | Immutable objects compared by value, not identity | [view](concepts/value-object/pattern.md) |
| Anti-corruption layer | Boundary translation between systems or bounded contexts | [view](concepts/anti-corruption-layer/pattern.md) |
| Decorator / Wrapper | Adding behavior to an object without modifying its interface | [view](concepts/decorator/pattern.md) |
| Proxy | Controls access to an object through the same interface | [view](concepts/proxy/pattern.md) |
| Adapter | Translates one interface to another | [view](concepts/adapter/pattern.md) |
| Facade | Simplified interface to a complex subsystem | [view](concepts/facade/pattern.md) |
| Pipeline / Filter | Ordered chain of transform functions processing data through stages | [view](concepts/pipeline-filter/pattern.md) |
| Composite | Tree structures where leaves and containers share the same interface | [view](concepts/composite/pattern.md) |
| Flyweight | Shared immutable objects to reduce memory | [view](concepts/flyweight/pattern.md) |
| Bridge | Separating abstraction from implementation so both can vary | [view](concepts/bridge/pattern.md) |

### Data

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Stream-to-store | Kafka consumer that writes to a local store via buffered flushes | [view](concepts/stream-to-store/pattern.md) |
| ETL/ELT | Batch extract-transform-load for periodic data processing | [view](concepts/etl/pattern.md) |
| Event sourcing | Append-only event log as the source of truth | [view](concepts/event-sourcing/pattern.md) |
| CQRS | Separate models for reading and writing data | [view](concepts/cqrs/pattern.md) |
| MapReduce | Parallel map phase + reduce/aggregate phase over distributed data | [view](concepts/mapreduce/pattern.md) |
| Idempotent consumer | Message deduplication before processing | [view](concepts/idempotent-consumer/pattern.md) |
| Change data capture | Database log tailing to capture changes as events | [view](concepts/change-data-capture/pattern.md) |
| Ring buffer | Fixed-size circular buffer with wrap-around | [view](concepts/ring-buffer/pattern.md) |
| Bloom filter | Probabilistic membership test with bit array | [view](concepts/bloom-filter/pattern.md) |
| Trie | Prefix tree for autocomplete and routing | [view](concepts/trie/pattern.md) |

### Integration

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Saga | Distributed transactions via local transactions with compensating actions | [view](concepts/saga/pattern.md) |
| Choreography | Services react to events independently with no central coordinator | [view](concepts/choreography/pattern.md) |
| API gateway | Centralized entry point for routing, auth, and rate limiting | [view](concepts/api-gateway/pattern.md) |
| Webhook | Callback URL registration with event delivery | [view](concepts/webhook/pattern.md) |
| Claim check | Large payload stored externally, message contains reference | [view](concepts/claim-check/pattern.md) |

### Resilience

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Circuit breaker | Stops calling a failing dependency after a threshold, allows recovery | [view](concepts/circuit-breaker/pattern.md) |
| Bulkhead | Isolates components so one failure doesn't exhaust shared resources | [view](concepts/bulkhead/pattern.md) |
| Retry with backoff | Retries failed operations with exponential delay and jitter | [view](concepts/retry/pattern.md) |
| Backpressure | Flow control when a producer is faster than its consumer | [view](concepts/backpressure/pattern.md) |
| Timeout | Explicit timeout on every external call | [view](concepts/timeout/pattern.md) |
| Graceful degradation | Fallback responses when dependencies are down | [view](concepts/graceful-degradation/pattern.md) |

### Lifecycle

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Service manager | Manages service startup, shutdown, health reporting, and graceful degradation | [view](concepts/service-manager/pattern.md) |
| Sidecar | Auxiliary container handling cross-cutting concerns alongside the main workload | [view](concepts/sidecar/pattern.md) |
| Scheduler / Cron | Time-based triggers for periodic task execution | [view](concepts/scheduler/pattern.md) |
| Workflow engine | DAG-based step/task orchestration with dependencies | [view](concepts/workflow-engine/pattern.md) |
| Strangler fig | Incremental replacement of legacy system | [view](concepts/strangler-fig/pattern.md) |
| Database migration | Versioned schema changes with up/down rollback | [view](concepts/database-migration/pattern.md) |

### Creational

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Factory | Object creation via factory methods/classes returning interfaces | [view](concepts/factory/pattern.md) |
| Abstract factory | Family of related objects created through a factory interface | [view](concepts/abstract-factory/pattern.md) |
| Builder | Step-by-step object construction with fluent method chaining | [view](concepts/builder/pattern.md) |
| Singleton | Single instance shared across the application | [view](concepts/singleton/pattern.md) |
| Object pool | Reusable object pool with acquire/release lifecycle | [view](concepts/object-pool/pattern.md) |
| Dependency injection | Inversion of control via constructor/setter injection | [view](concepts/dependency-injection/pattern.md) |
| Prototype | Creating objects by cloning existing instances | [view](concepts/prototype/pattern.md) |

### Behavioral

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Strategy | Interchangeable algorithms behind a common interface | [view](concepts/strategy/pattern.md) |
| Observer | Event emitter with subscribe/notify for decoupled communication | [view](concepts/observer/pattern.md) |
| Command | Encapsulated operations as objects with execute/undo | [view](concepts/command/pattern.md) |
| State machine | Explicit states with defined transitions and lifecycle hooks | [view](concepts/state-machine/pattern.md) |
| Chain of responsibility | Ordered handler chain where each can process or pass the request | [view](concepts/chain-of-responsibility/pattern.md) |
| Mediator | Central coordinator for component communication | [view](concepts/mediator/pattern.md) |
| Template method | Abstract base with overridable hook methods | [view](concepts/template-method/pattern.md) |
| Visitor | Double-dispatch traversal with accept/visit methods | [view](concepts/visitor/pattern.md) |
| Iterator | Lazy sequential access to elements without exposing internals | [view](concepts/iterator/pattern.md) |
| Specification | Composable boolean predicates for business rules | [view](concepts/specification/pattern.md) |
| Monad / Railway | Chained operations that short-circuit on failure via bind/flatMap | [view](concepts/monad/pattern.md) |
| Memento | Capturing and restoring object state (undo/redo) | [view](concepts/memento/pattern.md) |

### Concurrency

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Actor model | Isolated actors communicating via asynchronous message passing | [view](concepts/actor-model/pattern.md) |
| Producer-consumer | Shared queue/buffer between producing and consuming threads | [view](concepts/producer-consumer/pattern.md) |
| Worker pool | Fixed pool of workers processing tasks from a queue | [view](concepts/worker-pool/pattern.md) |
| Reactor / Event loop | Single-threaded event loop with non-blocking I/O | [view](concepts/reactor/pattern.md) |
| Read-write lock | Separate locks for concurrent reads and exclusive writes | [view](concepts/read-write-lock/pattern.md) |
| Future / Promise | Deferred computation with async result containers | [view](concepts/future-promise/pattern.md) |

### Frontend

| Pattern | Description | Reference |
|---------|-------------|-----------|
| MVC | Model-View-Controller separation of concerns | [view](concepts/mvc/pattern.md) |
| MVVM | Model-View-ViewModel with observable data binding | [view](concepts/mvvm/pattern.md) |
| Component | Self-contained UI components with props/state composition | [view](concepts/component/pattern.md) |
| Flux / Redux | Unidirectional data flow with store, actions, and reducers | [view](concepts/flux/pattern.md) |
| Micro-frontend | Independently deployable frontend modules | [view](concepts/micro-frontend/pattern.md) |

### Storage

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Repository | Abstraction over data access with CRUD operations | [view](concepts/repository/pattern.md) |
| Unit of work | Transaction management wrapping multiple operations | [view](concepts/unit-of-work/pattern.md) |
| Active record | Model instances with built-in persistence methods | [view](concepts/active-record/pattern.md) |
| Data mapper | Separate mapper transferring data between objects and database | [view](concepts/data-mapper/pattern.md) |
| Cache-aside | Check cache first, load from source on miss | [view](concepts/cache-aside/pattern.md) |
| Read-through | Cache that loads from source on miss automatically | [view](concepts/read-through/pattern.md) |
| Refresh-ahead | Proactive cache refresh before TTL expiry | [view](concepts/refresh-ahead/pattern.md) |
| Write-behind | Writes go to cache first, async flush to backing store | [view](concepts/write-behind/pattern.md) |
| Cache stampede prevention | Lock-based or probabilistic cache population to prevent thundering herd | [view](concepts/cache-stampede-prevention/pattern.md) |
| LRU cache | Bounded cache with least-recently-used eviction | [view](concepts/lru-cache/pattern.md) |
| Sharding | Data partitioned across nodes by shard key | [view](concepts/sharding/pattern.md) |
| Optimistic locking | Version field for conflict detection on write | [view](concepts/optimistic-locking/pattern.md) |
| Soft delete | Logical deletion with timestamp/flag instead of physical removal | [view](concepts/soft-delete/pattern.md) |
| Materialized view | Pre-computed query results stored as table/cache | [view](concepts/materialized-view/pattern.md) |
| Batch loader | N+1 prevention via batched queries | [view](concepts/batch-loader/pattern.md) |
| Pagination | Cursor or offset-based result windowing | [view](concepts/pagination/pattern.md) |

### Messaging

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Publish-subscribe | Topic-based fan-out messaging to multiple subscribers | [view](concepts/pub-sub/pattern.md) |
| Message queue | Point-to-point messaging with each message consumed once | [view](concepts/message-queue/pattern.md) |
| Dead letter queue | Failed message routing with retry tracking | [view](concepts/dead-letter/pattern.md) |
| Competing consumers | Multiple consumers on the same queue for load balancing | [view](concepts/competing-consumers/pattern.md) |
| Request-reply | RPC over message broker with correlation IDs | [view](concepts/request-reply/pattern.md) |
| Event-driven architecture | Domain events as first-class objects flowing through an event bus | [view](concepts/event-driven/pattern.md) |
| Outbox | Events written to DB in same transaction, published by separate process | [view](concepts/outbox/pattern.md) |
| Event notification | Thin events containing only ID + type, consumer calls back for data | [view](concepts/event-notification/pattern.md) |
| Event-carried state | Fat events containing full entity state for replication | [view](concepts/event-carried-state/pattern.md) |

### Deployment

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Blue-green | Two identical environments with traffic switching | [view](concepts/blue-green/pattern.md) |
| Canary | Gradual traffic splitting between stable and new versions | [view](concepts/canary/pattern.md) |
| Feature flag | Runtime feature toggles for conditional functionality | [view](concepts/feature-flag/pattern.md) |
| GitOps | Git repo as source of truth with reconciliation loops | [view](concepts/gitops/pattern.md) |
| Immutable infrastructure | Replace-not-patch, image-based deployment | [view](concepts/immutable-infra/pattern.md) |

### Security

| Pattern | Description | Reference |
|---------|-------------|-----------|
| OAuth2 / OIDC | Authorization code flow with token-based access | [view](concepts/oauth-oidc/pattern.md) |
| RBAC | Role-based access control with role-permission mapping | [view](concepts/rbac/pattern.md) |
| Rate limiting | Request throttling with token bucket or sliding window | [view](concepts/rate-limiting/pattern.md) |
| Secret management | Vault/KMS-based credential storage, never hardcoded | [view](concepts/secret-management/pattern.md) |
| Session auth | Session-based authentication with server-side session store | [view](concepts/session-auth/pattern.md) |
| Token auth (JWT) | Stateless token-based authentication with Bearer tokens | [view](concepts/token-auth/pattern.md) |
| Mutual TLS | Client certificate authentication for service-to-service | [view](concepts/mtls/pattern.md) |
| API key auth | API key validation for programmatic access | [view](concepts/api-key-auth/pattern.md) |
| Audit logging | Immutable log of who-did-what-when for compliance | [view](concepts/audit-logging/pattern.md) |
| Input validation | Schema validation and sanitization at API boundary | [view](concepts/input-validation/pattern.md) |
| CORS | Cross-origin resource sharing configuration | [view](concepts/cors/pattern.md) |
| Tenant isolation | Tenant-scoped data access (DB/schema/row-level) | [view](concepts/tenant-isolation/pattern.md) |
| Tenant routing | Tenant-aware request routing and connection switching | [view](concepts/tenant-routing/pattern.md) |

### API

| Pattern | Description | Reference |
|---------|-------------|-----------|
| REST | Resource-based HTTP API with standard methods and status codes | [view](concepts/rest/pattern.md) |
| GraphQL | Schema-driven query language with single endpoint | [view](concepts/graphql/pattern.md) |
| gRPC | Protocol buffer-based RPC with generated stubs | [view](concepts/grpc/pattern.md) |
| BFF | Backend for Frontend — API layer tailored per client type | [view](concepts/bff/pattern.md) |
| Content negotiation | Format selection via Accept/Content-Type headers | [view](concepts/content-negotiation/pattern.md) |

### Distributed

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Service mesh | Sidecar proxy layer for service-to-service communication | [view](concepts/service-mesh/pattern.md) |
| Leader election | Single leader coordination with lease-based failover | [view](concepts/leader-election/pattern.md) |
| Distributed lock | Cross-node mutual exclusion with TTL | [view](concepts/distributed-lock/pattern.md) |
| Health check | Liveness/readiness probes with dependency health aggregation | [view](concepts/health-check/pattern.md) |
| Correlation ID | Request ID propagation for distributed tracing | [view](concepts/correlation-id/pattern.md) |
| Service discovery | Registry-based or DNS-based service endpoint resolution | [view](concepts/service-discovery/pattern.md) |

### Testing

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Test doubles | Mock, stub, fake, and spy implementations for isolation | [view](concepts/test-doubles/pattern.md) |
| Contract testing | Consumer-driven contracts verified against providers | [view](concepts/contract-testing/pattern.md) |
| Property testing | Generator-based input with invariant assertions | [view](concepts/property-testing/pattern.md) |
| Fixture builder | Test data factories and builder helpers | [view](concepts/fixture-builder/pattern.md) |
| Snapshot testing | Output comparison against stored snapshots | [view](concepts/snapshot-testing/pattern.md) |

### Error Handling

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Result / Either type | Errors as values, not exceptions — with map/bind composition | [view](concepts/result-type/pattern.md) |
| Null object | No-op implementations replacing null checks | [view](concepts/null-object/pattern.md) |

### Infrastructure

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Configuration management | 12-factor config with env vars and hierarchical overrides | [view](concepts/config-management/pattern.md) |
| Infrastructure as Code | Declarative infra definitions (Terraform, Pulumi, CloudFormation) | [view](concepts/infrastructure-as-code/pattern.md) |
| Connection pooling | Reusable connection pools for databases and HTTP | [view](concepts/connection-pooling/pattern.md) |

### Networking

| Pattern | Description | Reference |
|---------|-------------|-----------|
| WebSocket | Persistent bidirectional connection | [view](concepts/websocket/pattern.md) |
| Server-sent events | One-way server push via HTTP streaming | [view](concepts/server-sent-events/pattern.md) |
| Long polling | Client holds request until server has data | [view](concepts/long-polling/pattern.md) |

### Observability

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Structured logging | JSON log output with key-value fields | [view](concepts/structured-logging/pattern.md) |
| Metrics instrumentation | Prometheus client usage for counters, gauges, histograms | [view](concepts/metrics-instrumentation/pattern.md) |
| Distributed tracing | OpenTelemetry SDK with span context propagation | [view](concepts/distributed-tracing/pattern.md) |

### Realtime

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Entity-component-system | Entities as IDs, components as data, systems operating on queries | [view](concepts/entity-component-system/pattern.md) |
| Game loop | Fixed timestep update loop with input/update/render phases | [view](concepts/game-loop/pattern.md) |
| Spatial partitioning | Quadtree, octree, or spatial hash for neighbor queries | [view](concepts/spatial-partitioning/pattern.md) |
| Tick simulation | Discrete time steps with deterministic updates | [view](concepts/tick-simulation/pattern.md) |

### ML

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Feature store | Centralized feature repository with online/offline serving | [view](concepts/feature-store/pattern.md) |
| Model registry | Versioned model storage with stage transitions | [view](concepts/model-registry/pattern.md) |
| Training pipeline | Data-to-model stages with experiment tracking | [view](concepts/training-pipeline/pattern.md) |
| Experiment framework | A/B testing with variant bucketing and metric collection | [view](concepts/experiment-framework/pattern.md) |

### Compiler

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Lexer / Parser | Tokenization + parsing into structured representation | [view](concepts/lexer-parser/pattern.md) |
| Abstract syntax tree | Tree node hierarchy representing language constructs | [view](concepts/ast/pattern.md) |
| Intermediate representation | Lowered representation for optimization passes | [view](concepts/intermediate-representation/pattern.md) |

## Libraries

Patterns with kordinate library implementations: stream-to-store (stoik), service-manager (orchestrator).
Implementation files are co-located in the pattern directory.

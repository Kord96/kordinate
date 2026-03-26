---
description: Index of recognized architectural patterns by category
curated: true
scope: global
preloaded: designer
---
# Patterns Index

71 patterns across 15 categories. Each pattern has recognition signatures for code scanning.

## Categories

| Category | Scope | Key Question |
|----------|-------|--------------|
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

## Patterns

### Structural

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Hexagonal (ports & adapters) | Decouples business logic from infrastructure via ports and adapters | [view](patterns/hexagonal/pattern.md) |
| Domain-driven design (DDD) | Organizes code around bounded contexts and domain aggregates | [view](patterns/ddd/pattern.md) |
| Plugin architecture | Extensible core with pluggable components registered at startup | [view](patterns/plugin/pattern.md) |

### Data

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Stream-to-store | Kafka consumer that writes to a local store via buffered flushes | [view](patterns/stream-to-store/pattern.md) |
| ETL/ELT | Batch extract-transform-load for periodic data processing | [view](patterns/etl/pattern.md) |
| Event sourcing | Append-only event log as the source of truth | [view](patterns/event-sourcing/pattern.md) |
| CQRS | Separate models for reading and writing data | [view](patterns/cqrs/pattern.md) |

### Integration

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Saga | Distributed transactions via local transactions with compensating actions | [view](patterns/saga/pattern.md) |
| Choreography | Services react to events independently with no central coordinator | [view](patterns/choreography/pattern.md) |
| API gateway | Centralized entry point for routing, auth, and rate limiting | [view](patterns/api-gateway/pattern.md) |

### Resilience

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Circuit breaker | Stops calling a failing dependency after a threshold, allows recovery | [view](patterns/circuit-breaker/pattern.md) |
| Bulkhead | Isolates components so one failure doesn't exhaust shared resources | [view](patterns/bulkhead/pattern.md) |
| Retry with backoff | Retries failed operations with exponential delay and jitter | [view](patterns/retry/pattern.md) |
| Backpressure | Flow control when a producer is faster than its consumer | [view](patterns/backpressure/pattern.md) |

### Lifecycle

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Service manager | Manages service startup, shutdown, health reporting, and graceful degradation | [view](patterns/service-manager/pattern.md) |
| Sidecar | Auxiliary container handling cross-cutting concerns alongside the main workload | [view](patterns/sidecar/pattern.md) |

### Creational

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Factory | Object creation via factory methods/classes returning interfaces | [view](patterns/factory/pattern.md) |
| Builder | Step-by-step object construction with fluent method chaining | [view](patterns/builder/pattern.md) |
| Singleton | Single instance shared across the application | [view](patterns/singleton/pattern.md) |
| Object pool | Reusable object pool with acquire/release lifecycle | [view](patterns/object-pool/pattern.md) |
| Dependency injection | Inversion of control via constructor/setter injection | [view](patterns/dependency-injection/pattern.md) |

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
| Write-behind | Writes go to cache first, async flush to backing store | [view](patterns/write-behind/pattern.md) |
| Sharding | Data partitioned across nodes by shard key | [view](patterns/sharding/pattern.md) |

### Messaging

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Publish-subscribe | Topic-based fan-out messaging to multiple subscribers | [view](patterns/pub-sub/pattern.md) |
| Message queue | Point-to-point messaging with each message consumed once | [view](patterns/message-queue/pattern.md) |
| Dead letter queue | Failed message routing with retry tracking | [view](patterns/dead-letter/pattern.md) |
| Competing consumers | Multiple consumers on the same queue for load balancing | [view](patterns/competing-consumers/pattern.md) |
| Request-reply | RPC over message broker with correlation IDs | [view](patterns/request-reply/pattern.md) |
| Event-driven architecture | Domain events as first-class objects flowing through an event bus | [view](patterns/event-driven/pattern.md) |

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

### API

| Pattern | Description | Reference |
|---------|-------------|-----------|
| REST | Resource-based HTTP API with standard methods and status codes | [view](patterns/rest/pattern.md) |
| GraphQL | Schema-driven query language with single endpoint | [view](patterns/graphql/pattern.md) |
| gRPC | Protocol buffer-based RPC with generated stubs | [view](patterns/grpc/pattern.md) |
| BFF | Backend for Frontend — API layer tailored per client type | [view](patterns/bff/pattern.md) |

### Distributed

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Service mesh | Sidecar proxy layer for service-to-service communication | [view](patterns/service-mesh/pattern.md) |
| Leader election | Single leader coordination with lease-based failover | [view](patterns/leader-election/pattern.md) |
| Distributed lock | Cross-node mutual exclusion with TTL | [view](patterns/distributed-lock/pattern.md) |
| Health check | Liveness/readiness probes with dependency health aggregation | [view](patterns/health-check/pattern.md) |
| Correlation ID | Request ID propagation for distributed tracing | [view](patterns/correlation-id/pattern.md) |

## Libraries

Patterns with kordinate library implementations: stream-to-store (stoik), service-manager (orchestrator).
Implementation files are co-located in the pattern directory.

# Shared Patterns Index

## Categories

| Category | Scope | Key Question |
|----------|-------|--------------|
| structural | How code is organized within a service | Is business logic decoupled from infrastructure? |
| data | How data flows and is stored | Is data moving correctly through the system? |
| integration | How services communicate with each other | Are cross-service interactions safe and traceable? |
| resilience | How the system handles failure | What happens when a dependency goes down? |
| lifecycle | How a single service starts, runs, and stops | Does the service boot and shut down cleanly? |

## Agent Coverage

Which agents have perspective docs for each pattern. Links point to `agent-memory/<agent>/patterns/<pattern>.md`.

| Pattern | Designer | Deployer | Sauron |
|---------|----------|----------|--------|
| Hexagonal | [view](designer/patterns/hexagonal.md) | — | — |
| DDD | [view](designer/patterns/ddd.md) | — | — |
| Plugin | [view](designer/patterns/plugin.md) | — | — |
| Stream-to-store | [view](designer/patterns/stream-to-store.md) | — | — |
| ETL/ELT | [view](designer/patterns/etl.md) | — | — |
| Event sourcing | [view](designer/patterns/event-sourcing.md) | [view](deployer/patterns/event-sourcing.md) | — |
| CQRS | [view](designer/patterns/cqrs.md) | — | — |
| Saga | [view](designer/patterns/saga.md) | — | [view](sauron/patterns/saga.md) |
| Choreography | [view](designer/patterns/choreography.md) | — | — |
| API gateway | [view](designer/patterns/api-gateway.md) | — | — |
| Circuit breaker | [view](designer/patterns/circuit-breaker.md) | [view](deployer/patterns/circuit-breaker.md) | [view](sauron/patterns/circuit-breaker.md) |
| Bulkhead | [view](designer/patterns/bulkhead.md) | — | — |
| Retry with backoff | [view](designer/patterns/retry.md) | — | — |
| Backpressure | — | — | [view](sauron/patterns/backpressure.md) |
| Service manager | [view](designer/patterns/service-manager.md) | — | — |
| Sidecar | [view](designer/patterns/sidecar.md) | — | — |

## Patterns

### Structural

| Pattern | Description |
|---------|-------------|
| Hexagonal (ports & adapters) | Decouples business logic from infrastructure via ports (interfaces) and adapters (implementations). Makes services testable and swappable. |
| Domain-driven design (DDD) | Organizes code around bounded contexts and domain aggregates. Events flow between contexts, not direct calls. |
| Plugin architecture | Extensible core with pluggable components registered at startup. New capabilities without modifying core code. |

### Data

| Pattern | Description |
|---------|-------------|
| Stream-to-store | Kafka consumer that writes to a local store via buffered flushes. Core pattern for pipeline services. |
| ETL/ELT | Batch extract-transform-load for periodic data processing. Scheduled via cron or service manager. |
| Event sourcing | Append-only event log as the source of truth. Current state derived by replaying events. |
| CQRS | Separate models for reading and writing data. Write model optimized for consistency, read model for query performance. |

### Integration

| Pattern | Description |
|---------|-------------|
| Saga | Distributed transactions across services via a sequence of local transactions with compensating actions on failure. |
| Choreography | Services react to events independently with no central coordinator. Loose coupling but harder to trace. |
| API gateway | Centralized entry point for routing, auth, and rate limiting across multiple backend services. |

### Resilience

| Pattern | Description |
|---------|-------------|
| Circuit breaker | Stops calling a failing dependency after a threshold, allows recovery time, then retries. Prevents cascade failures. |
| Bulkhead | Isolates components so one failure doesn't exhaust shared resources (threads, connections, memory). |
| Retry with backoff | Retries failed operations with exponential delay and jitter. Dead-letter queue for permanent failures. |
| Backpressure | Flow control when a producer is faster than its consumer. Prevents memory exhaustion and queue overflow. |

### Lifecycle

| Pattern | Description |
|---------|-------------|
| Service manager | Manages service startup, shutdown, health reporting, and graceful degradation within a single process. |
| Sidecar | Auxiliary container running alongside the main workload, handling cross-cutting concerns (networking, logging, auth). |

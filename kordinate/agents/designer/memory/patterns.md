---
description: Index of recognized architectural patterns by category
curated: true
scope: global
preloaded: designer
---
# Patterns Index

## Categories

| Category | Scope | Key Question |
|----------|-------|--------------|
| structural | How code is organized within a service | Is business logic decoupled from infrastructure? |
| data | How data flows and is stored | Is data moving correctly through the system? |
| integration | How services communicate with each other | Are cross-service interactions safe and traceable? |
| resilience | How the system handles failure | What happens when a dependency goes down? |
| lifecycle | How a single service starts, runs, and stops | Does the service boot and shut down cleanly? |

## Patterns

### Structural

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Hexagonal (ports & adapters) | Decouples business logic from infrastructure via ports (interfaces) and adapters (implementations). Makes services testable and swappable. | [view](patterns/hexagonal/pattern.md) |
| Domain-driven design (DDD) | Organizes code around bounded contexts and domain aggregates. Events flow between contexts, not direct calls. | [view](patterns/ddd/pattern.md) |
| Plugin architecture | Extensible core with pluggable components registered at startup. New capabilities without modifying core code. | [view](patterns/plugin/pattern.md) |

### Data

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Stream-to-store | Kafka consumer that writes to a local store via buffered flushes. Core pattern for pipeline services. | [view](patterns/stream-to-store/pattern.md) |
| ETL/ELT | Batch extract-transform-load for periodic data processing. Scheduled via cron or service manager. | [view](patterns/etl/pattern.md) |
| Event sourcing | Append-only event log as the source of truth. Current state derived by replaying events. | [view](patterns/event-sourcing/pattern.md) |
| CQRS | Separate models for reading and writing data. Write model optimized for consistency, read model for query performance. | [view](patterns/cqrs/pattern.md) |

### Integration

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Saga | Distributed transactions across services via a sequence of local transactions with compensating actions on failure. | [view](patterns/saga/pattern.md) |
| Choreography | Services react to events independently with no central coordinator. Loose coupling but harder to trace. | [view](patterns/choreography/pattern.md) |
| API gateway | Centralized entry point for routing, auth, and rate limiting across multiple backend services. | [view](patterns/api-gateway/pattern.md) |

### Resilience

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Circuit breaker | Stops calling a failing dependency after a threshold, allows recovery time, then retries. Prevents cascade failures. | [view](patterns/circuit-breaker/pattern.md) |
| Bulkhead | Isolates components so one failure doesn't exhaust shared resources (threads, connections, memory). | [view](patterns/bulkhead/pattern.md) |
| Retry with backoff | Retries failed operations with exponential delay and jitter. Dead-letter queue for permanent failures. | [view](patterns/retry/pattern.md) |
| Backpressure | Flow control when a producer is faster than its consumer. Prevents memory exhaustion and queue overflow. | [view](patterns/backpressure/pattern.md) |

### Lifecycle

| Pattern | Description | Reference |
|---------|-------------|-----------|
| Service manager | Manages service startup, shutdown, health reporting, and graceful degradation within a single process. | [view](patterns/service-manager/pattern.md) |
| Sidecar | Auxiliary container running alongside the main workload, handling cross-cutting concerns (networking, logging, auth). | [view](patterns/sidecar/pattern.md) |

## Libraries

Patterns with kordinate library implementations: stream-to-store (stoik), service-manager (orchestrator).
Implementation files are co-located in the pattern directory.

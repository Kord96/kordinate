# Shared Patterns Index

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

| Pattern | Repo | Description |
|---------|------|-------------|
| Hexagonal (ports & adapters) | — | Decouples business logic from infrastructure via ports (interfaces) and adapters (implementations). Makes services testable and swappable. |
| Domain-driven design (DDD) | — | Organizes code around bounded contexts and domain aggregates. Events flow between contexts, not direct calls. |
| Plugin architecture | — | Extensible core with pluggable components registered at startup. New capabilities without modifying core code. |

### Data

| Pattern | Repo | Description |
|---------|------|-------------|
| Stoik (stream-to-store) | [stoik](https://github.com/Kord96/stoik) | Kafka consumer that writes to a local DuckDB store via buffered flushes. Core pattern for pipeline services. |
| ETL/ELT | — | Batch extract-transform-load for periodic data processing. Scheduled via cron or orchestrator. |
| Event sourcing | — | Append-only event log as the source of truth. Current state derived by replaying events. |
| CQRS | — | Separate models for reading and writing data. Write model optimized for consistency, read model for query performance. |

### Integration

| Pattern | Repo | Description |
|---------|------|-------------|
| Saga | — | Distributed transactions across services via a sequence of local transactions with compensating actions on failure. |
| Choreography | — | Services react to events independently with no central coordinator. Loose coupling but harder to trace. |
| API gateway | — | Centralized entry point for routing, auth, and rate limiting across multiple backend services. |

### Resilience

| Pattern | Repo | Description |
|---------|------|-------------|
| Circuit breaker | — | Stops calling a failing dependency after a threshold, allows recovery time, then retries. Prevents cascade failures. |
| Bulkhead | — | Isolates components so one failure doesn't exhaust shared resources (threads, connections, memory). |
| Retry with backoff | — | Retries failed operations with exponential delay and jitter. Dead-letter queue for permanent failures. |
| Backpressure | — | Flow control when a producer is faster than its consumer. Prevents memory exhaustion and queue overflow. |

### Lifecycle

| Pattern | Repo | Description |
|---------|------|-------------|
| Orchestrator (service manager) | [orchestrator](https://github.com/Kord96/orchestrator) | Manages service startup, shutdown, health reporting, and graceful degradation within a single process. |
| Sidecar | — | Auxiliary container running alongside the main workload, handling cross-cutting concerns (networking, logging, auth). |

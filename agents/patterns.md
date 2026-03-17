# Shared Patterns Index

| Pattern | Category | Description |
|---------|----------|-------------|
| Hexagonal (ports & adapters) | structural | Decouples business logic from infrastructure via ports (interfaces) and adapters (implementations). Makes services testable and swappable. |
| Domain-driven design (DDD) | structural | Organizes code around bounded contexts and domain aggregates. Events flow between contexts, not direct calls. |
| Plugin architecture | structural | Extensible core with pluggable components registered at startup. New capabilities without modifying core code. |
| Stoik (stream-to-store) | data | Kafka consumer that writes to a local DuckDB store via buffered flushes. Core pattern for pipeline services. |
| ETL/ELT | data | Batch extract-transform-load for periodic data processing. Scheduled via cron or orchestrator. |
| Event sourcing | data | Append-only event log as the source of truth. Current state derived by replaying events. |
| CQRS | data | Separate models for reading and writing data. Write model optimized for consistency, read model for query performance. |
| Saga | integration | Distributed transactions across services via a sequence of local transactions with compensating actions on failure. |
| Choreography | integration | Services react to events independently with no central coordinator. Loose coupling but harder to trace. |
| API gateway | integration | Centralized entry point for routing, auth, and rate limiting across multiple backend services. |
| Circuit breaker | resilience | Stops calling a failing dependency after a threshold, allows recovery time, then retries. Prevents cascade failures. |
| Bulkhead | resilience | Isolates components so one failure doesn't exhaust shared resources (threads, connections, memory). |
| Retry with backoff | resilience | Retries failed operations with exponential delay and jitter. Dead-letter queue for permanent failures. |
| Backpressure | resilience | Flow control when a producer is faster than its consumer. Prevents memory exhaustion and queue overflow. |
| Orchestrator (service manager) | lifecycle | Manages service startup, shutdown, health reporting, and graceful degradation within a single process. |
| Sidecar | lifecycle | Auxiliary container running alongside the main workload, handling cross-cutting concerns (networking, logging, auth). |

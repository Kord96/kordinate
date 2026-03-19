# Design Patterns

Recognized architectural patterns used across our projects. Each pattern page explains what it is, when to use it, how it works, and where we use it.

## By Category

=== "Platform"

    How apps connect to infrastructure. Enforced by deployer at deploy time.

    | Pattern | What it does |
    |---------|-------------|
    | [Observability Contract](observability-contract.md) | Logs, metrics, and health — the app-to-platform interface |

=== "Resilience"

    How the system handles failure.

    | Pattern | What it does |
    |---------|-------------|
    | [Circuit Breaker](circuit-breaker.md) | Stops calling a failing dependency, waits, then retries |
    | [Bulkhead](bulkhead.md) | Isolates resources so one failure can't exhaust everything |
    | [Retry with Backoff](retry.md) | Retries with exponential delay and jitter |
    | [Backpressure](backpressure.md) | Flow control when producer outpaces consumer |

=== "Data"

    How data flows and is stored.

    | Pattern | What it does |
    |---------|-------------|
    | [Stream-to-Store](stream-to-store.md) | Kafka → buffered flush → database/S3 |
    | [ETL/ELT](etl.md) | Batch extract-transform-load for periodic processing |
    | [Event Sourcing](event-sourcing.md) | Append-only event log as source of truth |
    | [CQRS](cqrs.md) | Separate read and write models |

=== "Integration"

    How services communicate.

    | Pattern | What it does |
    |---------|-------------|
    | [Saga](saga.md) | Distributed transactions with compensating actions |
    | [Choreography](choreography.md) | Event-driven, no central coordinator |
    | [API Gateway](api-gateway.md) | Centralized routing, auth, rate limiting |

=== "Structural"

    How code is organized.

    | Pattern | What it does |
    |---------|-------------|
    | [Hexagonal](hexagonal.md) | Ports & adapters — decouple business logic from infra |
    | [DDD](ddd.md) | Bounded contexts and domain aggregates |
    | [Plugin](plugin.md) | Extensible core with registered components |

=== "Lifecycle"

    How services start, run, and stop.

    | Pattern | What it does |
    |---------|-------------|
    | [Service Manager](service-manager.md) | Startup, shutdown, health, graceful degradation |
    | [Sidecar](sidecar.md) | Auxiliary container for cross-cutting concerns |

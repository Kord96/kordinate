---
description: Connection Pooling architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction:
- infrastructure
status: primary
scope: cross-cutting
relationships:
  related_to:
  - bulkhead
  - health-check
  - distributed-lock
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Connection Pooling

## Recognition

How to identify this pattern in code.

### Signatures

- `pool_size`, `max_connections`, `min_idle` configuration parameters
- `SQLAlchemy create_engine(pool_size=)` (Python)
- `HikariCP` configuration (`maximumPoolSize`, `minimumIdle`) (Java)
- `pgBouncer` or `PgPool` as external connection pooler (PostgreSQL)
- `redis.ConnectionPool` or `redis.BlockingConnectionPool` (Python/Redis)
- `http.Agent({keepAlive: true, maxSockets:})` (Node.js)
- Connection checkout/checkin lifecycle in application code
- Pool exhaustion handling (`pool_timeout`, `QueuePool` overflow settings)

### Confidence

- **high** -- explicit pool configuration with size limits, idle management, and health checks on pooled connections
- **medium** -- pool is configured via framework defaults but pool size and timeout are not explicitly tuned
- **low** -- connections are reused implicitly by a library but no pool configuration is visible in the codebase

## Architecture

Look for bounded, reusable connection pools with health checks and proper lifecycle management.

### Review Checklist

- Pool size is tuned for the workload -- not left at framework defaults
- Idle connections are cleaned up to avoid holding resources unnecessarily
- Connection health is validated before checkout (test-on-borrow or background validation)
- Pool exhaustion behavior is defined (block with timeout, reject, or overflow)
- Connections are always returned to the pool -- no leaks from unclosed connections in error paths
- Pool metrics are exposed (active, idle, waiting, timeout counts)

### Anti-patterns

- Creating a new connection per request instead of pooling
- Pool size set to match max concurrent users (overprovisioned, exhausting DB connection limits)
- No connection validation -- stale or broken connections handed to callers
- Missing connection return in error paths -- pool drains under sustained errors

### Relationship To Other Concepts

- Related to [bulkhead](/concepts/bulkhead) because dedicated pools are one common way to isolate capacity across dependencies or workloads.
- Related to [health-check](/concepts/health-check) when broken or stale connections need validation before being handed to traffic.
- Related to [distributed-lock](/concepts/distributed-lock) when lock providers or coordination clients rely on pooled backend connections.

### Boundary

Use `connection-pooling` when expensive backend connections are intentionally reused through a managed pool instead of being created per operation.

Do not use it for any resource cache. The key signal is lifecycle management of reusable network or database connections.

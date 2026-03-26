---
description: Connection Pooling architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
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

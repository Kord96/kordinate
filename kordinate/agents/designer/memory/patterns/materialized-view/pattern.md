---
description: Materialized View architectural pattern
curated: true
scope: global
preloaded: none
---
# Materialized View

## Recognition

How to identify this pattern in code.

### Signatures

- `CREATE MATERIALIZED VIEW` in database migrations or schema definitions
- Pre-computed query results stored as denormalized tables or cache entries
- Refresh schedules: `REFRESH MATERIALIZED VIEW`, cron-triggered rebuild jobs
- Denormalized read models or projection tables in CQRS architectures
- View rebuild or refresh logic triggered by source data changes (event-driven or scheduled)
- Redis/Memcached entries populated from complex joins and served as flat lookups
- `CONCURRENTLY` refresh option to avoid locking during rebuilds

### Confidence

- **high** -- `CREATE MATERIALIZED VIEW` with a scheduled or event-driven refresh mechanism
- **medium** -- Denormalized projection tables populated by background workers from normalized source data
- **low** -- Cache layer storing computed aggregations that are periodically invalidated and rebuilt

## Architecture

Look for a clear separation between the source of truth and the materialized read model, with a defined refresh strategy.

### Review Checklist

- Source of truth and materialized view are clearly separated with a defined refresh mechanism
- Refresh strategy (scheduled, event-driven, or on-demand) is appropriate for the staleness tolerance
- Concurrent refresh is used where available to avoid blocking reads during rebuilds
- Monitoring tracks refresh duration, staleness age, and failure rate
- Fallback behavior is defined for when the view is stale or refresh fails (serve stale, query source, error)
- Indexes on the materialized view are optimized for the read queries it serves

### Anti-patterns

- No refresh mechanism, causing the materialized view to go stale indefinitely after initial creation
- Refreshing synchronously in the request path, adding latency to user-facing reads
- No monitoring on staleness, so consumers unknowingly serve outdated data
- Materialized view used as the source of truth with no way to rebuild from original data

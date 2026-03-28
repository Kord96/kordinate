## Testing

Verify that the materialized view reflects source data accurately and handles refresh failures gracefully.

### Unit Tests

- Insert known data into the source tables, trigger a refresh, and assert the view contents match expected output
- Modify source data, refresh, and verify the view reflects the changes
- Verify that concurrent refresh (`CONCURRENTLY`) does not block read queries

### Integration Tests

- Simulate a refresh failure and verify the fallback behavior (serve stale data, query source directly, or return error)
- Test the full refresh cycle under realistic data volumes and assert it completes within the staleness SLA
- Validate that indexes on the materialized view are maintained after refresh

### Edge Cases

- Refresh with no source data changes and verify the view remains valid and unchanged
- Drop and recreate the view from source data to verify the rebuild path works end-to-end

## Monitoring

Track view freshness, refresh performance, and query patterns to detect stale or degraded read models.

### Key Metrics

- `view_staleness_seconds` (gauge) — time since the last successful refresh
- `view_refresh_duration_seconds` (histogram) — how long each refresh cycle takes
- `view_refresh_failures_total` (counter) — failed refresh attempts
- `view_query_total` (counter) — queries served from the materialized view

### Alerts

- View staleness exceeding the defined freshness SLA
- Refresh duration growing over time (source data volume increasing or query plan degradation)
- Consecutive refresh failures (view becoming progressively stale)
- View query rate dropping to zero (consumers may have switched away or view is broken)


## Testing

Verify every auditable action produces a complete, tamper-evident log entry with correct metadata.

### Unit Tests

- Assert each auditable operation emits a log entry with actor, action, resource, timestamp, and outcome
- Verify sensitive fields are masked or excluded from audit entries
- Test that audit entries are immutable — no update or delete path exists

### Integration Tests

- Perform CRUD operations and query the audit log to verify entries are persisted and queryable
- Test audit log search and filtering by actor, time range, and resource type
- Verify audit entries survive application restart (durable storage)

### Failure Injection

- Simulate audit store unavailability and verify the application fails closed (rejects the operation, not silently drops the log)

## Monitoring

Track audit log ingestion rates, gaps, and storage health.

### Key Metrics

- `audit_events_total` (counter) — events written by action type and outcome
- `audit_write_latency_seconds` (histogram) — time to persist each audit entry
- `audit_lag_seconds` (gauge) — delay between event occurrence and log persistence
- `audit_storage_bytes` (gauge) — audit log storage consumption

### Alerts

- Audit write failures (compliance risk if events are lost)
- Ingestion lag exceeding acceptable window
- Gap in expected periodic events (missing heartbeat entries)


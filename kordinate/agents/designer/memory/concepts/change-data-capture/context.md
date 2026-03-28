## Testing

Verify event emission for all DML operations and ensure consumers handle ordering, duplicates, and schema changes.

### Unit Tests

- Assert insert, update, and delete operations each produce a CDC event with correct before/after state
- Verify event ordering: updates to the same row arrive in commit order
- Test schema evolution: events with added/removed columns are handled by the consumer deserializer

### Integration Tests

- Write to the source database, consume events through the full pipeline, and verify downstream state matches
- Test initial snapshot: start a new connector and verify it captures all existing rows before streaming changes

### Failure Injection

- Kill the connector mid-stream, restart it, and verify no events are lost or duplicated beyond idempotency guarantees

## Monitoring

Track replication lag, connector health, and event throughput from source to consumers.

### Key Metrics

- `cdc_lag_seconds` (gauge) — delay between source commit and event availability to consumers
- `cdc_events_total` (counter) — events captured by table/collection and operation type
- `cdc_connector_status` (gauge) — connector health (0=failed, 1=running, 2=paused)
- `cdc_snapshot_progress` (gauge) — initial snapshot completion percentage

### Alerts

- Replication lag exceeding acceptable threshold
- Connector failure or repeated restart
- Event throughput drop to zero (silent connector failure)

## Deployment

Coordinate connector updates with schema changes and ensure no events are lost during rollout.

### Rollout Implications

- Schema changes on the source database must be backward-compatible with the running connector
- Deploy connector updates during low-traffic windows to minimize replication lag during restart
- Connector restart triggers a catch-up phase — consumers may see a burst of events

### Pre-deploy Checklist

- Verify the connector's stored offset is valid and will resume from the correct position
- Test schema compatibility between the new connector version and current source schema
- Confirm consumer idempotency — duplicate events during catch-up must be handled safely


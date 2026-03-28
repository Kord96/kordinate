## Testing

Verify atomicity of the outbox write, publisher delivery guarantees, and correct cleanup behavior.

### Unit Tests

- Insert a business entity and outbox event in one transaction, then verify both are committed or both rolled back on failure
- Verify the publisher marks events as published after successful broker delivery
- Test idempotent re-publishing: re-running the publisher on already-published events does not produce duplicates on the broker
- Assert unpublished events are fetched in insertion order (FIFO guarantee)

### Integration Tests

- Write an event, run the publisher, and verify the message appears on the broker topic with correct payload and headers
- Simulate broker unavailability: verify events remain in the outbox unpublished and are retried on recovery
- Test the cleanup job: published events older than the retention window are deleted without affecting unpublished events
- Verify CDC-based publishing (if used) picks up new outbox rows within the expected latency window

### Failure Injection

- Kill the publisher mid-batch and verify no events are lost (at-least-once delivery) and the next run resumes correctly
- Simulate a database connection failure during publish and verify the publisher retries without marking events as published

## Monitoring

Track outbox table health and publisher lag to detect delivery stalls before they impact downstream consumers.

### Key Metrics

- `outbox_unpublished_count` (gauge) -- number of rows pending publication (should stay near zero)
- `outbox_publish_latency_seconds` (histogram) -- time from insert to successful broker delivery
- `outbox_publish_errors_total` (counter) -- failed publish attempts by error type (broker unavailable, serialization error)
- `outbox_table_size_rows` (gauge) -- total row count including published rows awaiting cleanup

### Alerts

- Unpublished event count exceeds threshold (publisher stalled or broker unreachable)
- Oldest unpublished event age exceeds SLA (events stuck in outbox beyond acceptable latency)
- Outbox table row count growing unboundedly (cleanup job not running or failing)
- Publisher error rate spike (broker connectivity issue or schema incompatibility)

## Deployment

Coordinate database schema changes and publisher process lifecycle during rollouts.

### Rollout Implications

- Schema migrations adding columns to the outbox table must be backward-compatible (new columns nullable or with defaults)
- The publisher process must be running during and after deployment -- ensure it is not accidentally terminated during rollout
- If using CDC (Debezium), connector configuration must be updated before schema changes that alter the outbox table structure
- Rolling deployments may produce outbox events in both old and new formats -- consumers must handle both during transition

### Pre-deploy Checklist

- Verify the outbox publisher is healthy and the unpublished count is near zero before starting rollout
- Confirm database migration does not lock the outbox table for extended periods (use online DDL where possible)
- Ensure the message broker topic exists and has appropriate retention for the new event types
- Test that new outbox event formats are deserializable by all downstream consumers before deploying the producer


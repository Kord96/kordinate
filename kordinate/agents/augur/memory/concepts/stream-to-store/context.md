## Testing

Validate offset commit ordering, buffer flush boundaries, and data integrity under reprocessing scenarios.

### Unit Tests

- Test buffer flush triggers — verify flush fires at both size threshold and time interval, whichever comes first
- Assert that offset commit only occurs after a successful store write, never before
- Test message deserialization failures — confirm bad records route to dead-letter, not block the pipeline
- Verify buffer correctly batches messages and respects max batch size boundaries

### Integration Tests

- Produce messages to a real broker, consume and flush to a real store, then verify all records landed with no duplicates
- Trigger a consumer group rebalance mid-flush and verify no data is lost or double-written
- Test end-to-end reprocessing by resetting offsets and replaying — assert store state is identical (idempotent writes)

### Failure Injection

- Kill the store mid-flush and verify the consumer retries the batch without advancing offsets
- Simulate broker unavailability during offset commit and verify the consumer re-fetches and re-processes the unflushed batch
- Introduce artificial latency in the store to trigger time-based flush while size-based flush is pending — verify no duplicate flush

## Monitoring

Track consumer lag, buffer health, and store write performance to catch pipeline stalls early.

### Key Metrics

- `consumer_lag_records` (gauge) — records behind head per partition (Kafka consumer lag)
- `buffer_utilization_ratio` (gauge) — current buffer fill level as fraction of max capacity
- `flush_duration_seconds` (histogram) — time to flush buffer contents to the store
- `store_write_errors_total` (counter) — failed store write attempts
- `dead_letter_records_total` (counter) — messages sent to dead-letter queue

### Alerts

- Consumer lag exceeding threshold for a sustained period (pipeline falling behind)
- Buffer utilization above 80% (approaching memory exhaustion)
- Store write error rate spiking (downstream store degraded)
- Dead-letter queue depth growing without resolution

## Deployment

Consumer rebalancing and offset management during rollout can cause duplicates or data loss if not handled correctly.

### Rollout Implications

- Rolling restart triggers consumer group rebalancing — ensure cooperative rebalancing is configured to minimize partition reassignment storms
- In-flight buffers must be flushed and offsets committed before a pod terminates, or data in the buffer is lost
- PVC-backed buffers require volume binding to complete before the consumer starts — account for this in readiness probes
- Scaling consumer replicas changes partition assignments — verify no partition is left unassigned during the transition
- New consumer instances starting with `latest` offset after a rebalance will skip unprocessed messages — always resume from committed offsets

### Pre-deploy Checklist

- Verify terminationGracePeriodSeconds is long enough to flush buffers and commit offsets
- Confirm PVCs are pre-provisioned or dynamic provisioning is fast enough to avoid readiness timeouts
- Check that consumer group rebalancing strategy is set to cooperative (incremental), not eager


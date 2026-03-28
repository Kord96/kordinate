## Testing

Verify that duplicate messages produce the same outcome and the deduplication store behaves correctly.

### Unit Tests

- Process a message, then send the same message ID again and assert no side effects are replayed
- Verify that duplicate detection returns the original result, not an error
- Assert that the dedup check and business logic execute within the same transaction (no partial state)

### Integration Tests

- Send the same message concurrently from multiple producers and verify exactly one processing occurs
- Simulate broker redelivery (ack timeout) and confirm the consumer handles the redelivered message idempotently
- Validate TTL expiry: insert a message ID, wait past TTL, and confirm the entry is cleaned up

### Failure Injection

- Kill the consumer mid-processing and verify the message is retried and processed exactly once after restart
- Corrupt the idempotency store and verify the consumer fails visibly rather than silently reprocessing

## Monitoring

Track deduplication effectiveness and the growth of the processed-ID store.

### Key Metrics

- `messages_deduplicated_total` (counter) — duplicate messages detected and skipped
- `idempotency_store_size` (gauge) — number of entries in the processed-ID table or set
- `idempotency_check_duration_seconds` (histogram) — latency of the dedup lookup
- `idempotency_store_cleanup_total` (counter) — expired entries purged per cleanup cycle

### Alerts

- Deduplication rate spike (upstream producing excessive retries)
- Idempotency store size approaching capacity or TTL cleanup stalled
- Dedup check latency increasing (index degradation or store overload)
- Zero deduplications over an extended period when at-least-once delivery is expected (check broken)

## Deployment

Coordinate deployments with message redelivery behavior to avoid false duplicates or missed dedup.

### Rollout Implications

- During rolling updates, old and new consumer versions may process the same message -- both must write to the same idempotency store
- Schema changes to the idempotency store (inbox table) must be backward-compatible with the running version
- If switching idempotency backends (e.g., in-memory to database), run both in parallel during transition to avoid gaps

### Pre-deploy Checklist

- Verify the idempotency store migration has been applied before deploying the new consumer version
- Confirm TTL cleanup jobs are scheduled and running in the target environment
- Check that the processed-ID store is shared across all consumer replicas, not local to each pod


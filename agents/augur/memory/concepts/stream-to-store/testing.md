---
description: Stream-to-Store — testing guidance
---
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

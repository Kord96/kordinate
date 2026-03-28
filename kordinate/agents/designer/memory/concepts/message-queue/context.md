## Testing

Verify message delivery, acknowledgment semantics, and dead-letter handling under normal and failure conditions.

### Unit Tests

- Produce a message, consume it, and assert the payload matches and the message is acknowledged
- Verify that unacknowledged messages become visible again after the visibility timeout
- Assert that messages exceeding the retry limit are routed to the dead-letter queue

### Integration Tests

- Produce and consume messages through a real broker and verify end-to-end delivery
- Test consumer idempotency: redeliver a message and confirm no duplicate side effects
- Validate message ordering guarantees (FIFO or best-effort) match the queue configuration

### Failure Injection

- Kill a consumer mid-processing (before ack) and verify the message is redelivered to another consumer
- Produce a poison message that always fails processing and verify it lands in the dead-letter queue after retries
- Simulate broker unavailability and verify the producer retries or buffers messages without data loss

## Monitoring

Track queue depth, consumer throughput, and dead-letter activity to detect processing bottlenecks.

### Key Metrics

- `queue_depth` (gauge) — number of messages waiting to be consumed
- `messages_consumed_total` (counter) — messages successfully processed and acknowledged
- `messages_dead_lettered_total` (counter) — messages routed to the dead-letter queue after retry exhaustion
- `message_processing_duration_seconds` (histogram) — time from dequeue to acknowledgment

### Alerts

- Queue depth growing monotonically (consumers not keeping up with producers)
- Dead-letter queue receiving messages (poison messages or persistent processing failures)
- Processing duration exceeding the visibility timeout (risk of duplicate delivery)
- Consumer count dropping to zero (all consumers crashed or disconnected)

## Deployment

Coordinate consumer rollouts with message processing to avoid message loss or duplicate processing.

### Rollout Implications

- Drain in-flight messages before terminating consumer pods (graceful shutdown with ack completion)
- During rolling updates, old and new consumer versions process from the same queue -- message format must be backward-compatible
- Scale consumers based on queue depth, but avoid scaling to zero if message loss is unacceptable
- Dead-letter queue configuration must exist before deploying consumers that rely on it

### Pre-deploy Checklist

- Verify queue and dead-letter queue exist in the target environment before deploying producers or consumers
- Confirm visibility timeout is tuned for the expected processing duration of the new consumer version
- Test that the new consumer version handles messages produced by the old producer version (schema compatibility)
- Ensure consumer graceful shutdown completes pending acks within `terminationGracePeriodSeconds`


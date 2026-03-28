## Testing

Verify messages are processed exactly once across consumers and that work distributes evenly.

### Unit Tests

- Publish N messages with M consumers and assert each message is processed exactly once
- Verify message acknowledgment: unacknowledged messages are redelivered to another consumer
- Test idempotency: redelivered messages do not produce duplicate side effects

### Integration Tests

- Run multiple consumer instances against a real broker and verify even work distribution
- Test consumer group rebalancing: add/remove a consumer mid-stream and verify no messages are lost or duplicated

### Failure Injection

- Kill a consumer mid-processing and verify the message is redelivered to a surviving consumer
- Introduce a poison message and verify it routes to a DLQ after max retries without blocking the queue

## Monitoring

Track queue depth, consumer throughput, and processing distribution across instances.

### Key Metrics

- `queue_depth` (gauge) — pending messages in the queue
- `consumer_messages_processed_total` (counter) — messages processed per consumer instance
- `consumer_processing_latency_seconds` (histogram) — per-message processing time
- `consumer_redeliveries_total` (counter) — messages redelivered after failed processing

### Alerts

- Queue depth growing steadily (consumers not keeping up with producers)
- Consumer instance processing zero messages (stuck or disconnected)
- Redelivery rate exceeding threshold (poison message or systemic failure)

## Deployment

Scale consumers independently of producers and ensure no messages are lost during rolling restarts.

### Rollout Implications

- During rolling restart, in-flight messages on terminating instances must be nacked or completed before shutdown
- Old and new consumer versions may process messages concurrently — ensure message format backward compatibility
- Scaling down reduces parallelism; verify remaining consumers can handle the full message rate

### Pre-deploy Checklist

- Verify consumer shutdown drains in-flight messages within terminationGracePeriodSeconds
- Confirm consumer group rebalancing completes without message loss


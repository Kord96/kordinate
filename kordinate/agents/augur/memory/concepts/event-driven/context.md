## Testing

Verify that events are published, routed, and consumed correctly, with proper handling of ordering, failures, and idempotency.

### Unit Tests

- Assert that domain actions publish the expected event type with the correct payload
- Verify consumers process events idempotently — duplicate delivery should not cause side effects
- Test event deserialization: malformed events should be rejected with a clear error, not silently dropped
- Assert that event handlers do not perform synchronous blocking calls that would stall the consumer

### Integration Tests

- Publish an event and verify the consumer processes it end-to-end, including downstream side effects
- Test event ordering: publish events with causal dependencies and verify consumers process them in the correct order
- Verify that multiple consumers on the same topic each receive and process events independently

### Failure Injection

- Kill a consumer mid-processing and verify the event is redelivered and processed successfully on restart
- Simulate broker unavailability and confirm producers either buffer events or fail with a retryable error

## Monitoring

Track event throughput, consumer lag, and processing errors to maintain visibility into asynchronous workflows.

### Key Metrics

- `events_published_total` (counter) — events emitted by producers, by event type
- `events_consumed_total` (counter) — events successfully processed by consumers
- `consumer_lag` (gauge) — offset difference between latest published and last consumed event
- `event_processing_duration_seconds` (histogram) — time from event receipt to processing completion

### Alerts

- Consumer lag exceeding threshold (consumers falling behind producers)
- Event processing error rate spike (poison messages or downstream failures)
- Zero events published for an expected event type over a time window (producer may be down)

## Deployment

Coordinate producer and consumer deployments to avoid event loss or processing gaps during rollouts.

### Rollout Implications

- Deploy consumers before producers when introducing new event types — consumers must be ready to handle events as soon as they appear
- Rolling consumer updates may cause temporary rebalancing of partitions — expect brief processing pauses during rebalance
- Verify that new consumers can handle events published by the old producer version and vice versa
- If changing event routing (new topics, partition keys), deploy the infrastructure change before the code change

### Pre-deploy Checklist

- Confirm message broker topics/queues exist and have correct partition counts in the target environment
- Verify consumer group offsets are committed and current — stale offsets after deploy could trigger unwanted replay

